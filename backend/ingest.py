from pathlib import Path

from docx import Document
from pypdf import PdfReader


def read_txt(file_path):
    path = Path(file_path)

    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    return text


def read_pdf(file_path):
    reader = PdfReader(file_path)

    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            pages_text.append(page_text)

    return "\n".join(pages_text)


def read_docx(file_path):
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def read_resume(file_path):
    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".txt":
        return read_txt(file_path)

    elif extension == ".pdf":
        return read_pdf(file_path)

    elif extension == ".docx":
        return read_docx(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )


if __name__ == "__main__":
    resume_path = "data/sample_resumes/alice_resume.pdf"

    resume_text = read_resume(resume_path)

    print(resume_text)