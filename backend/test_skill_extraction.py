from extract import extract_skills


def run_test(
    test_name,
    resume_text
):
    skills = extract_skills(
        resume_text
    )

    print(
        f"\n{test_name}"
    )

    print(
        "=" * len(test_name)
    )

    print(
        "Resume text:"
    )

    print(
        resume_text
    )

    print(
        "\nDetected skills:"
    )

    print(
        skills
    )


run_test(
    "TEST 1 - Normal canonical skills",
    """
    Data Analyst

    Skills:
    Python
    SQL
    Excel
    Power BI
    Pandas
    Tableau
    Docker
    Git
    """
)


run_test(
    "TEST 2 - Common skill aliases",
    """
    Technical Skills:
    PowerBI
    PostgreSQL
    Postgres
    MS Excel
    JavaScript
    JS
    sklearn
    """
)


run_test(
    "TEST 3 - False-positive words",
    """
    Excellent communicator with
    experience in digital reporting.

    The analyst draws insights from
    NoSQL systems.
    """
)


run_test(
    "TEST 4 - Formatting variations",
    """
    Skills include:

    Power-BI
    scikit learn
    machine-learning
    """
)


run_test(
    "TEST 5 - Capitalization",
    """
    PYTHON
    Sql
    POWER BI
    PaNdAs
    TABLEAU
    """
)