from extract import (
    extract_name,
    extract_email,
    extract_phone,
    extract_location
)


def run_test(
    test_name,
    resume_text
):
    print(
        f"\n{test_name}"
    )

    print(
        "=" * len(test_name)
    )

    print(
        "Name:",
        extract_name(
            resume_text
        )
    )

    print(
        "Email:",
        extract_email(
            resume_text
        )
    )

    print(
        "Phone:",
        extract_phone(
            resume_text
        )
    )

    print(
        "Location:",
        extract_location(
            resume_text
        )
    )


run_test(
    "TEST 1 - Current clean format",
    """
    Alice Sharma
    Data Analyst

    Email: alice@example.com
    Phone: 9999999999
    Location: Bengaluru, India
    """
)


run_test(
    "TEST 2 - CV heading before name",
    """
    CURRICULUM VITAE

    Rahul Gupta
    Business Analyst

    Email: rahul@example.com
    Mobile: +91 98765 43210
    Location: Mumbai, India
    """
)


run_test(
    "TEST 3 - Phone without label",
    """
    Priya Nair
    Data Analyst

    priya.nair@example.com
    +91 98765 12345
    Kochi, Kerala
    """
)


run_test(
    "TEST 4 - Different location label",
    """
    Arjun Rao
    Software Engineer

    Email: arjun@example.com
    Tel: +91-98765-43210
    Based in: Hyderabad, India
    """
)


run_test(
    "TEST 5 - LinkedIn first",
    """
    linkedin.com/in/meera-sharma

    Meera Sharma
    BI Analyst

    meera@example.com
    Phone: (987) 654-3210
    Location: Chennai
    """
)


run_test(
    "TEST 6 - Missing contact information",
    """
    Kiran Thomas
    Data Analyst

    Skills:
    Python
    SQL
    """
)