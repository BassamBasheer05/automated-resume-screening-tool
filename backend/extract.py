import re

from ingest import read_resume
from skills import extract_skills


def extract_years_experience(resume_text):
    text = resume_text.lower()

    experience_values = []

    year_after_experience_patterns = [
        (
            r"(?:total\s+|overall\s+|professional\s+|"
            r"relevant\s+|work\s+)?"
            r"experience\s*:?\s*"
            r"(\d+(?:\.\d+)?)"
            r"\s*\+?\s*"
            r"(?:years|year|yrs|yr)\b"
        )
    ]

    year_before_experience_patterns = [
        (
            r"(\d+(?:\.\d+)?)"
            r"\s*\+?\s*"
            r"(?:years|year|yrs|yr)\b"
            r"\s+(?:of\s+)?"
            r"(?:total\s+|overall\s+|professional\s+|"
            r"relevant\s+|work\s+)?"
            r"(?:experience|exp)\b"
        )
    ]

    for pattern in (
        year_after_experience_patterns
        + year_before_experience_patterns
    ):
        matches = re.findall(
            pattern,
            text
        )

        for value in matches:
            experience_values.append(
                float(value)
            )

    month_after_experience_patterns = [
        (
            r"(?:total\s+|overall\s+|professional\s+|"
            r"relevant\s+|work\s+)?"
            r"experience\s*:?\s*"
            r"(\d+(?:\.\d+)?)"
            r"\s*"
            r"(?:months|month|mos|mo)\b"
        )
    ]

    month_before_experience_patterns = [
        (
            r"(\d+(?:\.\d+)?)"
            r"\s*"
            r"(?:months|month|mos|mo)\b"
            r"\s+(?:of\s+)?"
            r"(?:total\s+|overall\s+|professional\s+|"
            r"relevant\s+|work\s+)?"
            r"(?:experience|exp)\b"
        )
    ]

    for pattern in (
        month_after_experience_patterns
        + month_before_experience_patterns
    ):
        matches = re.findall(
            pattern,
            text
        )

        for value in matches:
            months = float(value)

            years = (
                months / 12
            )

            experience_values.append(
                years
            )

    if not experience_values:
        return 0.0

    return round(
        max(experience_values),
        2
    )


def extract_name(resume_text):
    lines = resume_text.splitlines()

    headings_to_skip = {
        "resume",
        "résumé",
        "curriculum vitae",
        "cv",
        "profile",
        "professional profile"
    }

    contact_labels = (
        "email:",
        "phone:",
        "mobile:",
        "tel:",
        "telephone:",
        "location:",
        "current location:",
        "based in:",
        "address:"
    )

    for line in lines:
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        lower_line = (
            cleaned_line.lower()
        )

        if lower_line in headings_to_skip:
            continue

        if lower_line.startswith(
            contact_labels
        ):
            continue

        if (
            lower_line.startswith("http://")
            or lower_line.startswith("https://")
            or lower_line.startswith("www.")
            or "linkedin.com/" in lower_line
            or "github.com/" in lower_line
        ):
            continue

        if "@" in cleaned_line:
            continue

        if any(
            character.isdigit()
            for character in cleaned_line
        ):
            continue

        if len(cleaned_line) > 80:
            continue

        return cleaned_line

    return "Unknown Candidate"


def extract_email(resume_text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}",
        resume_text
    )

    if match:
        return match.group(0)

    return ""


def is_valid_phone_candidate(
    value
):
    digits = re.sub(
        r"\D",
        "",
        value
    )

    return (
        9 <= len(digits) <= 15
    )


def extract_phone(resume_text):
    labelled_match = re.search(
        r"^\s*"
        r"(?:Phone|Mobile|Tel|Telephone|"
        r"WhatsApp|Contact(?:\s+Number)?)"
        r"\s*:?\s*"
        r"([+\d(][+\d\s().\-]{7,})"
        r"\s*$",
        resume_text,
        re.IGNORECASE |
        re.MULTILINE
    )

    if labelled_match:
        value = (
            labelled_match
            .group(1)
            .strip()
        )

        if is_valid_phone_candidate(
            value
        ):
            return value

    # Conservative fallback:
    # accept an unlabeled line only when
    # the entire line looks like a phone
    # number.
    for line in resume_text.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        if not re.fullmatch(
            r"[+\d(][+\d\s().\-]*",
            cleaned_line
        ):
            continue

        if is_valid_phone_candidate(
            cleaned_line
        ):
            return cleaned_line

    return ""


def extract_location(resume_text):
    match = re.search(
        r"^\s*"
        r"(?:Current\s+Location|"
        r"Location|"
        r"Based\s+in|"
        r"City)"
        r"\s*:?\s*"
        r"(.+?)"
        r"\s*$",
        resume_text,
        re.IGNORECASE |
        re.MULTILINE
    )

    if match:
        return (
            match
            .group(1)
            .strip()
        )

    # We intentionally do not guess
    # unlabeled locations yet.
    return ""


def parse_resume(resume_text):
    candidate_profile = {
        "name":
            extract_name(
                resume_text
            ),

        "email":
            extract_email(
                resume_text
            ),

        "phone":
            extract_phone(
                resume_text
            ),

        "location":
            extract_location(
                resume_text
            ),

        "skills":
            extract_skills(
                resume_text
            ),

        "years_experience":
            extract_years_experience(
                resume_text
            )
    }

    return candidate_profile


if __name__ == "__main__":
    resume_path = (
        "data/sample_resumes/"
        "alice_resume.pdf"
    )

    resume_text = read_resume(
        resume_path
    )

    candidate = parse_resume(
        resume_text
    )

    print(
        "Candidate profile:"
    )

    print(
        candidate
    )