import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import PDF_DIR, TXT_DIR

try:
    from pdfminer.high_level import extract_text as _pdfminer_extract
    HAVE_PDFMINER = True
except ImportError:
    HAVE_PDFMINER = False
    print("⚠  pdfminer.six not found — run: pip install pdfminer.six")

try:
    from pypdf import PdfReader
    HAVE_PYPDF = True
except ImportError:
    HAVE_PYPDF = False
    print("pypdf not found — run: pip install pypdf")

if not HAVE_PDFMINER and not HAVE_PYPDF:
    print("No PDF library available. Install at least one:")
    print("   pip install pdfminer.six pypdf")
    sys.exit(1)


def _extract_pdfminer(path: Path) -> str:
    return _pdfminer_extract(str(path))


def _extract_pypdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            pages.append(t)
    return "\n\n".join(pages)


def _structure_handbook_text(text: str) -> str:
    """
    TUHH Specific Restructuring:
    1. Remove PDF artifacts (page numbers, references)
    2. Remove repeating global headers
    3. Force line breaks before Modules and Courses (Crucial for Chunking)
    4. Clean up mangled tables slightly
    """
    text = re.sub(r"^---\s*Page \d+\s*---\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\[\d+\]\s*$", "", text, flags=re.MULTILINE)
    
    # 2. Remove repeating global manual headers (we inject this via metadata later)
    text = re.sub(r"^Module Manual.*$", "", text, flags=re.MULTILINE)
    
    # 3. FORCE logical breaks before new modules and courses
    text = re.sub(r"(?<!\n)(?=Module\sM\d+)", "\n\n", text)
    text = re.sub(r"(?<!\n)(?=Course\sL\d+)", "\n\n", text)
    
    # 4. Add spacing before key headers so they don't get stuck to previous paragraphs
    key_headers = [
        "Module Responsible", "Admission Requirements", "Recommended Previous Knowledge",
        "Educational Objectives", "Professional Competence", "Personal Competence",
        "Workload in Hours", "Credit points", "Course achievement", "Examination",
        "Assignment for the Following Curricula", "Content", "Literature", "Typ"
    ]
    for header in key_headers:
        # If a header is glued to the end of a previous word, separate it
        text = re.sub(rf"(\S)({header})", r"\1\n\2", text)

    # 5. Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [ln.rstrip() for ln in text.splitlines()]
    return "\n".join(lines).strip()


def extract(pdf_path: Path) -> str:
    """Try pdfminer first, fall back to pypdf."""
    if HAVE_PDFMINER:
        try:
            text = _extract_pdfminer(pdf_path)
            if len(text.strip()) > 300:
                return _structure_handbook_text(text)
            print(f"pdfminer returned very little text — trying pypdf")
        except Exception as e:
            print(f"pdfminer error ({e}) — trying pypdf")

    if HAVE_PYPDF:
        return _structure_handbook_text(_extract_pypdf(pdf_path))

    raise RuntimeError("Both extractors failed.")


# ── Main ──────────────────────────────────────────────────────
def main():
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in  {PDF_DIR}")
        print(f"    Place your module handbook PDFs there and re-run.")
        return

    print(f"Found {len(pdfs)} PDF(s) in {PDF_DIR}\n")
    ok = 0

    for pdf in pdfs:
        out = TXT_DIR / (pdf.stem + ".txt")

        if out.exists():
            print(f"⏭   Skipping (already done): {pdf.name}")
            continue

        print(f"Extracting & Structuring: {pdf.name}")
        try:
            text = extract(pdf)
            out.write_text(text, encoding="utf-8")
            print(f" {out.name}  ({len(text):,} chars)")
            ok += 1
        except Exception as e:
            print(f" Failed: {e}")

    print(f"\n{'─'*50}")
    print(f"Done.  {ok} new file(s) written to {TXT_DIR}")


if __name__ == "__main__":
    main()