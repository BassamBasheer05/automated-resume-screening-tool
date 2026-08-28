from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


JOB_TEXT = """
Basic Qualifications:
- Knowledge of SQL or Python.
- Knowledge of Excel.

Preferred Qualifications:
- Experience with Tableau.

Minimum 2 years of experience.
"""


def test_screen_returns_matched_alternative_requirement():
    resume_content = b"""
Alice Example

Skills:
Python
Excel

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
                    "alice.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 200

    candidate = response.json()[
        "ranked_candidates"
    ][0]

    assert candidate[
        "missing_required_skill_groups"
    ] == []

    assert candidate[
        "matched_required_skill_groups"
    ] == [
        {
            "options": [
                "python",
                "sql",
            ],
            "matched_skills": [
                "python",
            ],
        }
    ]

    assert candidate[
        "score_breakdown"
    ][
        "required_skills"
    ][
        "matched"
    ] == 2

    assert candidate[
        "score_breakdown"
    ][
        "required_skills"
    ][
        "total"
    ] == 2


def test_screen_returns_missing_alternative_requirement():
    resume_content = b"""
Bob Example

Skills:
Excel

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
                    "bob.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 200

    candidate = response.json()[
        "ranked_candidates"
    ][0]

    assert candidate[
        "matched_required_skill_groups"
    ] == []

    assert candidate[
        "missing_required_skill_groups"
    ] == [
        [
            "python",
            "sql",
        ]
    ]

    assert candidate[
        "recommendation"
    ] == "Review"