from job_parser import parse_job_description


def test_example_services_are_not_independent_hard_requirements():
    job_text = """
Basic Qualifications:
- 2+ years of experience building automations using
  AWS services like AWS Lambda, S3, Glue, Redshift,
  SageMaker, EventBridge and Step Functions.
- Proficiency with Python.

Preferred Qualifications:
- Experience with Tableau.
"""

    result = parse_job_description(
        job_text
    )

    assert set(
        result["required_skills"]
    ) == {
        "aws",
        "python",
    }

    assert set(
        result["preferred_skills"]
    ) == {
        "tableau",
    }


def test_parenthetical_tool_examples_are_not_all_hard_requirements():
    job_text = """
Basic Qualifications:
- AWS cloud services
  (Lambda, Glue, Redshift, S3, SageMaker, EventBridge,
  Step Functions)
- Data visualization tools
  (QuickSight, Tableau, Power BI)
- Experience with SQL and ETL.

Preferred Qualifications:
- Experience with Power BI.
"""

    result = parse_job_description(
        job_text
    )

    assert set(
        result["required_skills"]
    ) == {
        "aws",
        "sql",
        "etl",
    }

    assert set(
        result["preferred_skills"]
    ) == {
        "power bi",
    }


def test_directly_listed_required_skills_remain_required():
    job_text = """
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
"""

    result = parse_job_description(
        job_text
    )

    assert set(
        result["required_skills"]
    ) == {
        "python",
        "sql",
        "excel",
        "power bi",
    }

    assert set(
        result["preferred_skills"]
    ) == {
        "pandas",
        "tableau",
    }

    assert (
        result["minimum_experience"]
        == 2.0
    )


def test_sentence_fallback_treats_examples_conservatively():
    job_text = """
Candidates must have Python and experience with
cloud platforms such as AWS Lambda, S3 and Redshift.

Tableau would be preferred.

Minimum 2 years of experience.
"""

    result = parse_job_description(
        job_text
    )

    assert "python" in result[
        "required_skills"
    ]

    assert "aws lambda" not in result[
        "required_skills"
    ]

    assert "s3" not in result[
        "required_skills"
    ]

    assert "redshift" not in result[
        "required_skills"
    ]

    assert "tableau" in result[
        "preferred_skills"
    ]