import requests
import time

session = requests.Session()
session.headers.update(
    {"User-Agent": "Minecraft-Server-Index/1.0 (+https://github.com/sanmacorz)"}
)

print("Fetching manifests...")
try:
    mojang_resp = session.get(
        "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    )
    mojang_resp.raise_for_status()
    mojang_data = mojang_resp.json()
except requests.RequestException as e:
    raise SystemExit(f"Failed to fetch Mojang version manifest: {e}") from e
except ValueError as e:
    raise SystemExit("Failed to parse Mojang version manifest JSON") from e

markdown_lines = [
    "# Minecraft Ultimate Server Index",
    "Mirrored Official Mojang",
    "",
    "_Generated automatically. Not all versions include official server jars._",
    "",
    "| Version | Type | SHA-1 Hash (Official) | Official Jar |",
    "| :--- | :--- | :--- | :--- |",
]

PLACEHOLDER = "*N/A*"

all_versions = mojang_data["versions"]
total = len(all_versions)

print(f"Processing {total} versions...")

TIMEOUT = 5

for index, version in enumerate(all_versions):
    # Initialize placeholders
    official_link = PLACEHOLDER
    official_hash = PLACEHOLDER
    omni_link = PLACEHOLDER

    # Check Mojang Official Data
    try:
        version_url = version.get("url")
        if not version_url:
            continue

        resp = session.get(version_url, timeout=TIMEOUT)
        resp.raise_for_status()
        v_data = resp.json()

        server_info = v_data.get("downloads", {}).get("server")
        if server_info:
            official_link = f"[Download]({server_info['url']})"
            official_hash = f"`{server_info['sha1']}`"
    except (requests.RequestException, ValueError):
        pass

    # Add row to the list
    markdown_lines.append(
        f"| {version['id']} | {version['type']} | {official_hash} | {official_link} | {omni_link} |"
    )

    print(f"[{index + 1}/{total}] Synced {version['id']} (Official)")  # Progress output
    time.sleep(0.1)  # Small sleep to be polite to the APIs

# Save to file
with open("minecraft-server-index.md", "w") as f:
    f.write("\n".join(markdown_lines))

print("\nDone! Full mirrored index saved to 'minecraft-server-index.md'")
