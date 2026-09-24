#!/usr/bin/env python3
"""Fetch the latest post text from the public Struggle Telegram channel page
and store it in channel.json (next to this repo root). No bot token needed:
t.me exposes the newest post in the page's og:description meta tag."""

import datetime
import html
import json
import os
import re
import urllib.request

CHANNEL = "Playlist_mp"
PAGE_URL = f"https://t.me/{CHANNEL}"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "channel.json")

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def fetch_latest():
    req = urllib.request.Request(PAGE_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        page = resp.read().decode("utf-8", "ignore")
    m = re.search(r'<meta property="og:description" content="(.*?)">', page, re.S)
    if not m:
        return None
    text = html.unescape(m.group(1))
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text or None


def main():
    text = fetch_latest()
    if not text:
        print("Could not read latest post; keeping existing channel.json")
        return

    data = {
        "channel": CHANNEL,
        "title": "Struggle",
        "url": f"https://t.me/{CHANNEL}",
        "text": text,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    old_text = None
    if os.path.exists(OUT_PATH):
        try:
            old_text = json.load(open(OUT_PATH, encoding="utf-8")).get("text")
        except Exception:
            pass

    if old_text == text:
        print("No change in latest post.")
        return

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Updated channel.json with new post:", text[:80])


if __name__ == "__main__":
    main()
