# 同梱フォント

| ファイル | 書体 | ライセンス |
|---|---|---|
| `plexmono-400.woff2` / `plexmono-600.woff2` | IBM Plex Mono | SIL OFL 1.1 — © IBM Corp. |
| `plexsans-400.woff2` / `plexsans-500.woff2` | IBM Plex Sans | SIL OFL 1.1 — © IBM Corp. |
| `notojp-400.woff2` / `notojp-500.woff2` | Noto Sans JP | SIL OFL 1.1 — © Google / Adobe |
| `notosc-400.woff2` / `notosc-500.woff2` | Noto Sans SC | SIL OFL 1.1 — © Google / Adobe |

ライセンス全文は `OFL.txt`。いずれも再配布・ウェブ埋め込みが許諾されている。

**これらは `index.html` に出てくる文字だけに絞ったサブセット。**
`charsets.json` が、生成時に含めた文字の一覧。本文（英語の HTML・`STRINGS` の
日本語/中国語・`MSG` のメッセージ）に**新しい文字を足したら、豆腐になるので再生成が要る**。

再生成:

```bash
cd <このリポジトリ>
python3 tools/build-fonts.py
```
