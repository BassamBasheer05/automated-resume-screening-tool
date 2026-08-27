from extract import extract_years_experience


def test_standard_years_experience():
    text = """
    Data Analyst

    Experience:
    3 years of experience in data analysis.
    """

    assert (
        extract_years_experience(text)
        == 3.0
    )


def test_decimal_years_experience():
    text = """
    Business Analyst with
    2.5 years of professional experience.
    """

    assert (
        extract_years_experience(text)
        == 2.5
    )


def test_plus_sign_experience():
    text = """
    Software Engineer with
    4+ years of experience.
    """

    assert (
        extract_years_experience(text)
        == 4.0
    )


def test_total_experience_wins_over_role_mentions():
    text = """
    Total experience: 5 years.

    Previous role:
    2 years as a Data Analyst.

    Earlier role:
    3 years as a Reporting Analyst.
    """

    assert (
        extract_years_experience(text)
        == 5.0
    )


def test_unrelated_larger_year_number_is_ignored():
    text = """
    Data Analyst with
    3 years of professional experience.

    Contributed to a strategic
    10 years business roadmap.
    """

    assert (
        extract_years_experience(text)
        == 3.0
    )


def test_age_is_not_treated_as_experience():
    text = """
    Junior Analyst.

    The candidate is 24 years old.

    Professional experience:
    1 year.
    """

    assert (
        extract_years_experience(text)
        == 1.0
    )


def test_months_are_converted_to_years():
    text = """
    Data Analyst with
    18 months of professional experience.
    """

    assert (
        extract_years_experience(text)
        == 1.5
    )


def test_date_range_only_is_not_inferred():
    text = """
    Data Analyst

    Employment:
    January 2022 - January 2025
    """

    assert (
        extract_years_experience(text)
        == 0.0
    )


def test_job_requirement_experience_is_detected():
    text = """
    Minimum 2 years of experience
    in data analysis.
    """

    assert (
        extract_years_experience(text)
        == 2.0
    )