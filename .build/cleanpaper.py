#!/usr/bin/env python3
"""Post-process pandoc-generated paper HTML.

Operates only on the content inside <div class="body">...</div> so that
the template header (with its own <h1>) is preserved untouched.

Transforms:
- Paragraph-only bold pseudo-headings -> real <h2>/<h3>.
- Strip duplicate title/author/email paragraphs that the .docx contains.
- Lift Highlights bullets out of pandoc's <blockquote>.
- Lift Abstract paragraph out of its <blockquote>.

Usage: cleanpaper.py <html-file> <paper title>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SECTION_NAMES = {
    "highlights",
    "abstract",
    "keywords",
    "introduction",
    "literature review",
    "methodology",
    "methods",
    "data",
    "data and methodology",
    "data and measurement",
    "empirical strategy",
    "results",
    "main results",
    "findings",
    "discussion",
    "conclusion",
    "references",
    "limitations",
    "robustness",
    "robustness checks",
    "extensions",
    "extension",
    "appendix",
    "implications",
    "policy implications",
    "proposal",
    "case study",
    "research question",
}


def is_section_name(text: str) -> bool:
    t = text.strip().rstrip(".:").lower()
    return t in SECTION_NAMES


def convert_pseudo_headings(html: str) -> str:
    # <p><strong>N. Title</strong></p>  -> <h2>N. Title</h2>
    html = re.sub(
        r"<p><strong>(\d+\.\s+[^<]+?)</strong></p>",
        r"<h2>\1</h2>",
        html,
        flags=re.DOTALL,
    )
    # <p><strong>N.M Sub</strong></p>   -> <h3>N.M Sub</h3>
    html = re.sub(
        r"<p><strong>(\d+\.\d+\s+[^<]+?)</strong></p>",
        r"<h3>\1</h3>",
        html,
        flags=re.DOTALL,
    )

    def named_repl(m: re.Match) -> str:
        inner = m.group(1).strip().rstrip(".:")
        if is_section_name(inner):
            return f"<h2>{inner.title()}</h2>"
        return m.group(0)

    # Match <p><strong>X</strong></p> and <p><u>X</u></p>
    html = re.sub(
        r"<p><strong>([A-Za-z][A-Za-z &]{2,40})</strong></p>",
        named_repl,
        html,
    )
    html = re.sub(
        r"<p><u>([A-Za-z][A-Za-z &]{2,40})</u></p>",
        named_repl,
        html,
    )
    return html


def wrap_named_section(body_html: str, heading_text: str, section_class: str) -> str:
    """Ensure <h2>heading_text</h2> and everything up to the next <h2>
    are wrapped in <section class="section_class">."""
    # Skip if already wrapped
    if re.search(
        rf'<section class="{section_class}">\s*<h2>{re.escape(heading_text)}</h2>',
        body_html,
    ):
        return body_html

    pattern = re.compile(
        rf"<h2>{re.escape(heading_text)}</h2>(.*?)(?=<h2>|$)",
        re.DOTALL,
    )
    m = pattern.search(body_html)
    if not m:
        return body_html
    inner = m.group(1).strip()
    replacement = (
        f'<section class="{section_class}">\n<h2>{heading_text}</h2>\n{inner}\n</section>\n'
    )
    return body_html[: m.start()] + replacement + body_html[m.end() :]


def strip_duplicate_title_block(body_html: str, title: str) -> str:
    # Collapse any whitespace-broken title into a flexible pattern
    title_pat = re.escape(title).replace(r"\ ", r"\s+")
    # Strip: <p><strong>Title</strong></p>  (multiline tolerant)
    body_html = re.sub(
        rf"<p><strong>{title_pat}[^<]*</strong></p>\s*",
        "",
        body_html,
        count=1,
        flags=re.DOTALL,
    )
    # Strip: <h1>Title</h1>
    body_html = re.sub(
        rf"<h1[^>]*>{title_pat}[^<]*</h1>\s*",
        "",
        body_html,
        count=1,
        flags=re.DOTALL,
    )

    # Strip first occurrences of author / school / email
    patterns = [
        r"<p>\s*Verushka Patel\s*</p>\s*",
        r"<p>\s*St\.\s*Mary['\u2019]?s School[^<]*</p>\s*",
        r"<p>\s*[Vv]erushkapatel4@gmail\.com\s*</p>\s*",
    ]
    for p in patterns:
        body_html = re.sub(p, "", body_html, count=1)
    return body_html


def lift_highlights_from_blockquote(body_html: str) -> str:
    m = re.search(
        r"(<h2>Highlights</h2>)\s*<blockquote>(.*?)</blockquote>",
        body_html,
        re.DOTALL,
    )
    if not m:
        return body_html
    inner = m.group(2)
    bullets = re.findall(r"<p>[\u2022•·]\s*(.*?)</p>", inner, re.DOTALL)
    if not bullets:
        bullets = re.findall(r"<p>-\s*(.*?)</p>", inner, re.DOTALL)
    if not bullets:
        return body_html
    lis = "\n".join(f"  <li>{b.strip()}</li>" for b in bullets)
    replacement = (
        f'<section class="highlights">\n<h2>Highlights</h2>\n<ul>\n{lis}\n</ul>\n</section>'
    )
    return body_html[: m.start()] + replacement + body_html[m.end() :]


def lift_abstract_from_blockquote(body_html: str) -> str:
    m = re.search(
        r"(<h2>Abstract</h2>)\s*<blockquote>(.*?)</blockquote>",
        body_html,
        re.DOTALL,
    )
    if not m:
        return body_html
    inner = m.group(2).strip()
    replacement = f'<section class="abstract">\n<h2>Abstract</h2>\n{inner}\n</section>'
    return body_html[: m.start()] + replacement + body_html[m.end() :]


BODY_RE = re.compile(r'(<div class="body">)(.*?)(</div>\s*<footer)', re.DOTALL)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: cleanpaper.py <html-file> <title>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    title = sys.argv[2]
    html = path.read_text(encoding="utf-8")

    match = BODY_RE.search(html)
    if not match:
        print(f"error: could not find body div in {path}", file=sys.stderr)
        return 1

    opener, body, closer = match.group(1), match.group(2), match.group(3)
    body = convert_pseudo_headings(body)
    body = strip_duplicate_title_block(body, title)
    body = lift_highlights_from_blockquote(body)
    body = lift_abstract_from_blockquote(body)
    body = wrap_named_section(body, "Highlights", "highlights")
    body = wrap_named_section(body, "Abstract", "abstract")
    # Pandoc writes img src relative to cwd, not the output file.
    # The output lives in papers/, so strip the "papers/" prefix.
    body = re.sub(r'src="papers/', 'src="', body)

    new_html = html[: match.start()] + opener + body + closer + html[match.end() :]
    path.write_text(new_html, encoding="utf-8")
    print(f"cleaned: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
