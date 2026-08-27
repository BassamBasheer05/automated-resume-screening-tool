from skills import extract_skills


def test_canonical_skills_are_detected():
    text = """
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

    skills = extract_skills(
        text
    )

    assert skills == [
        "python",
        "sql",
        "excel",
        "power bi",
        "pandas",
        "tableau",
        "docker",
        "git"
    ]


def test_common_aliases_are_normalized():
    text = """
    Technical Skills:
    PowerBI
    PostgreSQL
    Postgres
    MS Excel
    JavaScript
    JS
    sklearn
    """

    skills = extract_skills(
        text
    )

    assert skills == [
        "excel",
        "power bi",
        "scikit-learn",
        "javascript",
        "postgresql"
    ]


def test_false_positive_words_are_not_skills():
    text = """
    Excellent communicator with
    experience in digital reporting.

    The analyst draws insights
    from NoSQL systems.
    """

    skills = extract_skills(
        text
    )

    assert skills == []


def test_formatting_variations_are_normalized():
    text = """
    Skills:
    Power-BI
    scikit learn
    machine-learning
    """

    skills = extract_skills(
        text
    )

    assert skills == [
        "power bi",
        "machine learning",
        "scikit-learn"
    ]


def test_skill_matching_is_case_insensitive():
    text = """
    PYTHON
    Sql
    POWER BI
    PaNdAs
    TABLEAU
    """

    skills = extract_skills(
        text
    )

    assert skills == [
        "python",
        "sql",
        "power bi",
        "pandas",
        "tableau"
    ]