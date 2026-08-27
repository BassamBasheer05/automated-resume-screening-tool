from extract import extract_years_experience


def run_test(
    test_name,
    text
):
    years = extract_years_experience(
        text
    )

    print(
        f"\n{test_name}"
    )

    print(
        "=" * len(test_name)
    )

    print(
        "Text:"
    )

    print(
        text
    )

    print(
        "\nExtracted experience:"
    )

    print(
        years
    )


run_test(
    "TEST 1 - Standard experience",
    """
    Data Analyst

    Experience:
    3 years of experience in data analysis.
    """
)


run_test(
    "TEST 2 - Decimal experience",
    """
    Business Analyst with
    2.5 years of professional experience.
    """
)


run_test(
    "TEST 3 - Plus sign",
    """
    Software Engineer with
    4+ years of experience.
    """
)


run_test(
    "TEST 4 - Multiple experience mentions",
    """
    Total experience: 5 years.

    Previous role:
    2 years as a Data Analyst.

    Earlier role:
    3 years as a Reporting Analyst.
    """
)


run_test(
    "TEST 5 - Unrelated larger number",
    """
    Data Analyst with
    3 years of professional experience.

    Contributed to a strategic
    10 years business roadmap.
    """
)


run_test(
    "TEST 6 - Age-like wording",
    """
    Junior Analyst.

    The candidate is 24 years old.

    Professional experience:
    1 year.
    """
)


run_test(
    "TEST 7 - Date range only",
    """
    Data Analyst

    Employment:
    January 2022 - January 2025
    """
)


run_test(
    "TEST 8 - Months only",
    """
    Data Analyst with
    18 months of professional experience.
    """
)


run_test(
    "TEST 9 - Job requirement wording",
    """
    Minimum 2 years of experience
    in data analysis.
    """
)