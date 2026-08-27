from matching import match_candidate

from scoring import (
    calculate_score_breakdown,
    get_recommendation
)


def run_test(
    name,
    candidate,
    job
):
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

    print(
        f"\n{name}"
    )

    print(
        "=" * len(name)
    )

    print(
        "Required matched:",
        match_result[
            "matched_required_skills"
        ]
    )

    print(
        "Required missing:",
        match_result[
            "missing_required_skills"
        ]
    )

    print(
        "Preferred matched:",
        match_result[
            "matched_preferred_skills"
        ]
    )

    print(
        "Experience:",
        match_result[
            "candidate_experience"
        ],
        "/",
        match_result[
            "minimum_experience"
        ]
    )

    print(
        "Experience met:",
        match_result[
            "experience_met"
        ]
    )

    print(
        "Score:",
        score
    )

    print(
        "Recommendation:",
        recommendation
    )

    print(
        "Required contribution:",
        breakdown[
            "required_skills"
        ][
            "contribution_points"
        ]
    )

    print(
        "Preferred contribution:",
        breakdown[
            "preferred_skills"
        ][
            "contribution_points"
        ]
    )

    print(
        "Experience contribution:",
        breakdown[
            "experience"
        ][
            "contribution_points"
        ]
    )


candidate_all_requirements = {
    "skills": [
        "python",
        "sql",
        "excel",
        "pandas"
    ],
    "years_experience": 3.0
}


job_all_criteria = {
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


run_test(
    "TEST 1 - Normal job",
    candidate_all_requirements,
    job_all_criteria
)


job_no_preferred = {
    "required_skills": [
        "python",
        "sql",
        "excel"
    ],
    "preferred_skills": [],
    "minimum_experience": 2.0
}


run_test(
    "TEST 2 - No preferred skills",
    candidate_all_requirements,
    job_no_preferred
)


job_no_experience = {
    "required_skills": [
        "python",
        "sql",
        "excel"
    ],
    "preferred_skills": [
        "pandas",
        "tableau"
    ],
    "minimum_experience": 0.0
}


run_test(
    "TEST 3 - No experience requirement",
    candidate_all_requirements,
    job_no_experience
)


candidate_missing_required = {
    "skills": [
        "python",
        "sql",
        "pandas",
        "tableau"
    ],
    "years_experience": 3.0
}


run_test(
    "TEST 4 - Missing required skill",
    candidate_missing_required,
    job_all_criteria
)


candidate_low_experience = {
    "skills": [
        "python",
        "sql",
        "excel",
        "pandas",
        "tableau"
    ],
    "years_experience": 1.0
}


run_test(
    "TEST 5 - Experience below minimum",
    candidate_low_experience,
    job_all_criteria
)


job_no_criteria = {
    "required_skills": [],
    "preferred_skills": [],
    "minimum_experience": 0.0
}


run_test(
    "TEST 6 - No scoring criteria",
    candidate_all_requirements,
    job_no_criteria
)