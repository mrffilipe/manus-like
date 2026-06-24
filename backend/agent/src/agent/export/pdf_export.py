"""Export markdown deliverables to PDF."""

from __future__ import annotations

import io
import re
from html import escape


def markdown_to_pdf_bytes(markdown_text: str, *, title: str = "Relatório") -> bytes:
    """Convert markdown-ish text to a simple PDF using xhtml2pdf."""
    from xhtml2pdf import pisa

    html_body = _markdown_to_html(markdown_text)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
  body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.45; margin: 40px; }}
  h1 {{ font-size: 18pt; color: #1a1a1a; }}
  h2 {{ font-size: 14pt; color: #333; margin-top: 18px; }}
  h3 {{ font-size: 12pt; color: #444; }}
  code, pre {{ background: #f5f5f5; font-size: 9pt; }}
  pre {{ padding: 8px; white-space: pre-wrap; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
</style>
</head><body>
<h1>{escape(title)}</h1>
{html_body}
</body></html>"""

    buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=buffer, encoding="utf-8")
    return buffer.getvalue()


def _markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    html_parts: list[str] = []
    in_pre = False
    in_table = False
    table_rows: list[str] = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_pre:
                html_parts.append("</pre>")
                in_pre = False
            else:
                html_parts.append("<pre>")
                in_pre = True
            continue

        if in_pre:
            html_parts.append(escape(line) + "\n")
            continue

        if "|" in stripped and stripped.count("|") >= 2:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= {"-", ":"} for c in cells):
                continue
            if not in_table:
                in_table = True
                table_rows = []
            tag = "th" if not table_rows else "td"
            if not table_rows:
                table_rows.append("<tr>" + "".join(f"<th>{escape(c)}</th>" for c in cells) + "</tr>")
            else:
                table_rows.append("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in cells) + "</tr>")
            continue
        elif in_table:
            html_parts.append("<table>" + "".join(table_rows) + "</table>")
            in_table = False
            table_rows = []

        if stripped.startswith("### "):
            html_parts.append(f"<h3>{escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            html_parts.append(f"<h2>{escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            html_parts.append(f"<h1>{escape(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            html_parts.append(f"<li>{_inline_format(escape(stripped[2:]))}</li>")
        elif stripped == "":
            html_parts.append("<br/>")
        else:
            html_parts.append(f"<p>{_inline_format(escape(stripped))}</p>")

    if in_table:
        html_parts.append("<table>" + "".join(table_rows) + "</table>")
    if in_pre:
        html_parts.append("</pre>")

    return "\n".join(html_parts)


def _inline_format(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text
