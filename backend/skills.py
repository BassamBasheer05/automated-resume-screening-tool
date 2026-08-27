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
    ],

    "etl": [
        "etl",
        "extract transform load"
    ],

    "nlp": [
        "nlp",
        "natural language processing"
    ],

"data modeling": [
    "data modeling",
    "data modelling",
    "data model",
    "data models"
],

    "data warehousing": [
        "data warehousing",
        "data warehouse",
        "data warehouses"
    ],

    "data lakes": [
        "data lake",
        "data lakes"
    ],

    "data pipelines": [
        "data pipeline",
        "data pipelines",
        "data pipeline development"
    ],

    "api integration": [
        "api integration",
        "api integrations",
        "application programming interface integration",
        "application programming interface integrations"
    ],

    "predictive analytics": [
        "predictive analytics",
        "predictive modeling",
        "predictive modelling"
    ],

    "anomaly detection": [
        "anomaly detection"
    ],

    "statistical modeling": [
        "statistical modeling",
        "statistical modelling"
    ],

    "uipath": [
        "uipath",
        "ui path"
    ],

    "rpa": [
        "rpa",
        "robotic process automation"
    ],

    "oracle": [
        "oracle"
    ],

    "vba": [
        "vba",
        "visual basic for applications"
    ],

    "knime": [
        "knime"
    ],

    "alteryx": [
        "alteryx"
    ],

    "spark": [
        "apache spark",
        "spark"
    ],

    "scala": [
        "scala"
    ],

    "quicksight": [
        "quicksight",
        "quick sight",
        "amazon quicksight",
        "aws quicksight",
        "quicksuite",
        "quick suite"
    ],

    "aws lambda": [
        "aws lambda",
        "amazon lambda",
        "lambda"
    ],

    "aws glue": [
        "aws glue",
        "amazon glue"
    ],

    "redshift": [
        "redshift",
        "amazon redshift",
        "aws redshift"
    ],

    "s3": [
        "s3",
        "amazon s3",
        "aws s3"
    ],

    "sagemaker": [
        "sagemaker",
        "sage maker",
        "amazon sagemaker",
        "aws sagemaker"
    ],

    "eventbridge": [
        "eventbridge",
        "event bridge",
        "amazon eventbridge",
        "aws eventbridge"
    ],

    "step functions": [
        "step functions",
        "step function",
        "aws step functions",
        "aws step function"
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