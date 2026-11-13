"""Generate a browser viewable code exhibit sheet for the demo recording.

Reads the real files so the line numbers and the code can never drift from the repository,
and writes a single light-theme HTML page that can be scrolled full screen during recording.
"""
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXHIBITS = [
    (1, "load_dataset.py", 27, 34,
     "Category 5 is scored against the trap answer",
     "The paper's evaluation behind Table 1 scored adversarial questions against "
     "<code>adversarial_answer</code> — the wrong answer — so falling for the trap reads as a "
     "high score. 444 of the 446 have no gold answer at all."),
    (2, "memory_layer_robust.py", 414, 419,
     "The whole modification is one line (417)",
     "With <code>--no-evolution</code>, a note keeps its LLM-extracted metadata but never gains "
     "links, never strengthens tags, never rewrites its neighbours. Retrieval, prompts, k, seeds "
     "and metrics are untouched."),
    (3, "test_advanced_robust.py", 239, 247,
     "The cache trap that would have faked a null result",
     "The cache path encodes backend and model, not the memory configuration. Without the "
     "<code>_noevo</code> suffix both arms share one directory, the ablation reloads the "
     "baseline's notes, and the experiment reports a difference of exactly zero."),
    (4, "utils.py", 84, 96,
     "The swallowed exception: BLEU-1 was silently 0.0 for every question",
     "nltk 3.8.1 calls <code>Fraction(_normalize=)</code>, removed in Python 3.12. The bare "
     "<code>except</code> turned the TypeError into 0.0, so a broken metric looked like a low "
     "score. Now the first failure is reported out loud."),
    (5, "test_advanced_robust.py", 419, 421,
     "Retrieval depth: the driver defaults to k=10, paper Table 5 lists 40/50",
     "The baseline uses the shipped default; one extra trial at k=40 on the identical cached "
     "memories measures the setting gap instead of assuming it."),
]

CSS = """
:root { --ink:#1a1a1a; --muted:#5f5f5f; --rule:#d8d8d8; --bg:#fdfdfc; --accent:#7a1f1f; }
* { box-sizing: border-box; }
body { margin:0; padding:0 64px 96px; background:var(--bg); color:var(--ink);
  font-family:"Segoe UI",-apple-system,"Helvetica Neue",Arial,sans-serif; font-size:17px; line-height:1.55; }
nav { position:sticky; top:0; z-index:5; background:rgba(253,253,252,.96);
  border-bottom:1px solid var(--rule); padding:12px 0 11px; display:flex; gap:20px;
  flex-wrap:wrap; font-size:14.5px; }
nav a { color:var(--accent); text-decoration:none; letter-spacing:.01em; }
nav a:hover { text-decoration:underline; }
header { max-width:980px; margin:26px auto 40px; border-bottom:2px solid var(--ink); padding-bottom:18px; }
h1 { font-size:29px; margin:0 0 8px; font-weight:650; letter-spacing:-.01em; }
header p { margin:0; color:var(--muted); font-size:15px; }
section { max-width:980px; margin:0 auto 60px; scroll-margin-top:64px; page-break-inside:avoid; }
.ex-no { display:inline-block; font-size:12.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--accent); font-weight:700; margin-bottom:6px; }
h2 { font-size:22px; margin:0 0 8px; font-weight:620; letter-spacing:-.01em; }
.note { margin:0 0 14px; color:#333; font-size:15.5px; }
.filepath { font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:14px;
  color:var(--muted); margin-bottom:10px; }
pre { margin:0; background:#fff; border:1px solid var(--rule); border-left:3px solid var(--ink);
  border-radius:3px; padding:18px 20px; overflow-x:auto;
  font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:15.5px; line-height:1.62; }
.ln { display:inline-block; width:3.1em; color:#9a9a9a; text-align:right; margin-right:1.4em;
  user-select:none; font-variant-numeric:tabular-nums; }
.hit { background:#fff4c2; }
.hit .ln { color:#8a6a00; }
code { font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:.94em;
  background:#f0efec; padding:1px 5px; border-radius:3px; }
@media print { body{padding:0;font-size:12px} section{margin-bottom:28px} pre{font-size:11px} }
"""


def render_snippet(path, start, end, highlight=None):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    rows = []
    for n in range(start, end + 1):
        text = lines[n - 1] if n - 1 < len(lines) else ""
        cls = ' class="hit"' if highlight and n == highlight else ""
        rows.append(
            f'<div{cls}><span class="ln">{n}</span>{html.escape(text) or "&nbsp;"}</div>'
        )
    return "\n".join(rows), len(lines)


def main():
    parts = []
    for no, path, start, end, title, note in EXHIBITS:
        highlight = {1: 33, 2: 417, 3: 241, 4: 86, 5: 419}[no]
        body, total = render_snippet(path, start, end, highlight)
        parts.append(
            f'<section id="ex{no}">\n'
            f'  <div class="ex-no">Exhibit {no}</div>\n'
            f'  <h2>{html.escape(title)}</h2>\n'
            f'  <p class="note">{note}</p>\n'
            f'  <div class="filepath">{html.escape(path)} — lines {start}-{end} of {total}</div>\n'
            f'  <pre>{body}</pre>\n'
            f'</section>'
        )

    doc = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>A-MEM reproduction — code exhibits</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n"
        "<nav>"
        '<a href="#ex1">1 · category 5 scoring</a>'
        '<a href="#ex2">2 · the one-line change</a>'
        '<a href="#ex3">3 · the cache trap</a>'
        '<a href="#ex4">4 · the swallowed exception</a>'
        '<a href="#ex5">5 · retrieval depth</a>'
        "</nav>\n"
        "<header>\n"
        "  <h1>A-MEM reproduction — code exhibits</h1>\n"
        "  <p>FTEC5660 reproducibility work · Zi Han QIU · 1155268166 · "
        "lines read from the repository at HEAD, not transcribed</p>\n"
        "</header>\n"
        + "\n".join(parts)
        + "\n</body>\n</html>\n"
    )
    out = os.path.join(ROOT, "report", "code_exhibits.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print("wrote", out, len(doc), "bytes")


if __name__ == "__main__":
    main()
