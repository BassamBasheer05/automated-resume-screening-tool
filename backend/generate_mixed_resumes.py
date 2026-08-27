import random
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from generate_synthetic_resumes import create_resume


OUTPUT_FOLDER = Path(
    "data/mixed_resumes"
)

RESUMES_PER_FORMAT = 10


def save_txt(resume_text, file_path):
    file_path.write_text(
        resume_text,
        encoding="utf-8"
    )


def save_docx(resume_text, file_path):
    document = Document()

    for line in resume_text.splitlines():
        document.add_paragraph(line)

    document.save(file_path)


def save_pdf(resume_text, file_path):
    pdf = canvas.Canvas(
        str(file_path),
        pagesize=letter
    )

    width, height = letter

    x_position = 50
    y_position = height - 50

    for line in resume_text.splitlines():
        if y_position < 50:
            pdf.showPage()
            y_position = height - 50

        pdf.drawString(
            x_position,
            y_position,
            line
        )

        y_position -= 15

    pdf.save()


def generate_mixed_resumes():
    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    # Remove previous test files.
    for existing_file in OUTPUT_FOLDER.iterdir():
        if existing_file.is_file():
            existing_file.unlink()

    random.seed(42)

    candidate_number = 1

    for _ in range(RESUMES_PER_FORMAT):
        resume_text = create_resume(
            candidate_number
        )

        file_path = OUTPUT_FOLDER / (
            f"candidate_{candidate_number:03d}.txt"
        )

        save_txt(
            resume_text,
            file_path
        )

        candidate_number += 1

    for _ in range(RESUMES_PER_FORMAT):
        resume_text = create_resume(
            candidate_number
        )

        file_path = OUTPUT_FOLDER / (
            f"candidate_{candidate_number:03d}.docx"
        )

        save_docx(
            resume_text,
            file_path
        )

        candidate_number += 1

    for _ in range(RESUMES_PER_FORMAT):
        resume_text = create_resume(
            candidate_number
        )

        file_path = OUTPUT_FOLDER / (
            f"candidate_{candidate_number:03d}.pdf"
        )

        save_pdf(
            resume_text,
            file_path
        )

        candidate_number += 1

    total_resumes = (
        RESUMES_PER_FORMAT * 3
    )

    print(
        f"Generated {total_resumes} "
        f"mixed-format synthetic resumes."
    )

    print(
        f"TXT: {RESUMES_PER_FORMAT}"
    )

    print(
        f"DOCX: {RESUMES_PER_FORMAT}"
    )

    print(
        f"PDF: {RESUMES_PER_FORMAT}"
    )

    print(
        f"Location: {OUTPUT_FOLDER}"
    )


if __name__ == "__main__":
    generate_mixed_resumes()