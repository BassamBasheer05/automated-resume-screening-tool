from ranking import (
    count_recommendations,
    rank_candidates,
    remove_duplicate_files
)


JOB_TEXT = """
Data Analyst

Required Skills:
Python
SQL
Excel
Power BI

Preferred Skills:
Pandas
Tableau

Experience:
Minimum 2 years of experience.

Responsibilities:
Analyze business data.
"""


JOB = {
    "required_skills": [
        "python",
        "sql",
        "excel",
        "power bi"
    ],
    "preferred_skills": [
        "pandas",
        "tableau"
    ],
    "minimum_experience": 2.0
}


def test_good_match_ranks_above_higher_scoring_review(
    tmp_path
):
    good_resume = tmp_path / "good_candidate.txt"

    good_resume.write_text(
        """
Good Candidate
Email: good@example.com
Location: India

Skills:
Python
SQL
Excel
Power BI

Experience:
2 years of experience.
""",
        encoding="utf-8"
    )


    review_resume = (
        tmp_path / "review_candidate.txt"
    )

    review_resume.write_text(
        """
Review Candidate
Email: review@example.com
Location: India

Skills:
Python
SQL
Excel
Power BI
Pandas
Tableau

Experience:
1 year of experience.
""",
        encoding="utf-8"
    )


    rankings, failures, statistics = (
        rank_candidates(
            [
                str(review_resume),
                str(good_resume)
            ],
            JOB,
            JOB_TEXT
        )
    )


    assert failures == []

    assert (
        statistics["successful"]
        == 2
    )

    assert (
        rankings[0]["candidate_name"]
        == "Good Candidate"
    )

    assert (
        rankings[0]["score"]
        == 85.0
    )

    assert (
        rankings[0]["recommendation"]
        == "Good Match"
    )


    assert (
        rankings[1]["candidate_name"]
        == "Review Candidate"
    )

    assert (
        rankings[1]["score"]
        == 87.5
    )

    assert (
        rankings[1]["recommendation"]
        == "Review"
    )


def test_higher_score_wins_inside_same_recommendation(
    tmp_path
):
    perfect_resume = (
        tmp_path / "perfect_candidate.txt"
    )

    perfect_resume.write_text(
        """
Perfect Candidate

Skills:
Python
SQL
Excel
Power BI
Pandas
Tableau

Experience:
2 years of experience.
""",
        encoding="utf-8"
    )


    strong_resume = (
        tmp_path / "strong_candidate.txt"
    )

    strong_resume.write_text(
        """
Strong Candidate

Skills:
Python
SQL
Excel
Power BI
Pandas

Experience:
2 years of experience.
""",
        encoding="utf-8"
    )


    rankings, failures, _ = (
        rank_candidates(
            [
                str(strong_resume),
                str(perfect_resume)
            ],
            JOB,
            JOB_TEXT
        )
    )


    assert failures == []

    assert (
        rankings[0]["candidate_name"]
        == "Perfect Candidate"
    )

    assert rankings[0]["score"] == 100.0

    assert (
        rankings[0]["recommendation"]
        == "Strong Match"
    )


    assert (
        rankings[1]["candidate_name"]
        == "Strong Candidate"
    )

    assert rankings[1]["score"] == 92.5

    assert (
        rankings[1]["recommendation"]
        == "Strong Match"
    )


def test_exact_duplicate_files_are_removed(
    tmp_path
):
    content = """
Duplicate Candidate

Skills:
Python
SQL

Experience:
2 years of experience.
"""

    first_file = (
        tmp_path / "resume_one.txt"
    )

    second_file = (
        tmp_path / "resume_two.txt"
    )

    first_file.write_text(
        content,
        encoding="utf-8"
    )

    second_file.write_text(
        content,
        encoding="utf-8"
    )


    unique_files, duplicates = (
        remove_duplicate_files(
            [
                str(first_file),
                str(second_file)
            ]
        )
    )


    assert len(unique_files) == 1
    assert len(duplicates) == 1

    assert (
        duplicates[0]["file_name"]
        == "resume_two.txt"
    )

    assert (
        duplicates[0]["duplicate_of"]
        == "resume_one.txt"
    )


def test_broken_resume_does_not_stop_batch(
    tmp_path
):
    valid_resume = (
        tmp_path / "valid_resume.txt"
    )

    valid_resume.write_text(
        """
Valid Candidate

Skills:
Python
SQL
Excel
Power BI
Pandas

Experience:
3 years of experience.
""",
        encoding="utf-8"
    )


    broken_pdf = (
        tmp_path / "broken_resume.pdf"
    )

    broken_pdf.write_text(
        "This is not a real PDF file.",
        encoding="utf-8"
    )


    rankings, failures, statistics = (
        rank_candidates(
            [
                str(valid_resume),
                str(broken_pdf)
            ],
            JOB,
            JOB_TEXT
        )
    )


    assert (
        statistics["total_resumes"]
        == 2
    )

    assert (
        statistics["successful"]
        == 1
    )

    assert (
        statistics["failed"]
        == 1
    )

    assert len(rankings) == 1
    assert len(failures) == 1

    assert (
        rankings[0]["candidate_name"]
        == "Valid Candidate"
    )

    assert (
        failures[0]["file_name"]
        == "broken_resume.pdf"
    )


def test_recommendation_counts_are_correct():
    rankings = [
        {
            "recommendation":
                "Strong Match"
        },
        {
            "recommendation":
                "Review"
        },
        {
            "recommendation":
                "Review"
        },
        {
            "recommendation":
                "Weak Match"
        },
        {
            "recommendation":
                "Good Match"
        }
    ]


    counts = count_recommendations(
        rankings
    )


    assert counts == {
        "Strong Match": 1,
        "Good Match": 1,
        "Review": 2,
        "Weak Match": 1
    }