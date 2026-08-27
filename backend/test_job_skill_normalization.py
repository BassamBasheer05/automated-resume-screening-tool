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
    "TEST 1 - Canonical wording",
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
    Build dashboards.
    """
)


run_test(
    "TEST 2 - Alias wording",
    """
    Data Analyst

    Required Skills:
    PowerBI
    MS Excel
    PostgreSQL

    Preferred Skills:
    sklearn
    JavaScript

    Experience:
    Minimum 3 years of experience.

    Responsibilities:
    Analyze business data.
    """
)


run_test(
    "TEST 3 - Formatting variations",
    """
    Machine Learning Analyst

    Required Skills:
    Power-BI
    machine-learning
    scikit learn

    Preferred Skills:
    Amazon Web Services

    Experience:
    2+ years of experience.

    Responsibilities:
    Build machine learning solutions.
    """
)


run_test(
    "TEST 4 - False-positive wording",
    """
    Analyst

    Required Skills:
    Excellent communication
    Digital reporting

    Preferred Skills:
    Draws business insights
    NoSQL knowledge

    Experience:
    Minimum 1 year of experience.

    Responsibilities:
    Work with stakeholders.
    """
)