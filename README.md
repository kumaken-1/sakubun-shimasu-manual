# 作文します ver.2.3 使い方マニュアル

Gems「作文します ver.2.3」の初心者向け使い方マニュアルです。

GitHub PagesでHTML版をそのまま閲覧できるように、ルートの `index.html` に最新版を配置しています。

## 閲覧用ファイル

- `index.html`: GitHub Pages公開用HTML
- `docs/Gems作文しますver2.3_使い方マニュアル.html`: HTML版マニュアル
- `docs/Gems作文しますver2.3_使い方マニュアル.md`: Markdown版マニュアル

## 更新方法

Markdownを編集したあと、次のコマンドでHTMLを再生成できます。

```powershell
& 'C:\Users\ken1k\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/markdown_to_html.py 'docs/Gems作文しますver2.3_使い方マニュアル.md' 'docs/Gems作文しますver2.3_使い方マニュアル.html'
Copy-Item -LiteralPath 'docs/Gems作文しますver2.3_使い方マニュアル.html' -Destination 'index.html' -Force
```

