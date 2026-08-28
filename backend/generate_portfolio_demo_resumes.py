from pathlib import Path
from textwrap import wrap

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


OUTPUT_FOLDER = Path("data/portfolio_demo_resumes")


CANDIDATES = [
    {
        "name": "Aisha Mehta",
        "title": "Senior Analytics Engineer",
        "years": 7,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "Data Lakes",
            "API Integration",
            "Python",
            "UiPath",
            "RPA",
            "NLP",
            "Predictive Analytics",
            "Statistical Modeling",
            "Data Pipelines",
            "Power BI",
            "Tableau",
            "QuickSight",
            "Redshift",
            "S3",
            "AWS Lambda",
        ],
        "education": "Master of Science in Data Analytics",
    },
    {
        "name": "Dev Menon",
        "title": "Senior Data Automation Analyst",
        "years": 6,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "Data Lakes",
            "API Integration",
            "Python",
            "UiPath",
            "RPA",
            "NLP",
            "Predictive Analytics",
            "Statistical Modeling",
            "Data Pipelines",
            "Power BI",
            "QuickSight",
            "S3",
            "EventBridge",
        ],
        "education": "Bachelor of Technology in Computer Science",
    },
    {
        "name": "Kavya Rao",
        "title": "Analytics Platform Specialist",
        "years": 5,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "Data Lakes",
            "API Integration",
            "Python",
            "UiPath",
            "RPA",
            "NLP",
            "Predictive Analytics",
            "Statistical Modeling",
            "Data Pipelines",
            "Tableau",
            "Redshift",
        ],
        "education": "Master of Business Analytics",
    },
    {
        "name": "Arjun Patel",
        "title": "BI and Data Automation Analyst",
        "years": 4.5,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "Data Lakes",
            "API Integration",
            "Python",
            "UiPath",
            "RPA",
            "NLP",
            "Predictive Analytics",
            "Statistical Modeling",
            "Data Pipelines",
        ],
        "education": "Bachelor of Engineering in Information Technology",
    },
    {
        "name": "Neha Thomas",
        "title": "Senior Data Engineer",
        "years": 6,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "Data Lakes",
            "API Integration",
            "Python",
            "NLP",
            "Predictive Analytics",
            "Statistical Modeling",
            "Data Pipelines",
            "Redshift",
            "S3",
            "AWS Lambda",
            "Step Functions",
        ],
        "education": "Bachelor of Technology in Computer Science",
    },
    {
        "name": "Rohan Nair",
        "title": "Senior Business Intelligence Analyst",
        "years": 5,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "API Integration",
            "Python",
            "Predictive Analytics",
            "Statistical Modeling",
            "Power BI",
            "Tableau",
            "QuickSight",
            "Redshift",
            "S3",
        ],
        "education": "Master of Business Administration",
    },
    {
        "name": "Priya Shah",
        "title": "Machine Learning Analytics Specialist",
        "years": 5,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Modeling",
            "API Integration",
            "Python",
            "NLP",
            "Predictive Analytics",
            "Statistical Modeling",
            "Scikit-learn",
            "TensorFlow",
            "PyTorch",
            "SageMaker",
            "S3",
        ],
        "education": "Master of Science in Artificial Intelligence",
    },
    {
        "name": "Vikram Joseph",
        "title": "Cloud Data Analyst",
        "years": 4,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Warehousing",
            "Data Lakes",
            "API Integration",
            "Python",
            "Data Pipelines",
            "QuickSight",
            "Redshift",
            "S3",
            "AWS Lambda",
        ],
        "education": "Bachelor of Science in Data Science",
    },
    {
        "name": "Diya Menon",
        "title": "Automation Analytics Analyst",
        "years": 4,
        "skills": [
            "SQL",
            "ETL",
            "API Integration",
            "Python",
            "UiPath",
            "RPA",
            "Data Pipelines",
            "Power BI",
            "AWS Lambda",
        ],
        "education": "Bachelor of Technology in Information Technology",
    },
    {
        "name": "Isha Nair",
        "title": "Data Analyst",
        "years": 3.5,
        "skills": [
            "SQL",
            "ETL",
            "Data Modeling",
            "Python",
            "Predictive Analytics",
            "Statistical Modeling",
            "Power BI",
            "Tableau",
            "QuickSight",
        ],
        "education": "Bachelor of Science in Statistics",
    },
    {
        "name": "Kiran Kumar",
        "title": "Business Intelligence Developer",
        "years": 3,
        "skills": [
            "SQL",
            "ETL",
            "Data Modeling",
            "Data Warehousing",
            "Python",
            "Data Pipelines",
            "Power BI",
            "Tableau",
            "QuickSight",
        ],
        "education": "Bachelor of Computer Applications",
    },
    {
        "name": "Rahul Singh",
        "title": "Python Data Analyst",
        "years": 2.5,
        "skills": [
            "SQL",
            "API Integration",
            "Python",
            "Predictive Analytics",
            "Statistical Modeling",
            "Power BI",
            "Scikit-learn",
            "Tableau",
        ],
        "education": "Bachelor of Science in Computer Science",
    },
    {
        "name": "Meera Gupta",
        "title": "Reporting Analyst",
        "years": 3,
        "skills": [
            "SQL",
            "Data Modeling",
            "Python",
            "Statistical Modeling",
            "Power BI",
            "Tableau",
            "QuickSight",
        ],
        "education": "Bachelor of Commerce",
    },
    {
        "name": "Nikhil Rao",
        "title": "Junior Data Engineer",
        "years": 2,
        "skills": [
            "AWS",
            "SQL",
            "ETL",
            "Data Lakes",
            "Python",
            "Data Pipelines",
            "S3",
            "Redshift",
        ],
        "education": "Bachelor of Technology in Computer Science",
    },
    {
        "name": "Ananya Joseph",
        "title": "RPA Analyst",
        "years": 2.5,
        "skills": [
            "SQL",
            "API Integration",
            "Python",
            "UiPath",
            "RPA",
            "Power BI",
        ],
        "education": "Bachelor of Engineering in Electronics",
    },
    {
        "name": "Aarav Nair",
        "title": "Junior Business Analyst",
        "years": 1.5,
        "skills": [
            "SQL",
            "Python",
            "API Integration",
            "Power BI",
            "Tableau",
        ],
        "education": "Bachelor of Business Administration",
    },
    {
        "name": "Sneha Thomas",
        "title": "Graduate Data Analyst",
        "years": 1,
        "skills": [
            "SQL",
            "Python",
            "Statistical Modeling",
            "Tableau",
        ],
        "education": "Bachelor of Science in Statistics",
    },
    {
        "name": "Aditya Sharma",
        "title": "Operations Analyst",
        "years": 3,
        "skills": [
            "SQL",
            "Power BI",
            "Tableau",
        ],
        "education": "Bachelor of Commerce",
    },
]


