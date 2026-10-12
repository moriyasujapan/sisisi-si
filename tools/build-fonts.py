#!/usr/bin/env python3
"""index.html に出てくる文字だけに絞った woff2 を fonts/ に生成する。

ページを同一オリジンで完結させるためのもの。Google Fonts を <link> で読むと、
中国本土からは fonts.googleapis.com に届かず、しかも stylesheet はレンダリングを
止めるので白画面になる。フォントを同梱すれば「ページが開けた＝フォントも届いた」
が保証される。

本文（英語の HTML、STRINGS の日本語/中国語、MSG のメッセージ）に新しい文字を
足したら、このスクリプトを流し直すこと。落とし忘れると豆腐になる。

    python3 tools/build-fonts.py

サブセットの生成自体は Google Fonts の text= パラメータに任せている（ローカルに
fontTools を入れる必要がない）。生成物は OFL 1.1 で再配布が許諾されている。
"""

import html as H
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
OUT = ROOT / "fonts"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")


def is_cjk(ch):
    o = ord(ch)
    return (0x3000 <= o <= 0x30FF or 0x3400 <= o <= 0x4DBF
            or 0x4E00 <= o <= 0x9FFF or 0xFF00 <= o <= 0xFFEF)


def charsets(src):
    """ページから、言語ごとに実際に使われている文字を集める。"""
    body = re.sub(r"<style>.*?</style>", "", src, flags=re.S)
    body = re.sub(r"<script>.*?</script>", "", body, flags=re.S)
    en = H.unescape(re.sub(r"<[^>]+>", " ", body))

    def quoted(block):
        return " ".join(re.findall(r':\s*"((?:[^"\\]|\\.)*)"', block))

    def lang_block(name):
        m = re.search(name + r":\s*\{(.*?)\n    \}", src, re.S)
        return quoted(m.group(1)) if m else ""

    ja, zh = lang_block("ja"), lang_block("zh")

    msg = re.search(r"var MSG = \{(.*?)\n  \};", src, re.S)
    if msg:
        for name in ("ja", "zh"):
            m = re.search(name + r":\s*\{(.*?)\}", msg.group(1), re.S)
            if m:
                if name == "ja":
                    ja += " " + quoted(m.group(1))
                else:
                    zh += " " + quoted(m.group(1))

    latin = {c for c in en + ja + zh
             if not is_cjk(c) and c.isprintable() and not c.isspace()}
    return {
        "latin": "".join(sorted(latin)),
        "ja": "".join(sorted({c for c in ja if is_cjk(c)})),
        "zh": "".join(sorted({c for c in zh if is_cjk(c)})),
    }


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read()


def build(family, weight, text, name):
    query = urllib.parse.urlencode(
        {"family": f"{family}:wght@{weight}", "text": text, "display": "swap"})
    css = fetch("https://fonts.googleapis.com/css2?" + query).decode("utf-8")
    m = re.search(r"url\((https://[^)]+)\)\s*format\('woff2'\)", css)
    if not m:
        sys.exit(f"{name}: woff2 の URL が取れなかった")
    data = fetch(m.group(1))
    if data[:4] != b"wOF2":
        sys.exit(f"{name}: woff2 ではないデータが返ってきた")
    (OUT / f"{name}.woff2").write_bytes(data)
    return len(data)


def main():
    cs = charsets(PAGE.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    (OUT / "charsets.json").write_text(
        json.dumps(cs, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"欧文・記号 {len(cs['latin'])} / 日本語 {len(cs['ja'])} / 中国語 {len(cs['zh'])} 文字")

    jobs = [
        ("IBM Plex Mono", 400, cs["latin"], "plexmono-400"),
        ("IBM Plex Mono", 600, cs["latin"], "plexmono-600"),
        ("IBM Plex Sans", 400, cs["latin"], "plexsans-400"),
        ("IBM Plex Sans", 500, cs["latin"], "plexsans-500"),
        ("Noto Sans JP", 400, cs["latin"] + cs["ja"], "notojp-400"),
        ("Noto Sans JP", 500, cs["latin"] + cs["ja"], "notojp-500"),
        ("Noto Sans SC", 400, cs["latin"] + cs["zh"], "notosc-400"),
        ("Noto Sans SC", 500, cs["latin"] + cs["zh"], "notosc-500"),
    ]

    total = 0
    for family, weight, text, name in jobs:
        size = build(family, weight, text, name)
        total += size
        print(f"  {name:14} {size / 1024:6.1f} KB")
    print(f"合計 {total / 1024:.1f} KB")


if __name__ == "__main__":
    main()
