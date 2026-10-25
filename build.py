#!/usr/bin/env python3
"""Build unbranded PDFs from the HTML form sources.

Local build, zero signups: renders each form in print mode to printables/.

Engine order:
  1. Chrome / Chromium headless  (--print-to-pdf)  - preferred, best print CSS
  2. WeasyPrint CLI                              - fallback

Usage:
  python3 build.py            # build everything
  python3 build.py --clean    # delete built PDFs first
"""

import argparse
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORMS_DIR = ROOT / "forms"
DEFAULT_OUTPUT = ROOT / "printables"

# form source file -> PDF file name in printables/
FORMS = {
    "invoice.html": "service-invoice.pdf",
    "expense-log.html": "expense-log.pdf",
    "content-calendar.html": "content-calendar.pdf",
    "money-review.html": "weekly-money-review.pdf",
    "contract-checklist.html": "contract-sanity-checklist.pdf",
    "customer-emails.html": "customer-email-templates.pdf",
}

CHROME_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)

CROSS_PLATFORM_FLAGS = [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--no-pdf-header-footer",
    "--disable-extensions",
    "--disable-background-networking",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=10000",
]


def find_chrome():
    override = shutil.which("CHROME")  # allow CHROME=/path override via which trick
    if override:
        return override
    for name in CHROME_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    return None


def find_weasyprint():
    return shutil.which("weasyprint")


def _run(cmd, timeout=180):
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stderr: {result.stderr.strip()[:500]}"
        )
    return result


def build_pdf_with_chrome(chrome_bin, html_path, out_path):
    tmp_out = out_path.with_suffix(".pdf.tmp")
    if tmp_out.exists():
        tmp_out.unlink()
    cmd = [
        chrome_bin,
        *CROSS_PLATFORM_FLAGS,
        f"--crash-dumps-dir={tmp_out.parent}",
        str(tmp_out),
        html_path.resolve().as_uri(),
    ]
    try:
        _run(cmd)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"chrome timed out rendering {html_path.name}: {exc}") from exc
    if not tmp_out.exists():
        raise RuntimeError(f"chrome produced no PDF for {html_path.name}")
    shutil.move(str(tmp_out), out_path)


def build_pdf_with_weasyprint(weasy_bin, html_path, out_path):
    tmp_out = out_path.with_suffix(".pdf.tmp")
    try:
        _run([weasy_bin, "-e", "utf-8", str(html_path), str(tmp_out)])
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"weasyprint timed out rendering {html_path.name}: {exc}") from exc
    if not tmp_out.exists():
        raise RuntimeError(f"weasyprint produced no PDF for {html_path.name}")
    shutil.move(str(tmp_out), out_path)


def build_pdf(html_path, out_path, pages_app_url=None):
    """Render one HTML form to a PDF. Returns the PDF path."""
    if not html_path.exists():
        raise FileNotFoundError(f"missing form source: {html_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome()
    weasy = find_weasyprint()
    errors = []
    if chrome:
        try:
            build_pdf_with_chrome(chrome, html_path, out_path)
            return out_path
        except Exception as exc:  # fall through to weasyprint
            errors.append(f"chrome: {exc}")
    if weasy:
        try:
            build_pdf_with_weasyprint(weasy, html_path, out_path)
            return out_path
        except Exception as exc:
            errors.append(f"weasyprint: {exc}")
    if not errors:
        raise RuntimeError(
            "no PDF engine found. Install Google Chrome (happy path, see README) "
            "or weasyprint (pip install weasyprint), or both."
        )
    raise RuntimeError("all PDF engines failed:\n  " + "\n  ".join(errors))


_STREAM_RE = re.compile(rb"stream\r?\n(.*?)endstream", re.DOTALL)


def _count_pages(data):
    """Count /Type /Page objects, including ones inside compressed streams.

    Chromium/Skia and WeasyPrint both Flate-compress most object bodies, so a
    naive search of the raw bytes finds nothing. Uncompress what we can and
    search there too. Stdlib only (zlib); no PDF dependencies.
    """
    pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
    if pages >= 1:
        return pages
    for match in _STREAM_RE.finditer(data):
        raw = match.group(1)
        try:
            decompressed = zlib.decompress(raw)
        except zlib.error:
            # Sometimes there is trailing whitespace/newline padding; retry trimmed
            try:
                decompressed = zlib.decompress(raw.rstrip(b"\r\n"))
            except zlib.error:
                continue
        pages += decompressed.count(b"/Type /Page") - decompressed.count(b"/Type /Pages")
    return pages


def validate_pdf(pdf_path):
    """Validate that the given file looks like a real, >=1 page PDF."""
    data = pdf_path.read_bytes()
    if not data.startswith(b"%PDF-"):
        return f"invalid PDF magic bytes in {pdf_path.name}"
    if b"%%EOF" not in data[-2048:]:
        return f"missing %%EOF trailer at end of {pdf_path.name}"
    pages = _count_pages(data)
    if pages < 1:
        return f"no page objects found in {pdf_path.name}"
    return None


def clean_output(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in FORMS.values():
        pdf = output_dir / name
        if pdf.exists():
            pdf.unlink()
            print(f"  removed {pdf.name}")


def build_all(output_dir=DEFAULT_OUTPUT):
    """Build every form. Returns (built[pdf_path], failed[(name, error)])."""
    output_dir = Path(output_dir)
    built = []
    failed = []
    for src, dest in FORMS.items():
        html_path = FORMS_DIR / src
        out_path = output_dir / dest
        try:
            out_path = build_pdf(html_path, out_path)
            problem = validate_pdf(out_path)
            if problem:
                failed.append((dest, problem))
            else:
                built.append(out_path)
                print(f"  built  {dest}  ({out_path.stat().st_size:,} bytes)")
        except Exception as exc:
            failed.append((dest, str(exc)))
    return built, failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="remove built PDFs first")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="output dir (default: printables/)")
    args = parser.parse_args(argv)

    if args.clean:
        print("Cleaning previous builds...")
        clean_output(args.out)

    print(f"Building {len(FORMS)} forms into {args.out}/ ...")
    built, failed = build_all(args.out)

    if failed:
        for name, err in failed:
            print(f"  FAILED {name}: {err}", file=sys.stderr)
        return 1
    print(f"Done: {len(built)}/{len(FORMS)} valid PDFs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