FORMATS = [
    "txt",
    "docx",
    "pdf",
] * 6


def create_resume(candidate, candidate_number):
    skills_text = "\n".join(
        candidate["skills"]
    )

    resume_text = f"""
{candidate["name"]}
Synthetic Resume - For Portfolio Demo Purposes Only
{candidate["title"]}

Email: demo.candidate{candidate_number:02d}@example.com
Phone: 900001{candidate_number:04d}
Location: India

Professional Summary:
{candidate["title"]} with {candidate["years"]} years of experience
working across analytics, data-driven decision making,
reporting, automation, and technology-enabled business solutions.

Skills:
{skills_text}

Experience:
{candidate["title"]} with {candidate["years"]} years of experience
supporting analytics projects, business reporting,
data workflows, and stakeholder decision making.

Education:
{candidate["education"]}
""".strip()

    return resume_text


def save_txt(resume_text, file_path):
    file_path.write_text(
        resume_text,
        encoding="utf-8",
    )


def save_docx(resume_text, file_path):
    document = Document()

    for line in resume_text.splitlines():
        document.add_paragraph(line)

    document.save(file_path)


def save_pdf(resume_text, file_path):
    pdf = canvas.Canvas(
        str(file_path),
        pagesize=letter,
    )

    _, height = letter

    x_position = 50
    y_position = height - 50

    for original_line in resume_text.splitlines():
        lines = wrap(
            original_line,
            width=85,
        ) or [""]

        for line in lines:
            if y_position < 50:
                pdf.showPage()
                y_position = height - 50

            pdf.drawString(
                x_position,
                y_position,
                line,
            )

            y_position -= 15

    pdf.save()


def save_resume(
    resume_text,
    file_path,
    file_format,
):
    if file_format == "txt":
        save_txt(
            resume_text,
            file_path,
        )

    elif file_format == "docx":
        save_docx(
            resume_text,
            file_path,
        )

    elif file_format == "pdf":
        save_pdf(
            resume_text,
            file_path,
        )


def generate_portfolio_demo_resumes():
    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Remove only files from this dedicated demo folder.
    for existing_file in OUTPUT_FOLDER.iterdir():
        if existing_file.is_file():
            existing_file.unlink()

    for candidate_number, (
        candidate,
        file_format,
    ) in enumerate(
        zip(CANDIDATES, FORMATS),
        start=1,
    ):
        resume_text = create_resume(
            candidate,
            candidate_number,
        )

        safe_name = (
            candidate["name"]
            .lower()
            .replace(" ", "_")
        )

        file_name = (
            f"{safe_name}."
            f"{file_format}"
        )

        file_path = (
            OUTPUT_FOLDER / file_name
        )

        save_resume(
            resume_text,
            file_path,
            file_format,
        )

    txt_count = FORMATS.count("txt")
    docx_count = FORMATS.count("docx")
    pdf_count = FORMATS.count("pdf")

    print(
        f"Generated {len(CANDIDATES)} "
        f"portfolio demo resumes."
    )

    print(
        "All candidates are fictional "
        "and created only for demonstration."
    )

    print(
        f"TXT: {txt_count}"
    )

    print(
        f"DOCX: {docx_count}"
    )

    print(
        f"PDF: {pdf_count}"
    )

    print(
        f"Location: {OUTPUT_FOLDER}"
    )


if __name__ == "__main__":
    generate_portfolio_demo_resumes()