# UniFi Network MCP for Home Assistant OS

Home Assistant app for amd64 hardware, using [UniFi MCP](https://github.com/sirkirby/unifi-mcp) by Chris Kirby.

## Status

Experimental. Automated gateway tests, Linux container builds, dependency checks, and GHCR publication pass. The maintainer has tested installation on HAOS and use with a live UniFi controller.

## Installation

Public installation requires both this repository and the GHCR package `ghcr.io/davidharkis/ha-unifi-network-mcp` to be public; their visibility is configured separately.

1. On an amd64 HAOS host, open **Settings → Apps** (called **Add-ons** on older versions), then the app store.
2. Open the store's menu → **Repositories** and add `https://github.com/davidharkis/ha-unifi-mcp`.
3. Install **UniFi Network MCP**.
4. Put a TLS certificate and its private key in HA's `/ssl` folder. Defaults are `fullchain.pem` and `privkey.pem`. Use a certificate trusted by your MCP client and covering the hostname you will connect to.
5. In the app's Configuration tab, set the controller host, credentials, certificate filenames, and a randomly generated `mcp_token` of at least 32 characters. Keep `read_only: true` and use a dedicated read-only controller account.
6. Start the app. Configure a Streamable HTTP MCP client with URL `https://<certificate-hostname>:9443/mcp` and header `Authorization: Bearer <mcp_token>`.

See [configuration documentation](unifi_network_mcp/DOCS.md) for controller TLS, API keys, and backups. Keep the endpoint on a trusted network; no public internet exposure is required.

## Updates

GitHub Actions checks PyPI daily for stable, non-yanked upstream releases. It runs gateway tests, builds the container, checks dependencies/imports, pushes the versioned image, and only then commits the HA version metadata. Refresh the HA app store and use its Update action.

Wrapper-only changes must increment the suffix in `config.yaml` (e.g. `0.37.0-2`). Do not overwrite a released version. The upstream version is pinned; transitive dependencies resolve at build time. Build checks do not prove compatibility with a live controller.

## License

The Home Assistant wrapper is [MIT licensed](LICENSE). UniFi MCP is copyright Chris Kirby and distributed under its [MIT license](https://github.com/sirkirby/unifi-mcp/blob/main/LICENSE). Dependencies retain their own licenses.
