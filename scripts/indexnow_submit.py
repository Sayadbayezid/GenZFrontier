#!/usr/bin/env python3
"""Submit sitemap URL changes to IndexNow."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "www.genzfrontir.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_PATTERN = re.compile(r"^[A-Za-z0-9-]{8,128}$")
BATCH_SIZE = 10_000


def parse_urls(xml_text: str) -> dict[str, str]:
    root = ET.fromstring(xml_text)
    result: dict[str, str] = {}
    for url_node in root.iter():
        if not url_node.tag.endswith("url"):
            continue
        loc = next((child.text.strip() for child in url_node if child.tag.endswith("loc") and child.text), None)
        lastmod = next((child.text.strip() for child in url_node if child.tag.endswith("lastmod") and child.text), "")
        if loc:
            result[loc] = lastmod
    return result


def load_previous_sitemap() -> str | None:
    try:
        return subprocess.check_output(["git", "show", "HEAD:sitemap.xml"], text=True)
    except (subprocess.CalledProcessError, OSError):
        return None


def find_key(repo_root: Path) -> tuple[str, Path]:
    candidates = []
    for path in repo_root.glob("*.txt"):
        key = path.stem
        if KEY_PATTERN.fullmatch(key) and path.read_text(encoding="utf-8").strip() == key:
            candidates.append((key, path))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one valid IndexNow key file at repository root; found {len(candidates)}")
    return candidates[0]


def submit(urls: list[str], key: str) -> None:
    key_location = f"https://{HOST}/{key}.txt"
    for start in range(0, len(urls), BATCH_SIZE):
        batch = urls[start : start + BATCH_SIZE]
        body = (
            '{"host":' + _json_string(HOST) +
            ',"key":' + _json_string(key) +
            ',"keyLocation":' + _json_string(key_location) +
            ',"urlList":[' + ",".join(_json_string(url) for url in batch) + "]}"
        ).encode("utf-8")
        request = urllib.request.Request(
            ENDPOINT,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                status = response.status
                response_body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            response_body = error.read().decode("utf-8", errors="replace")
            print(f"IndexNow batch {start}:{start + len(batch)} failed: HTTP {error.code} {response_body[:500]}", file=sys.stderr)
            raise
        print(f"IndexNow batch {start}:{start + len(batch)}: HTTP {status} {response_body[:500]!r}")
        if status not in (200, 202):
            raise RuntimeError(f"IndexNow returned unexpected HTTP status {status}")


def _json_string(value: str) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sitemap", default="sitemap.xml")
    parser.add_argument("--previous-sitemap", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sitemap_path = Path(args.sitemap)
    current_text = sitemap_path.read_text(encoding="utf-8")
    current = parse_urls(current_text)
    if args.previous_sitemap:
        previous_path = Path(args.previous_sitemap)
        previous_text = previous_path.read_text(encoding="utf-8") if previous_path.exists() else ""
    else:
        previous_text = load_previous_sitemap()
    previous = parse_urls(previous_text) if previous_text else {}
    changed = sorted(
        set(current) | set(previous),
        key=lambda url: url,
    )
    changed = [url for url in changed if current.get(url) != previous.get(url)]
    changed = [url for url in changed if url.startswith(f"https://{HOST}/")]
    print(f"Current sitemap URLs: {len(current)}")
    print(f"URLs changed since HEAD: {len(changed)}")
    if not changed:
        print("No IndexNow submission needed.")
        return 0
    repo_root = sitemap_path.resolve().parent
    key, key_path = find_key(repo_root)
    print(f"Using key file: {key_path.name}")
    if args.dry_run:
        for url in changed:
            print(f"DRY_RUN_URL={url}")
        return 0
    submit(changed, key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
