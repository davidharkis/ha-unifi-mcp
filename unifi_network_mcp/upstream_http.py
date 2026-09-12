"""Run UniFi Network MCP in its container HTTP-only mode.

The upstream transport selects HTTP-only mode when it is PID 1. In this HA app
the TLS gateway is PID 1 and supervises the upstream process, so present that
same container-mode signal to the upstream lifecycle code.
"""
import unifi_mcp_shared.transport as transport


transport.os.getpid = lambda: 1

from unifi_network_mcp.main import main  # noqa: E402


if __name__ == "__main__":
    main()
