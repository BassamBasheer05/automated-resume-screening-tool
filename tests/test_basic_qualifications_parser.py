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

    result = parse_job_description(job_text)

    assert set(result["required_skills"]) == {
        "excel",
        "python",
        "sql",
    }

    assert set(result["preferred_skills"]) == {
        "power bi",
        "tableau",
    }

    assert result["minimum_experience"] == 4.0