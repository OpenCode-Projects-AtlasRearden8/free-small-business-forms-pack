"""Tests for the Free Small-Business Forms Pack.

Verifies that every form source exists and that the build produces a valid PDF
for each form. Run with either:

    python3 -m unittest discover -s tests -v
    pytest tests/
"""

import tempfile
import unittest
from pathlib import Path

import build

ROOT = Path(build.__file__).resolve().parent
MIN_PDF_BYTES = 1000


def _read(path):
    return path.read_bytes()


class SourceTests(unittest.TestCase):
    """Form sources that the pack promises actually exist and are wired up."""

    def test_all_form_sources_exist(self):
        missing = [src for src in build.FORMS if not (build.FORMS_DIR / src).exists()]
        self.assertEqual(missing, [], f"missing form sources: {missing}")

    def test_each_form_links_shared_stylesheet(self):
        for src in build.FORMS:
            html = (build.FORMS_DIR / src).read_text(encoding="utf-8")
            self.assertIn("assets/print.css", html, f"{src} does not link the shared stylesheet")

    def test_expected_output_names_are_unique(self):
        names = list(build.FORMS.values())
        self.assertEqual(len(names), len(set(names)), "duplicate PDF output names")
        for name in names:
            self.assertTrue(name.endswith(".pdf"), f"bad output name: {name}")


class BuildTests(unittest.TestCase):
    """Every form builds a real, valid PDF into a fresh output directory."""

    def test_build_all_forms_produce_valid_pdfs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            built, failed = build.build_all(out_dir)
            self.assertEqual(
                failed,
                [],
                f"build failures: {failed}",
            )
            self.assertEqual(len(built), len(build.FORMS))

            for pdf in built:
                with self.subTest(pdf=pdf.name):
                    self.assertTrue(pdf.exists())
                    size = pdf.stat().st_size
                    self.assertGreaterEqual(size, MIN_PDF_BYTES, f"{pdf.name} suspiciously small")

                    data = _read(pdf)
                    self.assertTrue(data.startswith(b"%PDF-"), f"{pdf.name}: no %PDF magic")
                    self.assertIn(b"%%EOF", data[-2048:], f"{pdf.name}: no EOF trailer")
                    page_count = build._count_pages(data)
                    self.assertGreaterEqual(
                        page_count, 1, f"{pdf.name}: no page objects detected"
                    )

    def test_printables_directory_has_all_pdfs_after_default_build(self):
        """The committed printables/ folder is complete (i.e., `python3 build.py` was run)."""
        pdfs = [build.DEFAULT_OUTPUT / name for name in build.FORMS.values()]
        missing = [p.name for p in pdfs if not p.exists()]
        self.assertEqual(
            missing,
            [],
            "printables/ is missing built PDFs — run `python3 build.py`",
        )

    def test_validation_rejects_non_pdfs(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "fake.pdf"
            fake.write_text("this is just a text file pretending to be a pdf, %PDF? no.")
            problem = build.validate_pdf(fake)
            self.assertIsNotNone(problem)
            self.assertIn("invalid PDF magic bytes", problem)

    def test_validation_rejects_pdf_missing_pages(self):
        """A file with a PDF header but no page objects is invalid."""
        with tempfile.TemporaryDirectory() as tmp:
            header_only = Path(tmp) / "header-only.pdf"
            header_only.write_bytes(b"%PDF-1.4\n%%EOF\n")
            self.assertIsNotNone(build.validate_pdf(header_only))


if __name__ == "__main__":
    unittest.main()
