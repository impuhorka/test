#!/usr/bin/env python3
"""Convert markdown file to styled A4 PDF using WeasyPrint."""

import argparse
import re
import sys
from pathlib import Path

import markdown
from weasyprint import HTML


CSS = """
@page {
    size: A4;
    margin: 2cm 2cm 2.2cm 2.5cm;
    @bottom-center {
        content: counter(page);
        font-family: "DejaVu Serif", serif;
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: "DejaVu Serif", "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.45;
    color: #1a1a1a;
    text-align: justify;
    hyphens: auto;
}

h1 {
    font-size: 20pt;
    font-weight: bold;
    text-align: center;
    margin: 0 0 0.8em;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin: 1.4em 0 0.5em;
    page-break-after: avoid;
    border-bottom: 0.5pt solid #ccc;
    padding-bottom: 0.2em;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    margin: 1em 0 0.4em;
    page-break-after: avoid;
}

p {
    margin: 0 0 0.6em;
}

ul, ol {
    margin: 0.4em 0 0.8em 1.2em;
    padding: 0;
}

li {
    margin-bottom: 0.25em;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.8em 0 1em;
    font-size: 10pt;
    page-break-inside: avoid;
}

th, td {
    border: 0.5pt solid #999;
    padding: 0.35em 0.5em;
    vertical-align: top;
}

th {
    background: #f0f0f0;
    font-weight: bold;
}

hr {
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 1.2em 0;
}

strong {
    font-weight: bold;
}

em {
    font-style: italic;
}

a {
    color: #1a1a1a;
    text-decoration: none;
}

blockquote {
    margin: 0.8em 1em;
    padding-left: 0.8em;
    border-left: 2pt solid #ccc;
    color: #444;
}

figure {
    margin: 1em 0 1.2em;
    page-break-inside: avoid;
    text-align: center;
}

figure img {
    max-width: 100%;
    height: auto;
}

.figure-svg {
    margin: 0 auto;
    max-width: 100%;
}

.figure-svg svg {
    width: 100%;
    height: auto;
    display: block;
}

figcaption {
    font-size: 9.5pt;
    color: #555;
    font-style: italic;
    margin-top: 0.4em;
    text-align: center;
}

.title-meta {
    text-align: center;
    margin-bottom: 1.5em;
    font-size: 11pt;
}

.title-meta p {
    margin: 0.2em 0;
}
"""


def strip_toc_links(md_text: str) -> str:
    """Remove markdown TOC section; PDF gets headings from content."""
    return re.sub(
        r"## Spis treści\n\n.*?\n\n---\n",
        "",
        md_text,
        count=1,
        flags=re.DOTALL,
    )


def embed_svg_figures(html_body: str, base_dir: Path) -> str:
    """Replace <img src="...svg"> with inline SVG so WeasyPrint renders figures."""
    pattern = re.compile(
        r'<img\s+[^>]*src="([^"]+\.svg)"[^>]*/?>',
        re.IGNORECASE,
    )

    def repl(match: re.Match[str]) -> str:
        src = match.group(1)
        svg_path = (base_dir / src).resolve()
        if not svg_path.is_file():
            return match.group(0)
        svg_content = svg_path.read_text(encoding="utf-8")
        svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content).strip()
        return (
            f'<div class="figure-svg">{svg_content}</div>'
        )

    return pattern.sub(repl, html_body)


def convert(input_path: Path, output_path: Path) -> None:
    md_text = input_path.read_text(encoding="utf-8")
    md_text = strip_toc_links(md_text)

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "sane_lists", "smarty"],
    )
    html_body = embed_svg_figures(html_body, input_path.parent)

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="utf-8"/>
  <title>{input_path.stem}</title>
  <style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    HTML(string=html, base_url=str(input_path.parent)).write_pdf(str(output_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert markdown to PDF")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    output = args.output or args.input.with_suffix(".pdf")
    convert(args.input, output)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
