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


EXAMPLE_CUE_PATTERNS = [
    r"\bsuch as\b",
    r"\bfor example\b",
    r"\be\.g\.",
    r"\bincluding but not limited to\b",
    r"\bincluding\b",
    r"\blike\b"
]


OR_PATTERN = re.compile(
    r"\b(?:and/or|or)\b",
    re.IGNORECASE
)


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


def append_unique_skills(
    target,
    skills
):
    for skill in skills:
        if skill not in target:
            target.append(
                skill
            )


def append_unique_skill_group(
    target,
    skill_group
):
    unique_group = []

    append_unique_skills(
        unique_group,
        skill_group
    )

    if len(unique_group) < 2:
        return

    group_set = set(
        unique_group
    )

    for existing_group in target:
        if set(existing_group) == group_set:
            return

    target.append(
        unique_group
    )


def find_example_cue_position(
    text
):
    positions = []

    for pattern in EXAMPLE_CUE_PATTERNS:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            positions.append(
                match.start()
            )

    if not positions:
        return None

    return min(
        positions
    )


def prepare_required_text(
    line
):
    """
    Remove portions that are clearly
    illustrative examples rather than
    independent hard requirements.
    """

    example_position = (
        find_example_cue_position(
            line
        )
    )

    if example_position is not None:
        return (
            line[
                :example_position
            ]
            .strip()
        )

    parenthetical_groups = re.findall(
        r"\(([^()]*)\)",
        line
    )

    parenthetical_skills = []

    for group in parenthetical_groups:
        append_unique_skills(
            parenthetical_skills,
            extract_skills(
                group
            )
        )

    if len(parenthetical_skills) >= 2:
        return (
            line.split(
                "(",
                1
            )[0]
            .strip()
        )

    return line


def extract_required_components_from_line(
    line
):
    """
    Return two kinds of requirements:

    1. Independent required skills.
    2. Alternative skill groups where
       satisfying any one skill is enough.

    If an OR statement contains an
    unrecognized alternative, the statement
    is handled conservatively instead of
    making the recognized side mandatory.
    """

    requirement_text = (
        prepare_required_text(
            line
        )
    )

    if not requirement_text:
        return [], []

    if not OR_PATTERN.search(
        requirement_text
    ):
        return (
            extract_skills(
                requirement_text
            ),
            []
        )

    alternative_parts = (
        OR_PATTERN.split(
            requirement_text
        )
    )

    skills_by_part = []

    for part in alternative_parts:
        part_skills = (
            extract_skills(
                part
            )
        )

        skills_by_part.append(
            part_skills
        )

    # Every side of the OR statement must
    # contain at least one recognized skill.
    # Otherwise we cannot represent the
    # alternatives faithfully.
    if any(
        not part_skills
        for part_skills
        in skills_by_part
    ):
        return [], []

    alternative_group = []

    for part_skills in skills_by_part:
        append_unique_skills(
            alternative_group,
            part_skills
        )

    if len(alternative_group) < 2:
        return [], []

    return (
        [],
        [
            alternative_group
        ]
    )


def extract_required_skills_from_line(
    line
):
    """
    Backward-compatible helper returning
    only independent hard-required skills.
    """

    (
        required_skills,
        _
    ) = extract_required_components_from_line(
        line
    )

    return required_skills


def split_section_into_items(
    section_text
):
    items = []
    current_item = None

    bullet_pattern = re.compile(
        r"^\s*[-•*]\s*"
    )

    for raw_line in section_text.splitlines():
        if not raw_line.strip():
            continue

        is_bullet = (
            bullet_pattern.match(
                raw_line
            )
            is not None
        )

        cleaned_line = (
            bullet_pattern.sub(
                "",
                raw_line
            )
            .strip()
        )

        if is_bullet:
            if current_item:
                items.append(
                    current_item
                )

            current_item = (
                cleaned_line
            )

        elif current_item is not None:
            current_item = (
                current_item
                + " "
                + cleaned_line
            )

        else:
            items.append(
                cleaned_line
            )

    if current_item:
        items.append(
            current_item
        )

    return items


def extract_required_requirements_from_section(
    section_text
):
    required_skills = []
    required_skill_groups = []

    section_items = (
        split_section_into_items(
            section_text
        )
    )

    for item in section_items:
        (
            item_skills,
            item_groups
        ) = extract_required_components_from_line(
            item
        )

        append_unique_skills(
            required_skills,
            item_skills
        )

        for group in item_groups:
            append_unique_skill_group(
                required_skill_groups,
                group
            )

    return (
        required_skills,
        required_skill_groups
    )


def extract_required_skills_from_section(
    section_text
):
    """
    Backward-compatible helper returning
    only independent required skills.
    """

    (
        required_skills,
        _
    ) = extract_required_requirements_from_section(
        section_text
    )

    return required_skills


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
    required_skill_groups = []
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

        is_preferred = any(
            cue in lower_sentence
            for cue in preferred_cues
        )

        is_required = any(
            cue in lower_sentence
            for cue in required_cues
        )

        if is_preferred:
            sentence_skills = (
                extract_skills(
                    sentence
                )
            )

            append_unique_skills(
                preferred_skills,
                sentence_skills
            )

        elif is_required:
            (
                sentence_skills,
                sentence_groups
            ) = extract_required_components_from_line(
                sentence
            )

            append_unique_skills(
                required_skills,
                sentence_skills
            )

            for group in sentence_groups:
                append_unique_skill_group(
                    required_skill_groups,
                    group
                )

    return (
        required_skills,
        required_skill_groups,
        preferred_skills
    )


def remove_redundant_required_groups(
    required_skill_groups,
    required_skills
):
    """
    If one member of an OR group is already
    independently mandatory elsewhere, the
    OR requirement is automatically satisfied
    by that mandatory skill and should not be
    counted again.
    """

    required_skill_set = set(
        required_skills
    )

    filtered_groups = []

    for group in required_skill_groups:
        if any(
            skill in required_skill_set
            for skill in group
        ):
            continue

        append_unique_skill_group(
            filtered_groups,
            group
        )

    return filtered_groups


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

    (
        required_skills,
        required_skill_groups
    ) = extract_required_requirements_from_section(
        required_section
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
        sentence_required_groups,
        sentence_preferred
    ) = extract_skills_from_sentences(
        job_text
    )

    if (
        not required_skills
        and not required_skill_groups
    ):
        required_skills = (
            sentence_required
        )

        required_skill_groups = (
            sentence_required_groups
        )

    if not preferred_skills:
        preferred_skills = (
            sentence_preferred
        )

    required_skill_groups = (
        remove_redundant_required_groups(
            required_skill_groups,
            required_skills
        )
    )

    # A directly required skill should not
    # also be counted as preferred.
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

        "required_skill_groups":
            required_skill_groups,

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