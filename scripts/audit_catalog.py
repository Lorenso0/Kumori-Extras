#!/usr/bin/env python3
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "Lorenso0/Kumori-Extras")


def asset_url(asset: dict) -> str:
    return (
        f"https://github.com/{REPOSITORY}/releases/download/"
        f"{asset['releaseTag']}/{asset['assetName']}"
    )


def verify(asset: dict, download: bool) -> None:
    request = urllib.request.Request(
        asset_url(asset),
        method="GET" if download else "HEAD",
        headers={"User-Agent": "Kumori-Extras-integrity"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status >= 400:
            raise RuntimeError(f"{response.status}: {asset_url(asset)}")
        if not download:
            return
        digest = hashlib.sha256()
        size = 0
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
        if size != asset["downloadBytes"]:
            raise RuntimeError(f"size mismatch: {asset['assetName']}")
        if digest.hexdigest() != asset["sha256"]:
            raise RuntimeError(f"SHA-256 mismatch: {asset['assetName']}")


def main() -> None:
    download = "--download" in sys.argv
    catalog = json.loads((ROOT / "catalog-v1.json").read_text(encoding="utf-8"))
    count = 0
    for pack in catalog["packs"]:
        verify(pack["package"], download)
        count += 1
        if pack.get("preview"):
            verify(pack["preview"], download)
            count += 1
    print(f"verified {count} public assets ({'full hashes' if download else 'availability'})")


if __name__ == "__main__":
    main()
