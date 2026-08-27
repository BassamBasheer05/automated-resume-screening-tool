from evaluate_similarity import evaluate_candidates


RULE_WEIGHT = 0.90
TEXT_SIMILARITY_WEIGHT = 0.10


RECOMMENDATION_PRIORITY = {
    "Strong Match": 4,
    "Good Match": 3,
    "Review": 2,
    "Weak Match": 1
}


def calculate_hybrid_score(candidate):
    rule_score = candidate["score"]

    text_similarity = candidate[
        "text_similarity"
    ]

    hybrid_score = (
        rule_score * RULE_WEIGHT
        + text_similarity
        * TEXT_SIMILARITY_WEIGHT
    )

    return round(
        hybrid_score,
        2
    )


def rank_with_hybrid_score(results):
    for candidate in results:
        candidate["hybrid_score"] = (
            calculate_hybrid_score(
                candidate
            )
        )

    ranked_results = sorted(
        results,
        key=lambda candidate: (
            RECOMMENDATION_PRIORITY[
                candidate["recommendation"]
            ],
            candidate["hybrid_score"],
            candidate["score"]
        ),
        reverse=True
    )

    return ranked_results


if __name__ == "__main__":
    job_path = (
        "data/sample_jobs/"
        "data_analyst_job.txt"
    )

    resume_folder = (
        "data/mixed_resumes"
    )

    results = evaluate_candidates(
        resume_folder,
        job_path
    )

    ranked_results = (
        rank_with_hybrid_score(
            results
        )
    )

    print(
        f"Candidates evaluated: "
        f"{len(ranked_results)}"
    )

    print(
        "\nHybrid Ranking Formula"
    )

    print(
        "======================"
    )

    print(
        "Rule score weight: "
        "90%"
    )

    print(
        "Text similarity weight: "
        "10%"
    )

    print(
        "\nTop 10 by Hybrid Ranking"
    )

    print(
        "========================"
    )

    for position, candidate in enumerate(
        ranked_results[:10],
        start=1
    ):
        print(
            f"\nRank #{position}"
        )

        print(
            f"Candidate: "
            f"{candidate['candidate_name']}"
        )

        print(
            f"File: "
            f"{candidate['file_name']}"
        )

        print(
            f"Rule score: "
            f"{candidate['score']}%"
        )

        print(
            f"Text similarity: "
            f"{candidate['text_similarity']}%"
        )

        print(
            f"Hybrid score: "
            f"{candidate['hybrid_score']}%"
        )

        print(
            f"Recommendation: "
            f"{candidate['recommendation']}"
        )

        print(
            f"Experience: "
            f"{candidate['candidate_experience']} "
            f"years"
        )

        print(
            f"Missing required skills: "
            f"{candidate['missing_required_skills']}"
        )