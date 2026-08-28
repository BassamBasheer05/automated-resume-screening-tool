from ingest import read_resume
from extract import parse_resume
from job_parser import parse_job_description


def match_candidate(candidate, job):
    candidate_skills = set(
        candidate["skills"]
    )

    required_skills = set(
        job["required_skills"]
    )

    preferred_skills = set(
        job["preferred_skills"]
    )

    required_skill_groups = (
        job.get(
            "required_skill_groups",
            []
        )
    )

    matched_required = (
        required_skills.intersection(
            candidate_skills
        )
    )

    missing_required = (
        required_skills.difference(
            candidate_skills
        )
    )

    matched_preferred = (
        preferred_skills.intersection(
            candidate_skills
        )
    )

    missing_preferred = (
        preferred_skills.difference(
            candidate_skills
        )
    )

    matched_required_skill_groups = []
    missing_required_skill_groups = []

    for group in required_skill_groups:
        group_skills = sorted(
            set(
                group
            )
        )

        matched_group_skills = sorted(
            set(
                group_skills
            ).intersection(
                candidate_skills
            )
        )

        if matched_group_skills:
            matched_required_skill_groups.append(
                {
                    "options":
                        group_skills,

                    "matched_skills":
                        matched_group_skills
                }
            )

        else:
            missing_required_skill_groups.append(
                group_skills
            )

    candidate_experience = (
        candidate[
            "years_experience"
        ]
    )

    minimum_experience = (
        job[
            "minimum_experience"
        ]
    )

    experience_met = (
        candidate_experience
        >= minimum_experience
    )

    result = {
        "matched_required_skills":
            sorted(
                matched_required
            ),

        "missing_required_skills":
            sorted(
                missing_required
            ),

        "matched_required_skill_groups":
            matched_required_skill_groups,

        "missing_required_skill_groups":
            missing_required_skill_groups,

        "matched_preferred_skills":
            sorted(
                matched_preferred
            ),

        "missing_preferred_skills":
            sorted(
                missing_preferred
            ),

        "candidate_experience":
            candidate_experience,

        "minimum_experience":
            minimum_experience,

        "experience_met":
            experience_met
    }

    return result


if __name__ == "__main__":
    resume_path = (
        "data/sample_resumes/"
        "alice_resume.txt"
    )

    job_path = (
        "data/sample_jobs/"
        "data_analyst_job.txt"
    )

    resume_text = read_resume(
        resume_path
    )

    job_text = read_resume(
        job_path
    )

    candidate = parse_resume(
        resume_text
    )

    job = parse_job_description(
        job_text
    )

    result = match_candidate(
        candidate,
        job
    )

    print(
        "Candidate:"
    )

    print(
        candidate
    )

    print(
        "\nJob:"
    )

    print(
        job
    )

    print(
        "\nMatching Result:"
    )

    print(
        result
    )