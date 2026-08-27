from extract import (
    extract_name,
    extract_email,
    extract_phone,
    extract_location
)


def test_clean_contact_format():
    text = """
    Alice Sharma
    Data Analyst

    Email: alice@example.com
    Phone: 9999999999
    Location: Bengaluru, India
    """

    assert extract_name(text) == "Alice Sharma"
    assert extract_email(text) == "alice@example.com"
    assert extract_phone(text) == "9999999999"

    assert (
        extract_location(text)
        == "Bengaluru, India"
    )


def test_cv_heading_is_not_used_as_name():
    text = """
    CURRICULUM VITAE

    Rahul Gupta
    Business Analyst

    Email: rahul@example.com
    Mobile: +91 98765 43210
    Location: Mumbai, India
    """

    assert extract_name(text) == "Rahul Gupta"
    assert extract_email(text) == "rahul@example.com"

    assert (
        extract_phone(text)
        == "+91 98765 43210"
    )

    assert (
        extract_location(text)
        == "Mumbai, India"
    )


def test_unlabelled_phone_is_detected():
    text = """
    Priya Nair
    Data Analyst

    priya.nair@example.com
    +91 98765 12345
    Kochi, Kerala
    """

    assert extract_name(text) == "Priya Nair"

    assert (
        extract_email(text)
        == "priya.nair@example.com"
    )

    assert (
        extract_phone(text)
        == "+91 98765 12345"
    )

    # Conservative behavior:
    # unlabeled locations are not guessed.
    assert extract_location(text) == ""


def test_based_in_location_is_detected():
    text = """
    Arjun Rao
    Software Engineer

    Email: arjun@example.com
    Tel: +91-98765-43210
    Based in: Hyderabad, India
    """

    assert extract_name(text) == "Arjun Rao"

    assert (
        extract_phone(text)
        == "+91-98765-43210"
    )

    assert (
        extract_location(text)
        == "Hyderabad, India"
    )


def test_linkedin_is_not_used_as_name():
    text = """
    linkedin.com/in/meera-sharma

    Meera Sharma
    BI Analyst

    meera@example.com
    Phone: (987) 654-3210
    Location: Chennai
    """

    assert extract_name(text) == "Meera Sharma"

    assert (
        extract_email(text)
        == "meera@example.com"
    )

    assert (
        extract_phone(text)
        == "(987) 654-3210"
    )

    assert extract_location(text) == "Chennai"


def test_missing_contact_information_is_safe():
    text = """
    Kiran Thomas
    Data Analyst

    Skills:
    Python
    SQL
    """

    assert extract_name(text) == "Kiran Thomas"
    assert extract_email(text) == ""
    assert extract_phone(text) == ""
    assert extract_location(text) == ""