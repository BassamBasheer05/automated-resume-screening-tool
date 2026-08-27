from job_parser import parse_job_description


def test_current_structured_format():
    job_text = """
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
    Build dashboards and reports.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "pandas",
        "tableau"
    ]

    assert job["minimum_experience"] == 2.0


def test_must_have_and_nice_to_have_headings():
    job_text = """
    Data Analyst

    Must Have:
    Python
    SQL
    Excel
    Power BI

    Nice to Have:
    Pandas
    Tableau

    Experience:
    Minimum 2 years of experience.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "pandas",
        "tableau"
    ]

    assert job["minimum_experience"] == 2.0


def test_required_and_preferred_qualifications():
    job_text = """
    Business Intelligence Analyst

    Required Qualifications:
    SQL
    Excel
    Power BI

    Preferred Qualifications:
    Tableau
    Python

    Minimum 3 years of experience
    in business intelligence.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "python",
        "tableau"
    ]

    assert job["minimum_experience"] == 3.0


def test_requirements_and_preferred_headings():
    job_text = """
    Data Analyst

    Requirements:
    Python
    SQL
    Excel
    Power BI

    Preferred:
    Pandas
    Tableau

    At least 2 years of experience
    in analytics.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "pandas",
        "tableau"
    ]

    assert job["minimum_experience"] == 2.0


def test_headings_without_colons():
    job_text = """
    Data Analyst

    Required Skills
    Python
    SQL
    Excel
    Power BI

    Preferred Skills
    Pandas
    Tableau

    Experience
    Minimum 2 years of experience.

    Responsibilities
    Analyze data.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "pandas",
        "tableau"
    ]

    assert job["minimum_experience"] == 2.0


def test_natural_sentence_style():
    job_text = """
    We are hiring a Data Analyst.

    You should have strong experience
    with Python, SQL, Excel and Power BI.

    Knowledge of Pandas and Tableau
    would be preferred.

    Candidates should have at least
    2 years of experience in analytics.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "pandas",
        "tableau"
    ]

    assert job["minimum_experience"] == 2.0


def test_what_youll_bring_and_bonus_skills():
    job_text = """
    Data Analyst

    What You'll Bring:
    Python
    SQL
    Excel
    Power BI

    Bonus Skills:
    Pandas
    Tableau

    We are looking for candidates with
    2+ years of experience.
    """

    job = parse_job_description(
        job_text
    )

    assert job["required_skills"] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job["preferred_skills"] == [
        "pandas",
        "tableau"
    ]

    assert job["minimum_experience"] == 2.0