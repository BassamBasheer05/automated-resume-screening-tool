import re

from ingest import read_resume
from extract import extract_years_experience
from skills import extract_skills


REQUIRED_HEADINGS = {
    "required skills",
    "must have",
    "must-have",
    "required qualifications",
    "basic qualifications",
    "requirements",
    "minimum qualifications",
    "what you'll bring",
    "qualifications"
}


PREFERRED_HEADINGS = {
    "preferred skills",
    "nice to have",
    "nice-to-have",
    "preferred qualifications",
    "preferred",
    "bonus skills",
    "good to have",
    "good-to-have"
}


OTHER_HEADINGS = {
    "experience",
    "responsibilities",
    "key responsibilities",
    "duties",
    "job responsibilities",
    "role responsibilities",
    "about the role",
    "about you",
    "job description"
}


def normalize_heading(line):
    normalized = (
        line
        .strip()
        .lower()
        .replace("’", "'")
    )

    normalized = re.sub(
        r"[:\-–—]+\s*$",
        "",
        normalized
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    return normalized.strip()


def extract_section_by_headings(
    text,
    start_headings
):
    lines = text.splitlines()

    all_headings = (
        REQUIRED_HEADINGS
        | PREFERRED_HEADINGS
        | OTHER_HEADINGS
    )

    collecting = False
    collected_lines = []

    for line in lines:
        normalized_line = (
            normalize_heading(
                line
            )
        )

        if not collecting:
            if (
                normalized_line
                in start_headings
            ):
                collecting = True

            continue

        if (
            normalized_line
            in all_headings
        ):
            break

        collected_lines.append(
            line
        )

    return "\n".join(
        collected_lines
    )


def extract_skills_from_sentences(
    job_text
):
    normalized_text = re.sub(
        r"\s+",
        " ",
        job_text
    ).strip()

    sentences = re.split(
        r"(?<=[.!?])\s+",
        normalized_text
    )

    required_skills = []
    preferred_skills = []


    required_cues = [
        "must have",
        "should have",
        "required",
        "requirements include",
        "need to have",
        "needs to have",
        "strong experience with",
        "proficiency in",
        "proficient in"
    ]


    preferred_cues = [
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "would be a plus",
        "is a plus",
        "good to have"
    ]


    for sentence in sentences:
        lower_sentence = (
            sentence.lower()
        )

        sentence_skills = (
            extract_skills(
                sentence
            )
        )

        if not sentence_skills:
            continue


        is_preferred = any(
            cue in lower_sentence
            for cue in preferred_cues
        )


        is_required = any(
            cue in lower_sentence
            for cue in required_cues
        )


        if is_preferred:
            for skill in sentence_skills:
                if (
                    skill
                    not in preferred_skills
                ):
                    preferred_skills.append(
                        skill
                    )

        elif is_required:
            for skill in sentence_skills:
                if (
                    skill
                    not in required_skills
                ):
                    required_skills.append(
                        skill
                    )


    return (
        required_skills,
        preferred_skills
    )


def parse_job_description(
    job_text
):
    required_section = (
        extract_section_by_headings(
            job_text,
            REQUIRED_HEADINGS
        )
    )

    preferred_section = (
        extract_section_by_headings(
            job_text,
            PREFERRED_HEADINGS
        )
    )


    required_skills = (
        extract_skills(
            required_section
        )
    )

    preferred_skills = (
        extract_skills(
            preferred_section
        )
    )


    # If structured headings were not
    # available, use conservative
    # sentence-level cues.
    (
        sentence_required,
        sentence_preferred
    ) = extract_skills_from_sentences(
        job_text
    )


    if not required_skills:
        required_skills = (
            sentence_required
        )


    if not preferred_skills:
        preferred_skills = (
            sentence_preferred
        )


    # A skill should not appear in both
    # categories. Required takes priority.
    preferred_skills = [
        skill
        for skill in preferred_skills
        if skill not in required_skills
    ]


    minimum_experience = (
        extract_years_experience(
            job_text
        )
    )


    job_profile = {
        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        "minimum_experience":
            minimum_experience
    }


    return job_profile


if __name__ == "__main__":
    job_path = (
        "data/sample_jobs/"
        "data_analyst_job.txt"
    )

    job_text = read_resume(
        job_path
    )

    job = parse_job_description(
        job_text
    )

    print(
        "Job profile:"
    )

    print(
        job
    )