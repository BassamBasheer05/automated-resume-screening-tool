import hashlib
import time
from pathlib import Path

from ingest import read_resume
from extract import parse_resume
from job_parser import parse_job_description
from matching import match_candidate
from scoring import (
    calculate_score_breakdown,
    get_recommendation
)
from similarity import calculate_text_similarity


def find_resume_files(resume_folder):
    folder = Path(resume_folder)

    supported_extensions = {
        ".txt",
        ".pdf",
        ".docx"
    }

    resume_files = []

    for file_path in folder.iterdir():
        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in supported_extensions
        ):
            resume_files.append(
                str(file_path)
            )

    return resume_files


def calculate_file_hash(file_path):
    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


def remove_duplicate_files(resume_paths):
    unique_files = []
    duplicates = []

    seen_hashes = {}

    for resume_path in resume_paths:
        file_hash = calculate_file_hash(
            resume_path
        )

        if file_hash in seen_hashes:
            duplicate = {
                "file_name":
                    Path(resume_path).name,

                "duplicate_of":
                    Path(
                        seen_hashes[file_hash]
                    ).name
            }

            duplicates.append(
                duplicate
            )

        else:
            seen_hashes[
                file_hash
            ] = resume_path

            unique_files.append(
                resume_path
            )

    return unique_files, duplicates


def screen_candidate(
    resume_path,
    job,
    job_text=None
):
    resume_text = read_resume(
        resume_path
    )

    candidate = parse_resume(
        resume_text
    )

    match_result = match_candidate(
        candidate,
        job
    )

    score_breakdown = (
        calculate_score_breakdown(
            match_result,
            job
        )
    )

    score = score_breakdown[
        "final_score"
    ]

    recommendation = get_recommendation(
        score,
        match_result
    )

    text_similarity = None

    if job_text is not None:
        text_similarity = (
            calculate_text_similarity(
                resume_text,
                job_text
            )
        )

    result = {
        "candidate_name":
            candidate["name"],

        "email":
            candidate["email"],

        "phone":
            candidate["phone"],

        "location":
            candidate["location"],

        "file_name":
            Path(resume_path).name,

        "score":
            score,

        "score_breakdown":
            score_breakdown,

        "text_similarity":
            text_similarity,

        "recommendation":
            recommendation,

        "matched_required_skills":
            match_result[
                "matched_required_skills"
            ],

        "missing_required_skills":
            match_result[
                "missing_required_skills"
            ],

        "matched_preferred_skills":
            match_result[
                "matched_preferred_skills"
            ],

        "candidate_experience":
            match_result[
                "candidate_experience"
            ],

        "experience_met":
            match_result[
                "experience_met"
            ]
    }

    return result


def rank_candidates(
    resume_paths,
    job,
    job_text
):
    results = []
    failures = []

    total_resumes = len(
        resume_paths
    )

    batch_start_time = (
        time.perf_counter()
    )

    for index, resume_path in enumerate(
        resume_paths,
        start=1
    ):
        file_name = Path(
            resume_path
        ).name

        resume_start_time = (
            time.perf_counter()
        )

        try:
            result = screen_candidate(
                resume_path,
                job,
                job_text
            )

            resume_time = (
                time.perf_counter()
                - resume_start_time
            )

            result[
                "processing_seconds"
            ] = round(
                resume_time,
                6
            )

            results.append(
                result
            )

        except Exception as error:
            resume_time = (
                time.perf_counter()
                - resume_start_time
            )

            failure = {
                "file_name":
                    file_name,

                "error":
                    str(error),

                "processing_seconds":
                    round(
                        resume_time,
                        6
                    )
            }

            failures.append(
                failure
            )

        if (
            index % 10 == 0
            or index == total_resumes
        ):
            print(
                f"Processed "
                f"{index}/{total_resumes}"
            )

    total_time = (
        time.perf_counter()
        - batch_start_time
    )

    if total_resumes > 0:
        average_time = (
            total_time
            / total_resumes
        )
    else:
        average_time = 0.0

    recommendation_priority = {
        "Strong Match": 4,
        "Good Match": 3,
        "Review": 2,
        "Weak Match": 1
    }

    ranked_results = sorted(
        results,
        key=lambda candidate: (
            recommendation_priority[
                candidate["recommendation"]
            ],
            candidate["score"],
            candidate["text_similarity"]
            if candidate["text_similarity"]
            is not None
            else 0.0
        ),
        reverse=True
    )

    statistics = {
        "total_resumes":
            total_resumes,

        "successful":
            len(results),

        "failed":
            len(failures),

        "total_seconds":
            round(
                total_time,
                6
            ),

        "average_seconds_per_resume":
            round(
                average_time,
                6
            )
    }

    return (
        ranked_results,
        failures,
        statistics
    )


