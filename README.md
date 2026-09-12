# UniFi Network MCP for Home Assistant OS

Private Home Assistant app repository for amd64 hardware. Upstream: https://github.com/sirkirby/unifi-mcp

## Status

Package prepared locally. Publication, image build on Linux, HA installation, and live controller testing are not yet complete.

## Updates

GitHub Actions checks PyPI daily for stable, non-yanked upstream releases. When there is a new version it runs gateway tests, builds the container, checks dependencies/imports, pushes the versioned image, and only then commits the HA version metadata. Home Assistant can subsequently offer its usual Update action. Installation remains manual in HA.

Wrapper-only changes must increment the suffix in `config.yaml` (e.g. `0.32.6-2`). Do not overwrite a released version. Builds use a pinned UniFi MCP version; transitive dependencies currently resolve at build time, and the resulting image is reused by HA. Build checks do not prove compatibility with your live UniFi controller.

## Private distribution

Keep the GitHub repository and GHCR package private. HA requires read access to both. Private repository authentication must be verified against Supervisor before installation; do not paste tokens into issues, logs, or this repository. GHCR needs a read-packages credential configured in Supervisor. The GitHub connector alone does not supply HA's credentials.

If private repository authentication cannot be configured reliably, stop and resolve distribution with the owner; do not make the repository public as a workaround.

## Cost

Uses standard Linux runners, a 25-minute job limit, one daily release check, no uploaded build artifacts and no paid larger runners. GitHub Free's private Actions allowance is shared with other repositories. Set a stop-usage budget in GitHub billing. GHCR is currently free under GitHub's published policy.

See [app documentation](unifi_network_mcp/DOCS.md) for configuration.
