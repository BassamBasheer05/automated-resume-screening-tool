from skills import extract_skills


def test_extracts_data_engineering_skills():
    text = """
    Experience building ETL workflows, data models,
    data warehouses, data lakes, data pipelines,
    and API integrations.
    """

    assert set(extract_skills(text)) == {
        "etl",
        "data modeling",
        "data warehousing",
        "data lakes",
        "data pipelines",
        "api integration",
    }


def test_extracts_analytics_and_automation_skills():
    text = """
    Built predictive analytics and anomaly detection
    solutions using statistical modelling.

    Experience with natural language processing,
    UiPath RPA, Oracle and VBA.
    """

    assert set(extract_skills(text)) == {
        "nlp",
        "predictive analytics",
        "anomaly detection",
        "statistical modeling",
        "uipath",
        "rpa",
        "oracle",
        "vba",
    }


def test_extracts_aws_service_skills():
    text = """
    AWS Lambda, Amazon S3, Redshift, SageMaker,
    EventBridge and Step Functions.
    """

    skills = set(
        extract_skills(text)
    )

    assert {
        "aws",
        "aws lambda",
        "s3",
        "redshift",
        "sagemaker",
        "eventbridge",
        "step functions",
    }.issubset(skills)


def test_extracts_business_intelligence_tools():
    text = """
    Experience with QuickSight, KNIME,
    Alteryx, Tableau and Power BI.
    """

    assert set(extract_skills(text)) == {
        "power bi",
        "tableau",
        "knime",
        "alteryx",
        "quicksight",
    }


def test_extracts_common_alias_variants():
    text = """
    Worked with QuickSuite and Sage Maker.
    Built data modelling and data warehouse solutions.
    Used robotic process automation and
    natural language processing.
    """

    assert set(extract_skills(text)) == {
        "nlp",
        "data modeling",
        "data warehousing",
        "rpa",
        "quicksight",
        "sagemaker",
    }


def test_short_skill_names_do_not_match_inside_larger_words():
    text = """
    The candidate works collaboratively,
    writes detailed reports,
    coordinates digital initiatives,
    and communicates clearly.
    """

    assert extract_skills(text) == []