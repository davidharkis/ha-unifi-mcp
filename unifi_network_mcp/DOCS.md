# Configuration

Set the controller host (IP/hostname without a URL scheme), HTTPS port and site. Enter a dedicated local UniFi Network read-only account's username and password in this app's HA Configuration tab. Alternatively, an API key supports a narrower set of inventory tools.

Keep `read_only` enabled initially. Turning it off permits upstream mutation tools with preview/confirmation, subject to the controller user's own permissions.

Set `mcp_token` to a randomly generated secret of at least 32 characters. Client requests must send `Authorization: Bearer <token>`. Do not share it or put it in a URL.

`certfile` and `keyfile` refer to existing certificate files in HA's `/ssl` folder. The default names are `fullchain.pem` and `privkey.pem`. The MCP connection URL must use a hostname covered by that certificate, on HTTPS port 9443 with path `/mcp`. Never expose the backend's port 3000. The app publishes only the authenticated HTTPS gateway.

`verify_ssl` controls verification of the UniFi controller's certificate, independently of the gateway TLS certificate. Prefer a trusted controller certificate; a self-signed certificate will fail verification unless explicitly configured otherwise.

HA stores app options in its app data and preserves them across updates. Protect backups because they may include credentials. Make an app backup before updates; restore it from HA if a release fails. Restart the app after renewing/replacing its TLS certificate.

GitHub Actions publishes successful upstream builds. Refresh the HA app store and use Update when a new version is offered. A failed build leaves HA's published version unchanged; inspect the repository's Actions page for the failure.