def count_recommendations(
    rankings
):
    counts = {
        "Strong Match": 0,
        "Good Match": 0,
        "Review": 0,
        "Weak Match": 0
    }

    for candidate in rankings:
        recommendation = (
            candidate[
                "recommendation"
            ]
        )

        if recommendation in counts:
            counts[
                recommendation
            ] += 1

    return counts


if __name__ == "__main__":
    job_path = (
        "data/sample_jobs/"
        "data_analyst_job.txt"
    )

    resume_folder = (
        "data/mixed_resumes"
    )

    resume_paths = (
        find_resume_files(
            resume_folder
        )
    )

    print(
        f"Resume files discovered: "
        f"{len(resume_paths)}"
    )

    unique_resume_paths, duplicates = (
        remove_duplicate_files(
            resume_paths
        )
    )

    print(
        f"Unique resumes to screen: "
        f"{len(unique_resume_paths)}"
    )

    print(
        f"Exact duplicates skipped: "
        f"{len(duplicates)}"
    )

    job_text = read_resume(
        job_path
    )

    job = parse_job_description(
        job_text
    )

    print(
        "\nStarting resume screening...\n"
    )

    rankings, failures, statistics = (
        rank_candidates(
            unique_resume_paths,
            job,
            job_text
        )
    )

    recommendation_counts = (
        count_recommendations(
            rankings
        )
    )

    print(
        "\nScreening Summary"
    )

    print(
        "================="
    )

    print(
        f"Files discovered: "
        f"{len(resume_paths)}"
    )

    print(
        f"Duplicate files skipped: "
        f"{len(duplicates)}"
    )

    print(
        f"Successfully processed: "
        f"{statistics['successful']}"
    )

    print(
        f"Failed: "
        f"{statistics['failed']}"
    )

    print(
        f"Total processing time: "
        f"{statistics['total_seconds']} "
        f"seconds"
    )

    print(
        f"Average time per resume: "
        f"{statistics['average_seconds_per_resume']} "
        f"seconds"
    )

    print(
        "\nRecommendation Summary"
    )

    print(
        "======================"
    )

    print(
        f"Strong Match: "
        f"{recommendation_counts['Strong Match']}"
    )

    print(
        f"Good Match: "
        f"{recommendation_counts['Good Match']}"
    )

    print(
        f"Review: "
        f"{recommendation_counts['Review']}"
    )

    print(
        f"Weak Match: "
        f"{recommendation_counts['Weak Match']}"
    )

    print(
        "\nTop 10 Candidates"
    )

    print(
        "================="
    )

    top_candidates = (
        rankings[:10]
    )

    for position, candidate in enumerate(
        top_candidates,
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
            f"Email: "
            f"{candidate['email']}"
        )

        print(
            f"Location: "
            f"{candidate['location']}"
        )

        print(
            f"File: "
            f"{candidate['file_name']}"
        )

        print(
            f"Match score: "
            f"{candidate['score']}%"
        )

        print(
            f"Text relevance: "
            f"{candidate['text_similarity']}%"
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

        breakdown = candidate[
            "score_breakdown"
        ]

        print(
            "Score breakdown:"
        )

        print(
            f"  Required skills: "
            f"{breakdown['required_skills']['matched']}"
            f"/"
            f"{breakdown['required_skills']['total']} "
            f"→ "
            f"{breakdown['required_skills']['contribution_points']} "
            f"points"
        )

        print(
            f"  Preferred skills: "
            f"{breakdown['preferred_skills']['matched']}"
            f"/"
            f"{breakdown['preferred_skills']['total']} "
            f"→ "
            f"{breakdown['preferred_skills']['contribution_points']} "
            f"points"
        )

        print(
            f"  Experience: "
            f"{breakdown['experience']['candidate_years']} "
            f"vs "
            f"{breakdown['experience']['minimum_years']} "
            f"years "
            f"→ "
            f"{breakdown['experience']['contribution_points']} "
            f"points"
        )

    if duplicates:
        print(
            "\nDuplicate Files"
        )

        print(
            "==============="
        )

        for duplicate in duplicates:
            print(
                f"{duplicate['file_name']} "
                f"→ duplicate of "
                f"{duplicate['duplicate_of']}"
            )

    if failures:
        print(
            "\nProcessing Issues"
        )

        print(
            "================="
        )

        for failure in failures:
            print(
                f"{failure['file_name']}: "
                f"{failure['error']}"
            )