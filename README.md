# sisisi.si — 売却ランディングページ

`sisisi.si` を GitHub Pages で配るための静的ページ。日本語・英語・中国語（簡体字）の3言語で、
言語切り替えはページ内のボタンで行う。メールアドレスはページに一切出さず、問い合わせは
外部フォームサービス経由で受ける。

```
index.html   ページ本体（CSS・JS 内包、外部依存は Google Fonts のみ）
CNAME        GitHub Pages のカスタムドメイン設定
README.md    このファイル
```

## 公開までの手順

### 1. 連絡先と決済の確認

問い合わせ先は **`ko@12.gy`**（Google Workspace）。ページには
`mailto:` リンクとして直接書いてあり、フォームもバックエンドも使っていない。
変更するときは `index.html` の `a.cta` の `href` と表示テキストの2箇所を直す。

> 2026-10-12: 当初 `sisisi@12.gy` にしていたが受信を確認できず、実在する `ko@12.gy` に変更した。
> 新しいアドレスにする場合は、**先に実際にテスト送信して届くことを確認してから**ページに載せること。

決済と移管は **Efty Pay**（`pay.efty.com`、手数料5%）を使う前提で文面を書いてある。
Efty Pay は**オファーフォームではなく決済・移管の代行**なので、流れはこうなる。

1. 買主からメールが来る（またはこちらからアウトバウンドで当たる）
2. メールで価格を合意する
3. `pay.efty.com` にリードを登録（ドメイン・合意金額・通貨・買主情報）
4. Efty が買主へ決済リンクを送り、入金後に移管まで代行、翌営業日に支払い

初回は KYC/KYB の本人確認が要るので、**買主が現れてから慌てないよう事前に済ませておく**とよい。
Escrow.com（1.9〜2.4%）に変えるなら、`cta_note` の文面を3言語分直すこと。

### 2. リポジトリに置いて Pages を有効化

```bash
cd /home/build/sisisi-si-sale
git init
git add .
git commit -m "feat: sisisi.si 売却ランディングページ"
git branch -M main
gh repo create sisisi-si --public --source=. --push
```

GitHub の Settings → Pages で **Source: Deploy from a branch**、Branch を `main` / `/ (root)`
に設定する。`CNAME` が入っているので、カスタムドメインは自動で `sisisi.si` が入る。

### 3. DNS を GitHub Pages に向ける

**現状の `sisisi.si` はこのサーバー（`5.104.86.3`）を指しているので、切り替えると
アプリと公開APIが止まる。** 先に以下を確認すること。

- 事務所 KeyStone の日次取込（毎日 05:00 に `/v1/gift-logs` を叩く）が `livit17.net` に
  移行済みであること。確認方法:
  `sudo grep -E "/v1/gift-logs" /var/log/nginx/livit17.net_access.log`
- 旧ドメインを使っている利用者がいなくなっていること。

切り替える DNS レコード（Cloudflare、**プロキシは灰色＝DNS only にする**。
GitHub Pages が自前で証明書を発行するため、橙のままだと証明書の取得に失敗する）:

| Type | Name | Value |
|---|---|---|
| A | `sisisi.si` | `185.199.108.153` |
| A | `sisisi.si` | `185.199.109.153` |
| A | `sisisi.si` | `185.199.110.153` |
| A | `sisisi.si` | `185.199.111.153` |
| CNAME | `www` | `<ユーザー名>.github.io` |

既存の `*.sisisi.si` ワイルドカードと `auth` / `analytics` / `gifts` / `mariadb` /
`queue` / `sso` / `test` / `beaver` / `cacti` / `code` の A レコードは、
不要なら合わせて削除する（nginx 側の vhost は 2026-10-12 に無効化済み）。

GitHub 側で証明書が発行されたら Settings → Pages で **Enforce HTTPS** を有効にする。

## 中身について

- **外部依存は Google Fonts だけ。** CSS と JS は `index.html` に内包。画像もスクリプトも
  追加で読み込まない。
- **CJK も Web フォント（Noto Sans JP / Noto Sans SC）で固定している。** 端末任せにすると
  ヒラギノ・游ゴシック・YaHei で字面がバラつくため。Google Fonts の CJK は unicode-range で
  細かく分割配信されるので、実際にページに出てくる文字のサブセットしか落ちてこない。
- **日本語と中国語でフォントを入れ替えている。** 同じ漢字でも簡体字と日本語で字形が違うため、
  `html[lang]` に応じて `--cjk` トークンを差し替えている（言語切り替え時に `lang` を書き換え）。
- Noto の後ろに端末フォントを残してある。**中国本土からは `fonts.googleapis.com` が
  届かないことが多い**ので、その場合は端末のフォントで表示される。
- **英語が HTML に直接書かれている。** JavaScript が動かない環境でも英語で読める。
  日本語・中国語はスクリプト内のテーブルから差し替える。
- 初回表示の言語はブラウザの設定（`navigator.language`）から判定し、一度選んだ言語は
  `localStorage` に覆える。プライベートブラウズでも落ちないよう try/catch してある。
- ライト／ダーク両対応。OS 設定に追従し、色はすべて `:root` のトークン経由。
- 価格は金額を出さず「ご相談ください / Make an offer / 欢迎出价」。金額を出す場合は
  `rec_price_v` を3言語分書き換える。
- **問い合わせは Sedo に委ねているので、サーバー側の受信処理もメールアドレスの記載も無い。**
  ページは完全な静的ファイルで、JavaScript は言語切り替えだけに使っている。
- フッターに「ここにあった分析ダッシュボードは livit17.net に移転しました」という
  一文を入れている。旧ドメインのブックマークが残っているため。不要なら
  `.former` の段落と `former` キーを消す。

## 載せていないこと

ドメインの登録日・レジストラは、`.si` の whois / RDAP から取得できなかったため
記載していない（推測で書くのを避けた）。載せるなら `.record` の `<dl>` に行を足す。
