from matching import match_candidate
from scoring import (
    calculate_score,
    calculate_score_breakdown,
    get_recommendation,
)


def make_job():
    return {
        "required_skills": [
            "excel",
        ],
        "required_skill_groups": [
            [
                "sql",
                "python",
            ]
        ],
        "preferred_skills": [],
        "minimum_experience": 2.0,
    }


def test_candidate_can_satisfy_or_group_with_first_option():
    candidate = {
        "skills": [
            "excel",
            "sql",
        ],
        "years_experience": 2.0,
    }

    result = match_candidate(
        candidate,
        make_job()
    )

    assert result[
        "missing_required_skills"
    ] == []

    assert result[
        "missing_required_skill_groups"
    ] == []

    assert len(
        result[
            "matched_required_skill_groups"
        ]
    ) == 1

    assert result[
        "matched_required_skill_groups"
    ][0]["matched_skills"] == [
        "sql"
    ]


def test_candidate_can_satisfy_or_group_with_second_option():
    candidate = {
        "skills": [
            "excel",
            "python",
        ],
        "years_experience": 2.0,
    }

    result = match_candidate(
        candidate,
        make_job()
    )

    assert result[
        "missing_required_skill_groups"
    ] == []

    assert result[
        "matched_required_skill_groups"
    ][0]["matched_skills"] == [
        "python"
    ]


def test_candidate_with_both_options_gets_only_one_group_credit():
    candidate = {
        "skills": [
            "excel",
            "sql",
            "python",
        ],
        "years_experience": 2.0,
    }

    job = make_job()

    result = match_candidate(
        candidate,
        job
    )

    breakdown = (
        calculate_score_breakdown(
            result,
            job
        )
    )

    assert breakdown[
        "required_skills"
    ]["matched"] == 2

    assert breakdown[
        "required_skills"
    ]["total"] == 2

    assert breakdown[
        "required_skills"
    ]["match_percentage"] == 100.0

    assert (
        calculate_score(
            result,
            job
        )
        == 100.0
    )


def test_missing_or_group_is_one_missing_requirement():
    candidate = {
        "skills": [
            "excel",
        ],
        "years_experience": 2.0,
    }

    job = make_job()

    result = match_candidate(
        candidate,
        job
    )

    assert result[
        "missing_required_skill_groups"
    ] == [
        [
            "python",
            "sql",
        ]
    ]

    breakdown = (
        calculate_score_breakdown(
            result,
            job
        )
    )

    assert breakdown[
        "required_skills"
    ]["matched"] == 1

    assert breakdown[
        "required_skills"
    ]["total"] == 2

    assert breakdown[
        "required_skills"
    ]["match_percentage"] == 50.0

    assert (
        get_recommendation(
            breakdown[
                "final_score"
            ],
            result
        )
        == "Review"
    )


def test_jobs_without_groups_remain_backward_compatible():
    job = {
        "required_skills": [
            "python",
            "sql",
        ],
        "preferred_skills": [],
        "minimum_experience": 2.0,
    }

    candidate = {
        "skills": [
            "python",
            "sql",
        ],
        "years_experience": 2.0,
    }

    result = match_candidate(
        candidate,
        job
    )

    assert result[
        "missing_required_skill_groups"
    ] == []

    assert (
        calculate_score(
            result,
            job
        )
        == 100.0
    )

    assert (
        get_recommendation(
            100.0,
            result
        )
        == "Strong Match"
    )