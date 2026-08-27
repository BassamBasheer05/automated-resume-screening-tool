from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import shutil
import uuid
from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    UploadFile
)
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from job_parser import parse_job_description
from ranking import (
    find_resume_files,
    remove_duplicate_files,
    rank_candidates,
    count_recommendations
)


app = FastAPI(
    title="Automated Resume Screening API",
    version="0.3.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobDescriptionRequest(BaseModel):
    job_description: str


@app.get("/")
def root():
    return {
        "message":
            "Automated Resume Screening API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/parse-job")
def parse_job(
    request: JobDescriptionRequest
):
    job_profile = parse_job_description(
        request.job_description
    )

    return {
        "job_profile": job_profile
    }


@app.post("/screen-demo")
def screen_demo(
    request: JobDescriptionRequest
):
    job_text = request.job_description

    job = parse_job_description(
        job_text
    )

    resume_folder = (
        "data/mixed_resumes"
    )

    resume_paths = find_resume_files(
        resume_folder
    )

    unique_resume_paths, duplicates = (
        remove_duplicate_files(
            resume_paths
        )
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

    return {
        "job_profile":
            job,

        "summary": {
            "files_discovered":
                len(resume_paths),

            "unique_resumes":
                len(unique_resume_paths),

            "duplicates_skipped":
                len(duplicates),

            "successfully_processed":
                statistics["successful"],

            "failed":
                statistics["failed"],

            "total_processing_seconds":
                statistics["total_seconds"],

            "average_seconds_per_resume":
                statistics[
                    "average_seconds_per_resume"
                ]
        },

        "recommendations":
            recommendation_counts,

        "top_candidates":
            rankings[:10],

        "duplicates":
            duplicates,

        "failures":
            failures
    }


@app.get(
    "/upload-test",
    response_class=HTMLResponse
)
def upload_test_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Screening Test</title>
    </head>

    <body>
        <h1>Resume Screening Test</h1>

        <form
            action="/screen"
            method="post"
            enctype="multipart/form-data"
        >
            <h3>Job Description</h3>

            <textarea
                name="job_description"
                rows="18"
                cols="80"
                required
            ></textarea>

            <h3>Upload Resumes</h3>

            <input
                name="resumes"
                type="file"
                accept=".pdf,.docx,.txt"
                multiple
                required
            >

            <br><br>

            <button type="submit">
                Screen Resumes
            </button>
        </form>
    </body>
    </html>
    """


@app.post("/screen")
async def screen_uploaded_resumes(
    job_description: Annotated[
        str,
        Form()
    ],
    resumes: Annotated[
        list[UploadFile],
        File()
    ]
):
    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    if not resumes:
        raise HTTPException(
            status_code=400,
            detail="At least one resume is required."
        )

    if len(resumes) > 500:
        raise HTTPException(
            status_code=400,
            detail="Maximum 500 resumes are allowed."
        )

    supported_extensions = {
        ".txt",
        ".pdf",
        ".docx"
    }

    session_id = str(
        uuid.uuid4()
    )

    session_folder = (
        Path("data/uploads")
        / session_id
    )

    session_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    saved_resume_paths = []
    rejected_files = []

    try:
        for index, upload in enumerate(
            resumes,
            start=1
        ):
            original_name = Path(
                upload.filename or ""
            ).name

            extension = Path(
                original_name
            ).suffix.lower()

            if (
                not original_name
                or extension
                not in supported_extensions
            ):
                rejected_files.append({
                    "file_name":
                        original_name
                        or "Unnamed file",

                    "reason":
                        "Unsupported file type"
                })

                continue

            destination = (
                session_folder
                / original_name
            )

            if destination.exists():
                destination = (
                    session_folder
                    / (
                        f"{Path(original_name).stem}"
                        f"_{index}"
                        f"{extension}"
                    )
                )

            file_content = await upload.read()

            destination.write_bytes(
                file_content
            )

            saved_resume_paths.append(
                str(destination)
            )

        if not saved_resume_paths:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No supported resumes were "
                    "provided. Use TXT, PDF, or DOCX."
                )
            )

        job_text = job_description

        job = parse_job_description(
            job_text
        )

        unique_resume_paths, duplicates = (
            remove_duplicate_files(
                saved_resume_paths
            )
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

        response = {
            "job_profile":
                job,

            "summary": {
                "files_received":
                    len(resumes),

                "supported_files":
                    len(saved_resume_paths),

                "unsupported_files":
                    len(rejected_files),

                "unique_resumes":
                    len(unique_resume_paths),

                "duplicates_skipped":
                    len(duplicates),

                "successfully_processed":
                    statistics["successful"],

                "failed":
                    statistics["failed"],

                "total_processing_seconds":
                    statistics["total_seconds"],

                "average_seconds_per_resume":
                    statistics[
                        "average_seconds_per_resume"
                    ]
            },

            "recommendations":
                recommendation_counts,

            "ranked_candidates":
                rankings,

            "duplicates":
                duplicates,

            "rejected_files":
                rejected_files,

            "failures":
                failures
        }

        return response

    finally:
        shutil.rmtree(
            session_folder,
            ignore_errors=True
        )