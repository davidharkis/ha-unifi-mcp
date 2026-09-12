import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

spec = importlib.util.spec_from_file_location("gateway", Path(__file__).resolve().parents[1] / "unifi_network_mcp/gateway.py")
gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gateway)


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.calls = []

        async def upstream(request):
            self.calls.append((request.headers, await request.read()))
            return web.Response(body=b'event: message\ndata: {"ok":true}\n\n',
                headers={"Content-Type": "text/event-stream", "Mcp-Session-Id": "test-session"})

        app = web.Application()
        app.router.add_route("*", "/mcp", upstream)
        self.backend = TestServer(app)
        await self.backend.start_server()
        self.client = TestClient(TestServer(gateway.make_app("x" * 40, str(self.backend.make_url("")))))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        await self.backend.close()

    async def test_unauthenticated_request_never_reaches_backend(self):
        for header in (None, "Bearer wrong", "Basic abc"):
            r = await self.client.post("/mcp", headers={"Authorization": header} if header else {})
            self.assertEqual(r.status, 401)
        self.assertEqual(self.calls, [])

    async def test_authenticated_mcp_preserves_body_session_and_stream(self):
        r = await self.client.post("/mcp", data=b'{"method":"initialize"}',
            headers={"Authorization": "Bearer " + "x" * 40, "Mcp-Session-Id": "incoming"})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.headers["Mcp-Session-Id"], "test-session")
        self.assertIn(b"event: message", await r.read())
        headers, body = self.calls[0]
        self.assertNotIn("Authorization", headers)
        self.assertEqual(headers["Mcp-Session-Id"], "incoming")
        self.assertEqual(body, b'{"method":"initialize"}')

    async def test_other_paths_not_forwarded(self):
        r = await self.client.get("/admin", headers={"Authorization": "Bearer " + "x" * 40})
        self.assertEqual(r.status, 404)
        self.assertEqual(self.calls, [])


class PolicyTests(unittest.TestCase):
    def test_read_only_cannot_be_overridden_by_inherited_environment(self):
        with patch.dict("os.environ", {"UNIFI_POLICY_NETWORK_DEVICES_UPDATE": "true"}):
            env = gateway.child_environment({"read_only": True, "verify_ssl": True})
        self.assertNotIn("UNIFI_POLICY_NETWORK_DEVICES_UPDATE", env)
        for action in ("CREATE", "UPDATE", "DELETE"):
            self.assertEqual(env[f"UNIFI_POLICY_NETWORK_{action}"], "false")
        self.assertEqual(env["UNIFI_MCP_HOST"], "127.0.0.1")
        self.assertEqual(env["UNIFI_NETWORK_VERIFY_SSL"], "true")

    def test_writes_still_require_confirmation(self):
        env = gateway.child_environment({"read_only": False})
        self.assertEqual(env["UNIFI_NETWORK_TOOL_PERMISSION_MODE"], "confirm")


if __name__ == "__main__":
    unittest.main()
