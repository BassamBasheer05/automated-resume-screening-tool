from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


JOB_TEXT = """
Data Analyst

Required Skills:
Python
SQL
Excel
Power BI

Preferred Skills:
Pandas
Tableau

Experience:
Minimum 2 years of experience.

Responsibilities:
Analyze business data.
"""


def test_health_endpoint():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_parse_job_accepts_natural_language():
    natural_job = """
    We are hiring a Data Analyst.

    You should have strong experience
    with Python, SQL, Excel and Power BI.

    Knowledge of Pandas and Tableau
    would be preferred.

    Candidates should have at least
    2 years of experience in analytics.
    """

    response = client.post(
        "/parse-job",
        json={
            "job_description":
                natural_job
        }
    )

    assert response.status_code == 200

    job = response.json()[
        "job_profile"
    ]

    assert job[
        "required_skills"
    ] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job[
        "preferred_skills"
    ] == [
        "pandas",
        "tableau"
    ]

    assert (
        job[
            "minimum_experience"
        ]
        == 2.0
    )


def test_screen_valid_resume():
    resume_content = b"""
Alice Sharma
Data Analyst

Email: alice@example.com
Phone: 9999999999
Location: Bengaluru, India

Skills:
Python
SQL
Excel
Power BI
Pandas

Experience:
3 years of experience.
"""

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "alice_resume.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "files_received"
        ]
        == 1
    )

    assert (
        data["summary"][
            "successfully_processed"
        ]
        == 1
    )

    assert (
        data["summary"]["failed"]
        == 0
    )

    candidate = (
        data[
            "ranked_candidates"
        ][0]
    )

    assert (
        candidate["candidate_name"]
        == "Alice Sharma"
    )

    assert (
        candidate["score"]
        == 92.5
    )

    assert (
        candidate["recommendation"]
        == "Strong Match"
    )

    assert (
        candidate[
            "score_breakdown"
        ][
            "final_score"
        ]
        == 92.5
    )


def test_unsupported_file_is_rejected_but_valid_resume_continues():
    resume_content = b"""
Valid Candidate

Skills:
Python
SQL
Excel
Power BI

Experience:
2 years of experience.
"""

    csv_content = (
        b"Name,Skill\n"
        b"Unsupported Candidate,Python\n"
    )

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "valid_resume.txt",
                    resume_content,
                    "text/plain"
                )
            ),
            (
                "resumes",
                (
                    "unsupported.csv",
                    csv_content,
                    "text/csv"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "files_received"
        ]
        == 2
    )

    assert (
        data["summary"][
            "supported_files"
        ]
        == 1
    )

    assert (
        data["summary"][
            "unsupported_files"
        ]
        == 1
    )

    assert (
        data[
            "rejected_files"
        ][0][
            "file_name"
        ]
        == "unsupported.csv"
    )


def test_exact_duplicate_upload_is_skipped():
    resume_content = b"""
Duplicate Candidate

Skills:
Python
SQL
Excel
Power BI

Experience:
2 years of experience.
"""

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "resume_one.txt",
                    resume_content,
                    "text/plain"
                )
            ),
            (
                "resumes",
                (
                    "resume_two.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "files_received"
        ]
        == 2
    )

    assert (
        data["summary"][
            "unique_resumes"
        ]
        == 1
    )

    assert (
        data["summary"][
            "duplicates_skipped"
        ]
        == 1
    )

    assert (
        data["summary"][
            "successfully_processed"
        ]
        == 1
    )

    assert (
        len(
            data["duplicates"]
        )
        == 1
    )


def test_broken_pdf_does_not_stop_valid_resume():
    valid_resume = b"""
Valid Candidate

Skills:
Python
SQL
Excel
Power BI
Pandas

Experience:
3 years of experience.
"""

    broken_pdf = (
        b"This is deliberately "
        b"not a real PDF file."
    )

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "valid_resume.txt",
                    valid_resume,
                    "text/plain"
                )
            ),
            (
                "resumes",
                (
                    "broken_resume.pdf",
                    broken_pdf,
                    "application/pdf"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "unique_resumes"
        ]
        == 2
    )

    assert (
        data["summary"][
            "successfully_processed"
        ]
        == 1
    )

    assert (
        data["summary"]["failed"]
        == 1
    )

    assert (
        len(
            data["ranked_candidates"]
        )
        == 1
    )

    assert (
        data["failures"][0][
            "file_name"
        ]
        == "broken_resume.pdf"
    )


def test_empty_job_description_is_rejected():
    resume_content = b"""
Test Candidate

Skills:
Python

Experience:
1 year of experience.
"""

    response = client.post(
        "/screen",
        data={
            "job_description": "   "
        },
        files=[
            (
                "resumes",
                (
                    "resume.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 400

    assert response.json()[
        "detail"
    ] == (
        "Job description cannot "
        "be empty."
    )


def test_more_than_500_resumes_is_rejected():
    files = []

    for index in range(501):
        files.append(
            (
                "resumes",
                (
                    f"resume_{index}.txt",
                    b"Test Candidate",
                    "text/plain"
                )
            )
        )

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=files
    )

    assert response.status_code == 400

    assert response.json()[
        "detail"
    ] == (
        "Maximum 500 resumes "
        "are allowed."
    )