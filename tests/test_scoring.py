from matching import match_candidate

from scoring import (
    calculate_score_breakdown,
    get_recommendation
)


def test_normal_strong_match():
    candidate = {
        "skills": [
            "python",
            "sql",
            "excel",
            "pandas"
        ],
        "years_experience": 3.0
    }

    job = {
        "required_skills": [
            "python",
            "sql",
            "excel"
        ],
        "preferred_skills": [
            "pandas",
            "tableau"
        ],
        "minimum_experience": 2.0
    }

    match_result = match_candidate(
        candidate,
        job
    )

    breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    score = breakdown[
        "final_score"
    ]

    recommendation = (
        get_recommendation(
            score,
            match_result
        )
    )

    assert score == 92.5
    assert recommendation == "Strong Match"

    assert (
        breakdown[
            "required_skills"
        ][
            "contribution_points"
        ]
        == 60.0
    )

    assert (
        breakdown[
            "preferred_skills"
        ][
            "contribution_points"
        ]
        == 7.5
    )

    assert (
        breakdown[
            "experience"
        ][
            "contribution_points"
        ]
        == 25.0
    )


def test_missing_required_skill_forces_review():
    candidate = {
        "skills": [
            "python",
            "sql",
            "pandas",
            "tableau"
        ],
        "years_experience": 3.0
    }

    job = {
        "required_skills": [
            "python",
            "sql",
            "excel"
        ],
        "preferred_skills": [
            "pandas",
            "tableau"
        ],
        "minimum_experience": 2.0
    }

    match_result = match_candidate(
        candidate,
        job
    )

    breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    score = breakdown[
        "final_score"
    ]

    recommendation = (
        get_recommendation(
            score,
            match_result
        )
    )

    assert score == 80.0

    assert (
        match_result[
            "missing_required_skills"
        ]
        == ["excel"]
    )

    assert recommendation == "Review"


def test_low_experience_forces_review():
    candidate = {
        "skills": [
            "python",
            "sql",
            "excel",
            "pandas",
            "tableau"
        ],
        "years_experience": 1.0
    }

    job = {
        "required_skills": [
            "python",
            "sql",
            "excel"
        ],
        "preferred_skills": [
            "pandas",
            "tableau"
        ],
        "minimum_experience": 2.0
    }

    match_result = match_candidate(
        candidate,
        job
    )

    breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    score = breakdown[
        "final_score"
    ]

    recommendation = (
        get_recommendation(
            score,
            match_result
        )
    )

    assert score == 87.5
    assert match_result["experience_met"] is False
    assert recommendation == "Review"


def test_no_preferred_skills_normalizes_weights():
    candidate = {
        "skills": [
            "python",
            "sql",
            "excel"
        ],
        "years_experience": 3.0
    }

    job = {
        "required_skills": [
            "python",
            "sql",
            "excel"
        ],
        "preferred_skills": [],
        "minimum_experience": 2.0
    }

    match_result = match_candidate(
        candidate,
        job
    )

    breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    assert breakdown["final_score"] == 100.0

    assert (
        breakdown[
            "required_skills"
        ][
            "weight_percentage"
        ]
        == 70.59
    )

    assert (
        breakdown[
            "preferred_skills"
        ][
            "weight_percentage"
        ]
        == 0.0
    )

    assert (
        breakdown[
            "experience"
        ][
            "weight_percentage"
        ]
        == 29.41
    )


def test_no_scoring_criteria_returns_zero():
    candidate = {
        "skills": [
            "python",
            "sql"
        ],
        "years_experience": 3.0
    }

    job = {
        "required_skills": [],
        "preferred_skills": [],
        "minimum_experience": 0.0
    }

    match_result = match_candidate(
        candidate,
        job
    )

    breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    score = breakdown[
        "final_score"
    ]

    recommendation = (
        get_recommendation(
            score,
            match_result
        )
    )

    assert score == 0.0
    assert recommendation == "Weak Match"