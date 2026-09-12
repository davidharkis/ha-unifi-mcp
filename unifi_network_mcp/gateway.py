"""Supervise the loopback MCP server and expose a TLS, bearer-authenticated proxy."""
import asyncio
import hmac
import json
import os
from pathlib import Path
import signal
import ssl

from aiohttp import ClientSession, ClientTimeout, web

CLIENT = web.AppKey("client", ClientSession)

HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
               "te", "trailer", "transfer-encoding", "upgrade", "host", "content-length"}


def child_environment(options):
    env = os.environ.copy()
    # Avoid inherited policy overrides defeating the UI's read-only setting.
    for name in list(env):
        if name.startswith(("UNIFI_", "CONFIG_PATH")):
            del env[name]
    mapping = {"controller_host": "HOST", "controller_port": "PORT", "site": "SITE",
               "username": "USERNAME", "password": "PASSWORD", "api_key": "API_KEY",
               "verify_ssl": "VERIFY_SSL"}
    for key, suffix in mapping.items():
        value = options.get(key, "")
        env[f"UNIFI_NETWORK_{suffix}"] = str(value).lower() if isinstance(value, bool) else str(value)
    env.update(UNIFI_MCP_HTTP_ENABLED="true", UNIFI_MCP_HTTP_FORCE="true",
               UNIFI_MCP_HTTP_TRANSPORT="streamable-http", UNIFI_MCP_HOST="127.0.0.1",
               UNIFI_MCP_PORT="3000", UNIFI_MCP_ALLOWED_HOSTS="127.0.0.1,127.0.0.1:3000",
               UNIFI_MCP_ENABLE_DNS_REBINDING_PROTECTION="true",
               UNIFI_NETWORK_TOOL_PERMISSION_MODE="confirm", UNIFI_TOOL_REGISTRATION_MODE="lazy",
               UNIFI_NETWORK_REDACT_SENSITIVE_FIELDS="true")
    for action in ("CREATE", "UPDATE", "DELETE"):
        env[f"UNIFI_POLICY_NETWORK_{action}"] = "false" if options.get("read_only", True) else "true"
    return env


def make_app(token, backend="http://127.0.0.1:3000"):
    app = web.Application(client_max_size=4 * 1024 * 1024)

    async def session_context(app):
        app[CLIENT] = ClientSession(timeout=ClientTimeout(total=None, sock_connect=10),
                                      auto_decompress=False, trust_env=False)
        yield
        await app[CLIENT].close()

    async def proxy(request):
        supplied = request.headers.get("Authorization", "")
        if not hmac.compare_digest(supplied.encode(), f"Bearer {token}".encode()):
            return web.Response(status=401, headers={"WWW-Authenticate": "Bearer"})
        if request.path not in ("/mcp", "/mcp/"):
            return web.Response(status=404)
        headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in HOP_HEADERS | {"authorization", "origin", "cookie"}}
        try:
            async with app[CLIENT].request(request.method, backend + request.path,
                                             params=request.query, headers=headers,
                                             data=await request.read(), allow_redirects=False) as upstream:
                response = web.StreamResponse(status=upstream.status,
                    headers={k: v for k, v in upstream.headers.items()
                             if k.lower() not in HOP_HEADERS | {"set-cookie"}})
                await response.prepare(request)
                async for chunk in upstream.content.iter_any():
                    await response.write(chunk)
                await response.write_eof()
                return response
        except (OSError, asyncio.TimeoutError):
            return web.Response(status=502, text="MCP backend unavailable")

    app.cleanup_ctx.append(session_context)
    app.router.add_route("*", "/{path:.*}", proxy)
    return app


async def main():
    options = json.loads(Path("/data/options.json").read_text())
    token = options.get("mcp_token", "")
    if len(token) < 32 or any(c.isspace() for c in token):
        raise ValueError("Set mcp_token to at least 32 characters without whitespace in HA app configuration")
    if not options.get("controller_host"):
        raise ValueError("Set controller_host in HA app configuration")
    if not options.get("api_key") and not (options.get("username") and options.get("password")):
        raise ValueError("Configure a controller API key or username and password")
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    cert, key = (Path("/ssl") / options[x] for x in ("certfile", "keyfile"))
    for path in (cert, key):
        if not path.resolve().is_relative_to(Path("/ssl")):
            raise ValueError("Certificate paths must stay inside /ssl")
    context.load_cert_chain(cert, key)
    child = await asyncio.create_subprocess_exec("unifi-network-mcp", env=child_environment(options))
    runner = web.AppRunner(make_app(token), access_log=None)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    wait_child = asyncio.create_task(child.wait())
    wait_stop = asyncio.create_task(stop.wait())
    try:
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", 9443, ssl_context=context).start()
        print("UniFi MCP HTTPS gateway listening on port 9443; path /mcp; bearer token required", flush=True)
        await asyncio.wait((wait_child, wait_stop), return_when=asyncio.FIRST_COMPLETED)
        if wait_child.done() and not stop.is_set():
            raise RuntimeError("UniFi MCP server exited")
    finally:
        wait_stop.cancel()
        await runner.cleanup()
        if child.returncode is None:
            child.terminate()
            try:
                await asyncio.wait_for(wait_child, 10)
            except asyncio.TimeoutError:
                child.kill()
                await child.wait()


if __name__ == "__main__":
    asyncio.run(main())
