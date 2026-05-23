from __future__ import annotations

import html
import re
import sys
from datetime import date
from pathlib import Path


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def inline(value: str) -> str:
    value = escape(value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    return value


def is_table_divider(line: str) -> bool:
    cells = line.strip().strip("|").split("|")
    return len(cells) > 1 and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def parse_table(lines: list[str], start: int) -> tuple[str, int] | None:
    if start + 1 >= len(lines):
        return None
    if "|" not in lines[start] or not is_table_divider(lines[start + 1]):
        return None

    rows: list[str] = []
    index = start
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        rows.append(lines[index])
        index += 1

    def cells(line: str) -> list[str]:
        return [inline(cell.strip()) for cell in line.strip().strip("|").split("|")]

    header = cells(rows[0])
    body_rows = [cells(row) for row in rows[2:]]
    parts = ["<div class=\"table-wrap\"><table>", "<thead><tr>"]
    parts.extend(f"<th>{cell}</th>" for cell in header)
    parts.extend(["</tr></thead>", "<tbody>"])
    for row in body_rows:
        parts.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    parts.extend(["</tbody></table></div>"])
    return "".join(parts), index


def slug(index: int) -> str:
    return f"section-{index}"


def parse(markdown: str) -> tuple[str, list[tuple[str, str, int]]]:
    lines = markdown.replace("\r\n", "\n").split("\n")
    parts: list[str] = []
    toc: list[tuple[str, str, int]] = []
    paragraph: list[str] = []
    items: list[str] = []
    in_code = False
    code: list[str] = []
    heading_index = 0

    def close_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            parts.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal items
        if items:
            parts.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            items = []

    index = 0
    while index < len(lines):
        line = lines[index]

        if line.startswith("```"):
            close_paragraph()
            close_list()
            if in_code:
                parts.append(f"<pre><code>{escape(chr(10).join(code))}</code></pre>")
                code = []
                in_code = False
            else:
                in_code = True
            index += 1
            continue

        if in_code:
            code.append(line)
            index += 1
            continue

        table = parse_table(lines, index)
        if table:
            close_paragraph()
            close_list()
            html_table, next_index = table
            parts.append(html_table)
            index = next_index
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            close_paragraph()
            close_list()
            heading_index += 1
            level = len(heading.group(1))
            text = heading.group(2).strip()
            ident = slug(heading_index)
            if level <= 2:
                toc.append((ident, text, level))
            parts.append(f"<h{level} id=\"{ident}\">{inline(text)}</h{level}>")
            index += 1
            continue

        item = re.match(r"^\s*-\s+(.+)$", line)
        if item:
            close_paragraph()
            items.append(item.group(1))
            index += 1
            continue

        if not line.strip():
            close_paragraph()
            close_list()
            index += 1
            continue

        close_list()
        paragraph.append(line.strip())
        index += 1

    close_paragraph()
    close_list()
    return "\n".join(parts), toc


def build_html(title: str, body: str, toc: list[tuple[str, str, int]]) -> str:
    toc_html = "\n".join(
        f'<a class="toc-level-{level}" href="#{ident}">{inline(text)}</a>' for ident, text, level in toc
    )
    def toc_id(starts_with: str, fallback: str) -> str:
        for ident, text, _level in toc:
            if text.startswith(starts_with):
                return ident
        return fallback

    quick_start_id = toc_id("0.", "section-2")
    multi_module_id = toc_id("4. マルチモジュール", "section-14")
    custom_id = toc_id("17. 秘技", "section-72")
    generated = date.today().strftime("%Y年%-m月%-d日") if sys.platform != "win32" else f"{date.today().year}年{date.today().month}月{date.today().day}日"
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.DOTALL)
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f7f8fb;
      --paper: #ffffff;
      --ink: #071b5f;
      --muted: #4b5570;
      --line: #dbe1ef;
      --nav: #071b5f;
      --accent: #ff4b4b;
      --accent-2: #071b5f;
      --accent-3: #ff6a5c;
      --accent-soft: #fff1f1;
      --blue-soft: #eef3ff;
      --code-bg: #071b5f;
      --code-ink: #f7fbff;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font-family: "Yu Gothic", "YuGothic", "Meiryo", system-ui, sans-serif;
      line-height: 1.75;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        radial-gradient(circle at 16px 16px, rgba(255, 75, 75, 0.12) 2px, transparent 2px);
      background-size: 34px 34px;
      mask-image: linear-gradient(to bottom, #000 0%, transparent 55%);
    }}
    .hero {{
      position: relative;
      max-width: 1240px;
      margin: 0 auto;
      padding: 28px 24px 0;
    }}
    .hero-inner {{
      position: relative;
      display: block;
      overflow: hidden;
      border: 3px solid var(--nav);
      border-radius: 18px;
      background: var(--paper);
      color: var(--ink);
      box-shadow: 0 18px 0 rgba(7, 27, 95, 0.09);
    }}
    .hero-copy {{
      padding: 30px 38px 34px;
      text-align: center;
    }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 14px;
      padding: 4px 16px;
      border-radius: 999px;
      background: #fff;
      color: var(--nav);
      font-weight: 700;
      font-size: 0.88rem;
      letter-spacing: 0;
      border-top: 4px dotted var(--accent);
      border-bottom: 4px dotted var(--accent);
    }}
    .hero h1 {{
      margin: 0;
      max-width: none;
      font-size: clamp(2.35rem, 6vw, 5.6rem);
      line-height: 1.05;
      letter-spacing: 0;
      font-weight: 900;
    }}
    .hero h1::first-letter {{
      color: var(--accent);
    }}
    .hero-lead {{
      max-width: 900px;
      margin: 18px auto 0;
      color: var(--muted);
      font-size: 1.08rem;
      font-weight: 700;
    }}
    .hero-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 24px;
      justify-content: center;
    }}
    .hero-actions a {{
      display: inline-flex;
      align-items: center;
      min-height: 40px;
      padding: 8px 16px;
      border: 2px solid var(--accent);
      border-radius: 999px;
      color: #fff;
      background: var(--accent);
      text-decoration: none;
      font-weight: 700;
      font-size: 0.92rem;
    }}
    .hero-actions a:first-child {{
      color: #fff;
      background: var(--nav);
      border-color: var(--nav);
    }}
    .hero-panel {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 14px;
      align-items: center;
      margin: 0 26px 26px;
      padding: 18px 22px;
      border: 2px solid var(--nav);
      border-radius: 14px;
      background: var(--blue-soft);
      color: var(--ink);
      text-align: left;
    }}
    .hero-panel strong {{
      display: block;
      font-size: 1.25rem;
      line-height: 1.35;
    }}
    .hero-panel span {{
      display: block;
      color: var(--muted);
      line-height: 1.65;
    }}
    .quick-metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 4px;
      min-width: 260px;
    }}
    .quick-metrics div {{
      padding: 10px;
      border-radius: 10px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      text-align: center;
      line-height: 1.35;
    }}
    .page {{
      display: grid;
      grid-template-columns: minmax(230px, 292px) minmax(0, 1fr);
      gap: 22px;
      max-width: 1240px;
      margin: 0 auto;
      padding: 24px 24px 64px;
      position: relative;
    }}
    aside {{
      position: sticky;
      top: 20px;
      align-self: start;
      max-height: calc(100vh - 40px);
      overflow: auto;
      padding: 16px;
      border: 3px solid var(--nav);
      border-radius: 14px;
      background: var(--nav);
      color: #fff;
      box-shadow: 0 10px 0 rgba(7, 27, 95, 0.12);
    }}
    aside h2 {{
      margin: 0 0 12px;
      font-size: 1rem;
      color: #fff;
      text-align: center;
      border-bottom: 4px dotted var(--accent);
      padding-bottom: 10px;
    }}
    aside a {{
      display: block;
      margin: 3px 0;
      padding: 7px 9px;
      border-radius: 8px;
      color: #d9e7ec;
      text-decoration: none;
      font-size: 0.92rem;
      line-height: 1.45;
    }}
    aside a:hover {{
      color: #202124;
      background: #fff;
    }}
    .toc-level-1 {{ font-weight: 700; color: #fff; }}
    .toc-level-2 {{ padding-left: 16px; }}
    main {{
      min-width: 0;
      padding: 4px 0 30px;
      counter-reset: chapter;
    }}
    main > * {{
      max-width: 860px;
      margin-left: auto;
      margin-right: auto;
    }}
    main > h2,
    main > h2 + p,
    main > h2 + p + p {{
      max-width: 940px;
    }}
    .meta {{
      max-width: 940px;
      margin: 0 auto 14px;
      color: var(--muted);
      font-size: 0.95rem;
      text-align: right;
    }}
    main h1 {{
      display: none;
    }}
    main > h2 {{
      counter-increment: chapter;
      position: relative;
      margin: 26px auto 18px;
      padding: 20px 24px 20px 84px;
      border: 3px solid var(--nav);
      border-radius: 14px;
      background: var(--paper);
      box-shadow: 0 8px 0 rgba(7, 27, 95, 0.08);
      font-size: clamp(1.35rem, 2vw, 1.75rem);
      line-height: 1.45;
    }}
    main > h2::before {{
      content: counter(chapter, decimal-leading-zero);
      position: absolute;
      left: 22px;
      top: 50%;
      transform: translateY(-50%);
      display: grid;
      place-items: center;
      width: 46px;
      height: 46px;
      border-radius: 50%;
      background: var(--accent);
      color: #fff;
      font-size: 0.95rem;
      font-weight: 800;
      line-height: 1;
    }}
    main > h2:nth-of-type(3n + 1)::before {{ background: var(--accent); }}
    main > h2:nth-of-type(3n + 2)::before {{ background: var(--nav); }}
    main h3 {{
      margin: 30px auto 12px;
      padding: 10px 14px;
      border-left: 7px solid var(--accent);
      border-radius: 8px;
      background: var(--accent-soft);
      font-size: 1.14rem;
    }}
    main h4 {{
      margin: 24px auto 8px;
      color: var(--nav);
      font-size: 1.03rem;
    }}
    p {{ margin: 0 0 16px; }}
    ul {{
      margin: 0 0 18px;
      padding: 0;
      list-style: none;
    }}
    li {{
      position: relative;
      margin: 7px 0;
      padding-left: 24px;
    }}
    li::before {{
      content: "";
      position: absolute;
      left: 4px;
      top: 0.82em;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
    }}
    code {{
      padding: 0.12em 0.35em;
      border-radius: 4px;
      background: #edf1f5;
      font-family: "Cascadia Mono", Consolas, monospace;
      font-size: 0.94em;
    }}
    pre {{
      position: relative;
      max-width: 940px;
      margin: 18px auto 26px;
      padding: 44px 20px 20px;
      overflow: auto;
      border: 1px solid #2d3a47;
      border-radius: 14px;
      background: var(--code-bg);
      color: var(--code-ink);
      line-height: 1.7;
      white-space: pre-wrap;
      box-shadow: 0 8px 0 rgba(7, 27, 95, 0.16);
    }}
    pre::before {{
      content: "そのまま使えるプロンプト";
      position: absolute;
      left: 16px;
      top: 12px;
      padding: 4px 9px;
      border-radius: 999px;
      background: var(--accent);
      color: #fff;
      font-size: 0.78rem;
      font-weight: 800;
    }}
    pre code {{
      padding: 0;
      background: transparent;
      color: inherit;
      font-size: 0.94rem;
    }}
    .table-wrap {{
      overflow-x: auto;
      max-width: 940px;
      margin: 18px auto 24px;
      border: 3px solid var(--nav);
      border-radius: 14px;
      box-shadow: 0 8px 0 rgba(7, 27, 95, 0.08);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 540px;
      background: #fff;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: var(--nav);
      color: #fff;
      font-weight: 700;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    tr:nth-child(even) td {{ background: var(--blue-soft); }}
    @media (max-width: 880px) {{
      .hero {{
        padding: 16px 16px 0;
      }}
      .hero-inner {{
        display: block;
        border-radius: 16px;
      }}
      .hero-copy {{
        padding: 26px 22px;
      }}
      .hero-panel {{
        display: block;
        padding: 22px;
        margin: 0 16px 18px;
      }}
      .quick-metrics {{
        grid-template-columns: 1fr;
      }}
      .page {{
        display: block;
        padding: 16px;
      }}
      aside {{
        position: static;
        max-height: none;
        margin-bottom: 16px;
      }}
      main {{
        padding: 4px 0 40px;
      }}
      .meta {{
        text-align: left;
      }}
      main > h2 {{
        padding: 18px 18px 18px 70px;
      }}
      main > h2::before {{
        left: 16px;
        width: 38px;
        height: 38px;
      }}
    }}
    @media print {{
      body {{ background: #fff; }}
      body::before, .hero {{ display: none; }}
      .page {{ display: block; max-width: none; padding: 0; }}
      aside {{ display: none; }}
      main {{
        padding: 0;
        border: 0;
        box-shadow: none;
      }}
      h2 {{ break-after: avoid; }}
      pre, table {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <div class="hero-copy">
        <p class="eyebrow">初心者が3分で試せる学校文書AIガイド</p>
        <h1>{escape(title)}</h1>
        <p class="hero-lead">通信文、校務文書、レポート、素材整理、Web調査まで。まず試して、少しずつ自分の仕事に合わせて育てるための実用マニュアルです。</p>
        <div class="hero-actions">
          <a href="#{quick_start_id}">まず使ってみる</a>
          <a href="#{multi_module_id}">マルチモジュールを見る</a>
          <a href="#{custom_id}">カスタム版の作り方</a>
        </div>
      </div>
      <div class="hero-panel">
        <strong>読む前に、まず1回。</strong>
        <span>完璧な指示はいりません。下書き、不明点、確認事項まで一緒に出す使い方から始められます。</span>
        <div class="quick-metrics">
          <div>3分<br>お試し</div>
          <div>17章<br>実務型</div>
          <div>コピペ<br>例つき</div>
        </div>
      </div>
    </div>
  </header>
  <div class="page">
    <aside>
      <h2>目次</h2>
      {toc_html}
    </aside>
    <main>
      <p class="meta">HTML版生成日：{generated}</p>
      {body}
    </main>
  </div>
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scripts/markdown_to_html.py <input.md> <output.html>", file=sys.stderr)
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    markdown = input_path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Gems 作文します ver.2.3 使い方マニュアル"
    body, toc = parse(markdown)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(title, body, toc), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
