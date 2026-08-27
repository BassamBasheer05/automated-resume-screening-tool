REQUIRED_WEIGHT = 0.60
PREFERRED_WEIGHT = 0.15
EXPERIENCE_WEIGHT = 0.25


def calculate_score_breakdown(
    match_result,
    job
):
    total_required = len(
        job["required_skills"]
    )

    total_preferred = len(
        job["preferred_skills"]
    )

    matched_required = len(
        match_result[
            "matched_required_skills"
        ]
    )

    matched_preferred = len(
        match_result[
            "matched_preferred_skills"
        ]
    )

    candidate_experience = (
        match_result[
            "candidate_experience"
        ]
    )

    minimum_experience = (
        match_result[
            "minimum_experience"
        ]
    )

    active_weight = 0.0

    if total_required > 0:
        active_weight += REQUIRED_WEIGHT

    if total_preferred > 0:
        active_weight += PREFERRED_WEIGHT

    if minimum_experience > 0:
        active_weight += EXPERIENCE_WEIGHT

    # If the job parser found no usable
    # scoring criteria, return a zero score.
    if active_weight == 0:
        return {
            "required_skills": {
                "matched": matched_required,
                "total": total_required,
                "match_percentage": 0.0,
                "weight_percentage": 0.0,
                "contribution_points": 0.0
            },

            "preferred_skills": {
                "matched": matched_preferred,
                "total": total_preferred,
                "match_percentage": 0.0,
                "weight_percentage": 0.0,
                "contribution_points": 0.0
            },

            "experience": {
                "candidate_years":
                    candidate_experience,

                "minimum_years":
                    minimum_experience,

                "match_percentage":
                    0.0,

                "weight_percentage":
                    0.0,

                "contribution_points":
                    0.0
            },

            "final_score": 0.0
        }

    required_match_score = 0.0
    required_effective_weight = 0.0
    required_points = 0.0

    if total_required > 0:
        required_match_score = (
            matched_required
            / total_required
        )

        required_effective_weight = (
            REQUIRED_WEIGHT
            / active_weight
        )

        required_points = (
            required_match_score
            * required_effective_weight
            * 100
        )

    preferred_match_score = 0.0
    preferred_effective_weight = 0.0
    preferred_points = 0.0

    if total_preferred > 0:
        preferred_match_score = (
            matched_preferred
            / total_preferred
        )

        preferred_effective_weight = (
            PREFERRED_WEIGHT
            / active_weight
        )

        preferred_points = (
            preferred_match_score
            * preferred_effective_weight
            * 100
        )

    experience_match_score = 0.0
    experience_effective_weight = 0.0
    experience_points = 0.0

    if minimum_experience > 0:
        experience_match_score = min(
            candidate_experience
            / minimum_experience,
            1.0
        )

        experience_effective_weight = (
            EXPERIENCE_WEIGHT
            / active_weight
        )

        experience_points = (
            experience_match_score
            * experience_effective_weight
            * 100
        )

    final_score = (
        required_points
        + preferred_points
        + experience_points
    )

    breakdown = {
        "required_skills": {
            "matched":
                matched_required,

            "total":
                total_required,

            "match_percentage":
                round(
                    required_match_score
                    * 100,
                    2
                ),

            "weight_percentage":
                round(
                    required_effective_weight
                    * 100,
                    2
                ),

            "contribution_points":
                round(
                    required_points,
                    2
                )
        },

        "preferred_skills": {
            "matched":
                matched_preferred,

            "total":
                total_preferred,

            "match_percentage":
                round(
                    preferred_match_score
                    * 100,
                    2
                ),

            "weight_percentage":
                round(
                    preferred_effective_weight
                    * 100,
                    2
                ),

            "contribution_points":
                round(
                    preferred_points,
                    2
                )
        },

        "experience": {
            "candidate_years":
                candidate_experience,

            "minimum_years":
                minimum_experience,

            "match_percentage":
                round(
                    experience_match_score
                    * 100,
                    2
                ),

            "weight_percentage":
                round(
                    experience_effective_weight
                    * 100,
                    2
                ),

            "contribution_points":
                round(
                    experience_points,
                    2
                )
        },

        "final_score":
            round(
                final_score,
                2
            )
    }

    return breakdown


def calculate_score(
    match_result,
    job
):
    breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    return breakdown[
        "final_score"
    ]


def get_recommendation(
    score,
    match_result
):
    missing_required = (
        match_result[
            "missing_required_skills"
        ]
    )

    experience_met = (
        match_result[
            "experience_met"
        ]
    )

    # Missing a minimum requirement prevents
    # automatic Strong Match or Good Match.
    if (
        missing_required
        or not experience_met
    ):
        if score >= 50:
            return "Review"
        else:
            return "Weak Match"

    # Candidate satisfies all minimum
    # job requirements.
    if score >= 90:
        return "Strong Match"

    elif score >= 85:
        return "Good Match"

    elif score >= 50:
        return "Review"

    else:
        return "Weak Match"