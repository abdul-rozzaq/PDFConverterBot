import subprocess
from pathlib import Path

from pdf2docx import Converter


async def convert_pdf_to_docx(input_path: str, output_path: str):
    try:
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
        return True
    except Exception as e:
        print(f"PDF to DOCX conversion error: {str(e)}")
        return False


def convert_docx_to_pdf(input_path: Path, output_path: Path) -> bool:
    try:
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(output_path.parent), str(input_path)],
            check=True,
        )
        return output_path.exists()

    except subprocess.CalledProcessError:
        return False
