from ingest import read_resume
from job_parser import parse_job_description
from ranking import find_resume_files, screen_candidate
from similarity import calculate_text_similarity


def evaluate_candidates(
    resume_folder,
    job_path
):
    job_text = read_resume(
        job_path
    )

    job = parse_job_description(
        job_text
    )

    resume_paths = find_resume_files(
        resume_folder
    )

    results = []

    for resume_path in resume_paths:
        resume_text = read_resume(
            resume_path
        )

        candidate = screen_candidate(
            resume_path,
            job
        )

        similarity_score = (
            calculate_text_similarity(
                resume_text,
                job_text
            )
        )

        candidate[
            "text_similarity"
        ] = similarity_score

        results.append(candidate)

    return results


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

    similarity_ranked = sorted(
        results,
        key=lambda candidate:
            candidate["text_similarity"],
        reverse=True
    )

    print(
        f"Candidates evaluated: "
        f"{len(similarity_ranked)}"
    )

    print(
        "\nTop 10 by Text Similarity"
    )

    print(
        "========================="
    )

    for position, candidate in enumerate(
        similarity_ranked[:10],
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
            f"Text similarity: "
            f"{candidate['text_similarity']}%"
        )

        print(
            f"Rule score: "
            f"{candidate['score']}%"
        )

        print(
            f"Recommendation: "
            f"{candidate['recommendation']}"
        )

        print(
            f"Missing required skills: "
            f"{candidate['missing_required_skills']}"
        )

    print(
        "\nBottom 5 by Text Similarity"
    )

    print(
        "==========================="
    )

    bottom_candidates = sorted(
        results,
        key=lambda candidate:
            candidate["text_similarity"]
    )[:5]

    for candidate in bottom_candidates:
        print(
            f"\nCandidate: "
            f"{candidate['candidate_name']}"
        )

        print(
            f"Text similarity: "
            f"{candidate['text_similarity']}%"
        )

        print(
            f"Rule score: "
            f"{candidate['score']}%"
        )

        print(
            f"Recommendation: "
            f"{candidate['recommendation']}"
        )

        print(
            f"Missing required skills: "
            f"{candidate['missing_required_skills']}"
        )