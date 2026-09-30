from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import os
import secrets
import shutil
import uuid
from pathlib import Path

from fastapi import (
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile
)
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from job_parser import parse_job_description
from ranking import (
    find_resume_files,
    remove_duplicate_files,
    rank_candidates,
    count_recommendations
)


MAX_RESUMES = 20
MAX_FILE_BYTES = 2_000_000
MAX_UPLOAD_BYTES = 20_000_000
UPLOAD_LIMIT_MESSAGE = "The complete upload must be 20 MB or smaller."


def get_allowed_origins():
    origins = ["http://localhost:3000"]
    frontend_url = os.environ.get("FRONTEND_URL", "").strip().rstrip("/")
    if frontend_url and frontend_url not in origins:
        origins.append(frontend_url)
    return origins


class ScreeningAccessMiddleware:
    """Check access and bound the body before FastAPI parses resume uploads."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope["path"].rstrip("/") not in {"/screen", "/screen-demo"}
        ):
            await self.app(scope, receive, send)
            return

        expected_password = os.environ.get("SCREENING_PASSWORD", "")
        headers = Headers(scope=scope)
        provided_password = headers.get("X-Screening-Password", "")
        if not expected_password:
            response = JSONResponse(
                status_code=503,
                content={"detail": "Screening access is not configured. Please try again later."},
            )
            await response(scope, receive, send)
            return
        if not secrets.compare_digest(
            provided_password.encode("utf-8"), expected_password.encode("utf-8")
        ):
            response = JSONResponse(
                status_code=401,
                content={"detail": "Incorrect or missing screening password."},
            )
            await response(scope, receive, send)
            return

        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                declared_bytes = int(content_length)
            except ValueError:
                declared_bytes = -1
            if declared_bytes < 0:
                response = JSONResponse(
                    status_code=400, content={"detail": "Invalid upload size."}
                )
                await response(scope, receive, send)
                return
            if declared_bytes > MAX_UPLOAD_BYTES:
                response = JSONResponse(
                    status_code=413, content={"detail": UPLOAD_LIMIT_MESSAGE}
                )
                await response(scope, receive, send)
                return

        received_bytes = 0

        async def limited_receive() -> Message:
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail=UPLOAD_LIMIT_MESSAGE)
            return message

        await self.app(scope, limited_receive, send)


app = FastAPI(
    title="Automated Resume Screening API",
    version="0.3.0"
)
app.add_middleware(ScreeningAccessMiddleware)
# CORS wraps the access checks so browsers can read password/size errors too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
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
    request: JobDescriptionRequest,
    screening_password: Annotated[
        str | None, Header(alias="X-Screening-Password")
    ] = None,
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
            id="screening-form"
            action="/screen"
            method="post"
            enctype="multipart/form-data"
        >
            <h3>Screening Password</h3>
            <input id="screening-password" type="password" required>

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
        <pre id="screening-result" aria-live="polite"></pre>
        <script>
            document.getElementById("screening-form").addEventListener("submit", async (event) => {
                event.preventDefault();
                const result = document.getElementById("screening-result");
                const button = event.currentTarget.querySelector("button");
                const formData = new FormData(event.currentTarget);
                button.disabled = true;
                result.textContent = "Screening...";
                try {
                    const response = await fetch("/screen", {
                        method: "POST",
                        headers: {
                            "X-Screening-Password": document.getElementById("screening-password").value
                        },
                        body: formData
                    });
                    const data = await response.json();
                    result.textContent = response.ok ? JSON.stringify(data, null, 2) : data.detail;
                } catch (error) {
                    result.textContent = "Could not reach the screening service. Please try again.";
                } finally {
                    button.disabled = false;
                }
            });
        </script>
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
    ],
    screening_password: Annotated[
        str | None, Header(alias="X-Screening-Password")
    ] = None,
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

    if len(resumes) > MAX_RESUMES:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 resumes are allowed."
        )

    # Validate every submitted file, including duplicates and unsupported types.
    for upload in resumes:
        if upload.size is not None and upload.size > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=413, detail="Each resume must be 2 MB or smaller."
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

            file_content = await upload.read(MAX_FILE_BYTES + 1)
            if len(file_content) > MAX_FILE_BYTES:
                raise HTTPException(
                    status_code=413, detail="Each resume must be 2 MB or smaller."
                )

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

        job = await run_in_threadpool(parse_job_description, job_text)

        unique_resume_paths, duplicates = (
            await run_in_threadpool(
                remove_duplicate_files,
                saved_resume_paths
            )
        )

        rankings, failures, statistics = (
            await run_in_threadpool(
                rank_candidates,
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
