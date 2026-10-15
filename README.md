# UniFi Network MCP for Home Assistant OS

Connect MCP-compatible AI assistants to your UniFi Network controller through a Home Assistant app. Powered by [UniFi MCP](https://github.com/sirkirby/unifi-mcp) by Chris Kirby.

**Development:** [AI-assisted](#ai-assisted-development).

## Requirements

- Home Assistant OS running on amd64 (x86-64) hardware.
- A UniFi Network controller and a dedicated local account with read-only permissions.
- A TLS certificate and private key for the hostname your MCP client will connect to.
- An AI assistant or other MCP client that supports Streamable HTTP and bearer authentication.

## Installation

1. On an amd64 HAOS host, open **Settings → Apps** (called **Add-ons** on older versions), then the app store.
2. Open the store's menu → **Repositories** and add `https://github.com/davidharkis/ha-unifi-mcp`.
3. Install **UniFi Network MCP**.
4. Put a TLS certificate and its private key in HA's `/ssl` folder. Defaults are `fullchain.pem` and `privkey.pem`. Use a certificate trusted by your MCP client and covering the hostname you will connect to.
5. In the app's Configuration tab, set the controller host, credentials, certificate filenames, and a randomly generated `mcp_token` of at least 32 characters. Keep `read_only: true` and use a dedicated read-only controller account.
6. Start the app. Configure a Streamable HTTP MCP client with URL `https://<certificate-hostname>:9443/mcp` and header `Authorization: Bearer <mcp_token>`.

See [configuration documentation](unifi_network_mcp/DOCS.md) for controller TLS, API keys, and backups. Keep the endpoint on a trusted network; no public internet exposure is required.

## Updates

Refresh the Home Assistant app store and select **Update** when a new version is available. Create an app backup before updating so you can restore it if needed. Your app settings are preserved across updates.

See the [changelog](unifi_network_mcp/CHANGELOG.md) for release details.

## AI-assisted development

This Home Assistant wrapper is developed and maintained with assistance from AI tools, including help with code, documentation, and review. Please report problems through [GitHub Issues](https://github.com/davidharkis/ha-unifi-mcp/issues).

## License

The Home Assistant wrapper is [MIT licensed](LICENSE). UniFi MCP is copyright Chris Kirby and distributed under its [MIT license](https://github.com/sirkirby/unifi-mcp/blob/main/LICENSE). Dependencies retain their own licenses.
