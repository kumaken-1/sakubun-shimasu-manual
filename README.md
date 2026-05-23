# 学校マネジメント相談カード作成アプリ

Gem「学校マネジメント相談室」に貼り付ける相談文を整える、APIなしの静的Webアプリです。

GitHub Pagesでアプリをそのまま使えるように、ルートの `index.html` に配置しています。

## GitHub Pages公開アドレス

マニュアルは上書きを避けるため、次の専用URLで分けて公開します。

- 作文します: `https://kumaken-1.github.io/sakubun-shimasu-manual/sakubun/`
- 学校マネジメント相談室: `https://kumaken-1.github.io/sakubun-shimasu-manual/school-management/`

トップURL `https://kumaken-1.github.io/sakubun-shimasu-manual/` は、学校マネジメント相談カード作成アプリ用です。

## 閲覧用ファイル

- `index.html`: GitHub Pages公開用アプリ
- `sakubun/index.html`: Gems「作文します ver.2.3」マニュアル公開用
- `school-management/index.html`: Gem「学校マネジメント相談室」マニュアル公開用
- `docs/Gem学校マネジメント相談室_使い方マニュアル.html`: HTML版マニュアル
- `docs/Gem学校マネジメント相談室_使い方マニュアル.md`: Markdown版マニュアル
- `docs/Gems作文しますver2.3_使い方マニュアル.html`: HTML版マニュアル
- `docs/Gems作文しますver2.3_使い方マニュアル.md`: Markdown版マニュアル

## アプリの使い方

1. 相談タイトル、状況、事実、困り感、願い、不明点を入力します。
2. 関係する領域や安全・緊急性を選びます。
3. 生成された「貼り付け用プロンプト」をコピーします。
4. Gem「学校マネジメント相談室」に貼り付けて相談します。

このアプリ自体はAI APIを呼び出しません。入力内容はブラウザ内で整形されます。

## 更新方法

マニュアルMarkdownを編集したあと、次のコマンドでHTMLを再生成できます。

```powershell
& 'C:\Users\ken1k\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/markdown_to_html.py 'docs/Gem学校マネジメント相談室_使い方マニュアル.md' 'docs/Gem学校マネジメント相談室_使い方マニュアル.html'
```

公開用の専用URLへ反映するときは、対応する `index.html` にコピーします。

```powershell
Copy-Item 'docs/Gems作文しますver2.3_使い方マニュアル.html' 'sakubun/index.html' -Force
Copy-Item 'docs/Gem学校マネジメント相談室_使い方マニュアル.html' 'school-management/index.html' -Force
```
