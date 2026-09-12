"""Prepare metadata for the latest stable PyPI version; never publish by itself."""
import json
import os
from pathlib import Path
import urllib.request
from packaging.version import Version
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    config_path = ROOT / "unifi_network_mcp/config.yaml"
    config = yaml.safe_load(config_path.read_text())
    current = (ROOT / "unifi_network_mcp/requirements.txt").read_text().strip().split("==")[1]
    with urllib.request.urlopen("https://pypi.org/pypi/unifi-network-mcp/json", timeout=30) as response:
        data = json.load(response)
    stable = [Version(v) for v, files in data["releases"].items()
              if files and not Version(v).is_prerelease and not Version(v).is_devrelease
              and any(not f.get("yanked", False) for f in files)]
    latest = str(max(stable))
    changed = Version(latest) > Version(current)
    if changed:
        config["version"] = latest + "-1"
        config_path.write_text(yaml.safe_dump(config, sort_keys=False))
        (ROOT / "unifi_network_mcp/requirements.txt").write_text(f"unifi-network-mcp=={latest}\n")
        changelog = ROOT / "unifi_network_mcp/CHANGELOG.md"
        changelog.write_text(f"## {config['version']}\n\n- Update UniFi Network MCP to {latest}.\n\n" + changelog.read_text())
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as f:
            f.write(f"version={config['version']}\nchanged={str(changed).lower()}\n")
    print(f"App version: {config['version']}; upstream update: {changed}")


if __name__ == "__main__":
    main()
