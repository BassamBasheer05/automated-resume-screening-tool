from matching import match_candidate


def test_required_and_preferred_skills_match():
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

    result = match_candidate(
        candidate,
        job
    )

    assert result[
        "matched_required_skills"
    ] == [
        "excel",
        "python",
        "sql"
    ]

    assert result[
        "missing_required_skills"
    ] == []

    assert result[
        "matched_preferred_skills"
    ] == [
        "pandas"
    ]

    assert result[
        "missing_preferred_skills"
    ] == [
        "tableau"
    ]


def test_missing_required_skill_is_detected():
    candidate = {
        "skills": [
            "python",
            "sql"
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

    result = match_candidate(
        candidate,
        job
    )

    assert result[
        "missing_required_skills"
    ] == [
        "excel"
    ]

    assert result[
        "matched_required_skills"
    ] == [
        "python",
        "sql"
    ]


def test_experience_requirement_is_met():
    candidate = {
        "skills": [],
        "years_experience": 2.5
    }

    job = {
        "required_skills": [],
        "preferred_skills": [],
        "minimum_experience": 2.0
    }

    result = match_candidate(
        candidate,
        job
    )

    assert (
        result[
            "candidate_experience"
        ]
        == 2.5
    )

    assert (
        result[
            "minimum_experience"
        ]
        == 2.0
    )

    assert (
        result[
            "experience_met"
        ]
        is True
    )


def test_experience_requirement_not_met():
    candidate = {
        "skills": [
            "python"
        ],
        "years_experience": 1.0
    }

    job = {
        "required_skills": [
            "python"
        ],
        "preferred_skills": [],
        "minimum_experience": 2.0
    }

    result = match_candidate(
        candidate,
        job
    )

    assert (
        result[
            "candidate_experience"
        ]
        == 1.0
    )

    assert (
        result[
            "minimum_experience"
        ]
        == 2.0
    )

    assert (
        result[
            "experience_met"
        ]
        is False
    )


def test_no_experience_requirement_is_treated_as_met():
    candidate = {
        "skills": [
            "python"
        ],
        "years_experience": 0.0
    }

    job = {
        "required_skills": [
            "python"
        ],
        "preferred_skills": [],
        "minimum_experience": 0.0
    }

    result = match_candidate(
        candidate,
        job
    )

    assert (
        result[
            "experience_met"
        ]
        is True
    )

    assert (
        result[
            "matched_required_skills"
        ]
        == [
            "python"
        ]
    )

    assert (
        result[
            "missing_required_skills"
        ]
        == []
    )