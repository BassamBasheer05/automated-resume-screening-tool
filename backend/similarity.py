from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ingest import read_resume


def calculate_text_similarity(
    resume_text,
    job_text
):
    documents = [
        job_text,
        resume_text
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    similarity_percentage = round(
        similarity * 100,
        2
    )

    return similarity_percentage


if __name__ == "__main__":
    job_path = (
        "data/sample_jobs/"
        "data_analyst_job.txt"
    )

    strong_resume_path = (
        "data/mixed_resumes/"
        "candidate_006.txt"
    )

    weak_resume_path = (
        "data/mixed_resumes/"
        "candidate_010.txt"
    )

    job_text = read_resume(
        job_path
    )

    strong_resume_text = read_resume(
        strong_resume_path
    )

    weak_resume_text = read_resume(
        weak_resume_path
    )

    strong_similarity = (
        calculate_text_similarity(
            strong_resume_text,
            job_text
        )
    )

    weak_similarity = (
        calculate_text_similarity(
            weak_resume_text,
            job_text
        )
    )

    print(
        f"Candidate 006 similarity: "
        f"{strong_similarity}%"
    )

    print(
        f"Candidate 010 similarity: "
        f"{weak_similarity}%"
    )