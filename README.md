# UniFi Network MCP for Home Assistant OS

Connect MCP-compatible AI assistants to your UniFi Network controller through a Home Assistant app. Powered by [UniFi MCP](https://github.com/sirkirby/unifi-mcp) by Chris Kirby.

**Development:** [AI-assisted](#ai-assisted-development).

## Prerequisites

- Home Assistant OS running on amd64 (x86-64) hardware.
- A UniFi Network controller and a dedicated local account with read-only permissions.
- A TLS certificate and matching private key already available in Home Assistant's `/ssl` folder (defaults: `fullchain.pem` and `privkey.pem`). The certificate must be trusted by your MCP client and cover the hostname it will use. That hostname must resolve to your HAOS host from the client.
- An AI assistant or other MCP client that supports Streamable HTTP and bearer authentication.

### If you do not already have TLS certificates

Complete this before installing the app. Follow the official [Let's Encrypt app documentation](https://github.com/home-assistant/addons/blob/master/letsencrypt/DOCS.md) to obtain a certificate and private key in `/ssl`. Its DNS challenge option supports issuing certificates without opening a port to Home Assistant. You will need a domain and a supported DNS provider.

If suitable certificate files are already in `/ssl`, skip this setup and use their filenames when configuring the app. The UniFi Network MCP app does not generate certificates.

## Installation

1. On an amd64 HAOS host, open **Settings → Apps** (called **Add-ons** on older versions), then the app store.
2. Open the store's menu → **Repositories** and add `https://github.com/davidharkis/ha-unifi-mcp`.
3. Install **UniFi Network MCP**.
4. In the app's Configuration tab, set the controller host, credentials, certificate filenames, and a randomly generated `mcp_token` of at least 32 characters. Keep `read_only: true` and use a dedicated read-only controller account.
5. Start the app. Configure a Streamable HTTP MCP client with URL `https://<certificate-hostname>:9443/mcp` and header `Authorization: Bearer <mcp_token>`.

See [configuration documentation](unifi_network_mcp/DOCS.md) for controller TLS, API keys, and backups. Keep the endpoint on a trusted network; no public internet exposure is required.

## Updates

Refresh the Home Assistant app store and select **Update** when a new version is available. Create an app backup before updating so you can restore it if needed. Your app settings are preserved across updates.

See the [changelog](unifi_network_mcp/CHANGELOG.md) for release details.

## AI-assisted development

This Home Assistant wrapper is developed and maintained with assistance from AI tools, including help with code, documentation, and review. Please report problems through [GitHub Issues](https://github.com/davidharkis/ha-unifi-mcp/issues).

## License

The Home Assistant wrapper is [MIT licensed](LICENSE). UniFi MCP is copyright Chris Kirby and distributed under its [MIT license](https://github.com/sirkirby/unifi-mcp/blob/main/LICENSE). Dependencies retain their own licenses.
