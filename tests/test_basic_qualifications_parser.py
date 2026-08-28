from job_parser import parse_job_description


def test_basic_qualifications_heading_and_experience_format():
    job_text = """
Business Analyst

Description:
We are seeking a Business Analyst to work with large datasets.

Basic Qualifications:
- 4+ years of relevant professional experience in business intelligence,
  analytics, statistics, data engineering, or data science.
- Knowledge of SQL or Python.
- Proficiency with Python (Mandatory).
- Knowledge of Excel.

Preferred Qualifications:
- Experience with Tableau and Power BI.
"""

    result = parse_job_description(
        job_text
    )

    assert set(
        result["required_skills"]
    ) == {
        "excel",
        "python",
    }

    # "SQL or Python" does not need to be
    # counted separately because Python is
    # independently mandatory elsewhere.
    assert (
        result["required_skill_groups"]
        == []
    )

    assert set(
        result["preferred_skills"]
    ) == {
        "power bi",
        "tableau",
    }

    assert (
        result["minimum_experience"]
        == 4.0
    )


def test_or_skills_are_stored_as_one_alternative_requirement():
    job_text = """
Basic Qualifications:
- Knowledge of SQL or Python.
- Knowledge of Excel.

Preferred Qualifications:
- Experience with Tableau.
"""

    result = parse_job_description(
        job_text
    )

    assert set(
        result["required_skills"]
    ) == {
        "excel",
    }

    assert (
        result["required_skill_groups"]
        == [
            [
                "sql",
                "python",
            ]
        ]
    )

    assert set(
        result["preferred_skills"]
    ) == {
        "tableau",
    }


def test_unrecognized_or_alternative_is_not_made_mandatory():
    job_text = """
Basic Qualifications:
- Experience with anomaly detection or defect prediction.
- Proficiency with Python.

Preferred Qualifications:
- Tableau.
"""

    result = parse_job_description(
        job_text
    )

    assert set(
        result["required_skills"]
    ) == {
        "python",
    }

    assert (
        result["required_skill_groups"]
        == []
    )

    assert "anomaly detection" not in result[
        "required_skills"
    ]