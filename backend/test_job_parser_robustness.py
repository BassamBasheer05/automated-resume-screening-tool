from job_parser import parse_job_description


def run_test(
    test_name,
    job_text
):
    job = parse_job_description(
        job_text
    )

    print(
        f"\n{test_name}"
    )

    print(
        "=" * len(test_name)
    )

    print(
        "Required skills:",
        job["required_skills"]
    )

    print(
        "Preferred skills:",
        job["preferred_skills"]
    )

    print(
        "Minimum experience:",
        job["minimum_experience"]
    )


run_test(
    "TEST 1 - Current supported format",
    """
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
)


run_test(
    "TEST 2 - Must Have and Nice to Have",
    """
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

    Responsibilities:
    Build dashboards.
    """
)


run_test(
    "TEST 3 - Required Qualifications",
    """
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
)


run_test(
    "TEST 4 - Requirements heading",
    """
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
)


run_test(
    "TEST 5 - No colon after headings",
    """
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
)


run_test(
    "TEST 6 - Natural sentence style",
    """
    We are hiring a Data Analyst.

    You should have strong experience
    with Python, SQL, Excel and Power BI.

    Knowledge of Pandas and Tableau
    would be preferred.

    Candidates should have at least
    2 years of experience in analytics.
    """
)


run_test(
    "TEST 7 - What You'll Bring",
    """
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
)