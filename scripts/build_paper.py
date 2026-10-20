"""Build the report as a web page (and its figures) for the portfolio site.

    python3 scripts/build_paper.py [--site ../kmsmohamedansar.github.io] [--no-pdf]

Turns paper/report.md into <site>/portfolio/public/p/rea-study/report.html (markdown by
`npx -y marked@14.1.4`), copies the six figures beside it, and prints a PDF from the page with
headless Chromium. While the report still has [OWNER] placeholders the page carries a visible
DRAFT banner; set DRAFT = False below only when the author has written every marked part.
"""
import argparse, html, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRAFT = True
CHROME = next(iter(sorted(pathlib.Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"))), None)

CSS = """
:root { --ink:#1b1a17; --muted:#5f5a51; --rule:#d8d2c4; --paper:#fbf9f4; --accent:#0e7490; --tint:#eef3f4; }
* { box-sizing:border-box }
html { background:var(--paper) }
body { margin:0; color:var(--ink); background:var(--paper); font:17px/1.65 "Source Serif 4", Georgia, serif; }
main { max-width:760px; margin:0 auto; padding:40px 16px 80px }
.top { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;
  font:600 12px/1.4 "IBM Plex Mono", ui-monospace, monospace; letter-spacing:.06em;
  text-transform:uppercase; color:var(--muted); border-bottom:1px solid var(--rule); padding-bottom:10px; margin-bottom:28px }
.top a { color:var(--accent); text-decoration:none }
.draft { border:2px solid #b45309; background:#fff7ed; color:#7c2d12; padding:12px 14px; border-radius:6px;
  font:600 14px/1.5 "IBM Plex Sans", system-ui, sans-serif; margin:0 0 26px }
h1 { font:700 clamp(2rem,6vw,2.8rem)/1.1 "Source Serif 4", Georgia, serif; letter-spacing:-.01em; margin:0 0 6px }
h1 + h2 { font:400 1.25rem/1.35 "Source Serif 4", Georgia, serif; color:var(--muted); margin:0 0 18px; border:0; padding:0 }
h2 { font:700 1.35rem/1.3 "IBM Plex Sans", system-ui, sans-serif; margin:48px 0 12px; padding-top:14px; border-top:1px solid var(--rule) }
h3 { font:600 1.05rem/1.35 "IBM Plex Sans", system-ui, sans-serif; margin:30px 0 8px }
p, li { hyphens:auto }
a { color:var(--accent) }
hr { display:none }
blockquote { margin:14px 0; padding:2px 0 2px 14px; border-left:3px solid var(--rule); color:var(--muted) }
code { font:0.86em "IBM Plex Mono", ui-monospace, monospace; background:var(--tint); padding:1px 4px; border-radius:3px }
pre { background:#eef1f1; padding:14px; overflow-x:auto; border-radius:4px; font-size:13px; line-height:1.5 }
pre code { background:none; padding:0 }
.table { overflow-x:auto; margin:16px 0 }
table { border-collapse:collapse; width:100%; font:13.5px/1.45 "IBM Plex Sans", system-ui, sans-serif }
th, td { text-align:left; padding:7px 8px; border-bottom:1px solid var(--rule); vertical-align:top }
th { font-weight:600; border-bottom:2px solid var(--ink) }
img { display:block; max-width:100%; height:auto; margin:18px auto 6px; background:#fcfcfb; border:1px solid var(--rule); border-radius:4px }
.pdf { display:inline-block; margin:0 0 6px; padding:8px 14px; border:1px solid var(--accent); border-radius:4px;
  font:600 13px "IBM Plex Sans", system-ui, sans-serif; text-decoration:none }
@media print {
  body { font-size:11pt; background:#fff } html { background:#fff }
  main { max-width:none; padding:0 }
  .top a, .pdf { display:none }
  h2 { break-after:avoid } table, img, pre { break-inside:avoid }
  @page { size:A4; margin:18mm 16mm }
}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=str(ROOT.parent / "kmsmohamedansar.github.io"))
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    out = pathlib.Path(a.site) / "portfolio" / "public" / "p" / "rea-study"
    out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp()) / "body.html"
    subprocess.run(["npx", "-y", "marked@14.1.4", "--gfm", "-i", str(ROOT / "paper" / "report.md"), "-o", str(tmp)], check=True)
    body = tmp.read_text()
    for f in sorted((ROOT / "paper" / "figures").glob("*.svg")): shutil.copy(f, out / f.name)
    body = body.replace('src="figures/', 'src="')
    body = re.sub(r"<table>", '<div class="table"><table>', body).replace("</table>", "</table></div>")
    title = "My Take on REA · Mohamed Ansar"
    desc = "An independent test of whether a reverse-engineering tool helps an AI agent explain programs it has no source for, and whether the agent says what it cannot know."
    banner = ('<p class="draft">Draft. Parts marked [OWNER] are still to be written by the author, and the title, byline and disclosure are not yet approved. '
              'Do not treat this page as final.</p>') if DRAFT else ""
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body><main>
<div class="top"><span>Technical report · October 2026</span><a href="/#project/rea-study">Back to the project</a></div>
{banner}<a class="pdf" href="report.pdf">Download PDF</a>
{body}
</main></body>
</html>
"""
    (out / "report.html").write_text(page)
    print("wrote", out / "report.html")
    if not a.no_pdf:
        if CHROME is None: sys.exit("no Chromium found for the PDF")
        subprocess.run([str(CHROME), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out / 'report.pdf'}", f"file://{out / 'report.html'}"], check=True, capture_output=True, timeout=180)
        print("wrote", out / "report.pdf", f"({(out / 'report.pdf').stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
