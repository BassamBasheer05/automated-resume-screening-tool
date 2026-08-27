import random
from pathlib import Path


OUTPUT_FOLDER = Path("data/synthetic_resumes")

NUMBER_OF_RESUMES = 500


FIRST_NAMES = [
    "Aarav",
    "Diya",
    "Arjun",
    "Meera",
    "Rahul",
    "Ananya",
    "Vikram",
    "Neha",
    "Kiran",
    "Priya",
    "Rohan",
    "Sneha",
    "Aditya",
    "Isha",
    "Nikhil"
]


LAST_NAMES = [
    "Sharma",
    "Nair",
    "Patel",
    "Kumar",
    "Thomas",
    "Singh",
    "Rao",
    "Menon",
    "Gupta",
    "Joseph"
]


SKILLS = [
    "Python",
    "SQL",
    "Excel",
    "Power BI",
    "Pandas",
    "Tableau",
    "Data Analysis",
    "NumPy",
    "Git",
    "AWS"
]


JOB_TITLES = [
    "Data Analyst",
    "Junior Data Analyst",
    "Business Analyst",
    "Reporting Analyst",
    "Business Intelligence Analyst"
]


EDUCATION_OPTIONS = [
    "Bachelor of Commerce",
    "Bachelor of Science",
    "Bachelor of Business Administration",
    "Bachelor of Technology",
    "Master of Business Administration"
]


def create_resume(candidate_number):
    first_name = random.choice(FIRST_NAMES)

    last_name = random.choice(LAST_NAMES)

    full_name = f"{first_name} {last_name}"

    job_title = random.choice(JOB_TITLES)

    years_experience = random.choice(
        [0.5, 1, 1.5, 2, 2.5, 3, 4, 5]
    )

    number_of_skills = random.randint(2, 7)

    candidate_skills = random.sample(
        SKILLS,
        number_of_skills
    )

    education = random.choice(
        EDUCATION_OPTIONS
    )

    skills_text = "\n".join(
        candidate_skills
    )

    resume_text = f"""
{full_name}
{job_title}

Email: candidate{candidate_number}@example.com
Phone: 900000{candidate_number:04d}
Location: India

Professional Summary:
{job_title} with {years_experience} years of experience
working with data, reporting, analytics, and business insights.

Skills:
{skills_text}

Experience:
{job_title} with {years_experience} years of experience
working with analytics, reporting, and data-driven decision making.

Education:
{education}
""".strip()

    return resume_text


def generate_resumes():
    OUTPUT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    random.seed(42)

    for candidate_number in range(
        1,
        NUMBER_OF_RESUMES + 1
    ):
        resume_text = create_resume(
            candidate_number
        )

        file_name = (
            f"candidate_{candidate_number:03d}.txt"
        )

        file_path = (
            OUTPUT_FOLDER / file_name
        )

        file_path.write_text(
            resume_text,
            encoding="utf-8"
        )

    print(
        f"Generated {NUMBER_OF_RESUMES} "
        f"synthetic resumes."
    )

    print(
        f"Location: {OUTPUT_FOLDER}"
    )


if __name__ == "__main__":
    generate_resumes()