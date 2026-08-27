import re


SKILL_ALIASES = {
    "python": [
        "python"
    ],

    "sql": [
        "sql",
        "structured query language"
    ],

    "excel": [
        "excel",
        "ms excel",
        "microsoft excel"
    ],

    "power bi": [
        "power bi",
        "powerbi",
        "microsoft power bi"
    ],

    "pandas": [
        "pandas"
    ],

    "numpy": [
        "numpy"
    ],

    "data analysis": [
        "data analysis"
    ],

    "tableau": [
        "tableau"
    ],

    "machine learning": [
        "machine learning"
    ],

    "scikit-learn": [
        "scikit learn",
        "sklearn"
    ],

    "tensorflow": [
        "tensorflow",
        "tensor flow"
    ],

    "pytorch": [
        "pytorch"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": [
        "azure",
        "microsoft azure"
    ],

    "docker": [
        "docker"
    ],

    "git": [
        "git"
    ],

    "javascript": [
        "javascript",
        "java script",
        "js"
    ],

    "postgresql": [
        "postgresql",
        "postgres",
        "postgre sql"
    ]
}


def normalize_text(text):
    normalized = text.lower()

    normalized = re.sub(
        r"[-_/]+",
        " ",
        normalized
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    return normalized.strip()


def contains_alias(
    normalized_text,
    alias
):
    normalized_alias = normalize_text(
        alias
    )

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(
            normalized_alias
        )
        + r"(?![a-z0-9])"
    )

    return (
        re.search(
            pattern,
            normalized_text
        )
        is not None
    )


def extract_skills(text):
    normalized_text = normalize_text(
        text
    )

    found_skills = []

    for (
        canonical_skill,
        aliases
    ) in SKILL_ALIASES.items():

        for alias in aliases:

            if contains_alias(
                normalized_text,
                alias
            ):
                found_skills.append(
                    canonical_skill
                )

                break

    return found_skills