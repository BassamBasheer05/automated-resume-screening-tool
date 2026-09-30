import asyncio
import json
from pathlib import Path
from threading import Event

import httpx
import pytest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

import api
from api import app


client = TestClient(app)
TEST_PASSWORD = "test-screening-password"


@pytest.fixture(autouse=True)
def configure_screening_password(monkeypatch):
    monkeypatch.setenv("SCREENING_PASSWORD", TEST_PASSWORD)
    monkeypatch.setitem(
        client.headers,
        "X-Screening-Password",
        TEST_PASSWORD,
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


def test_health_endpoint():
    with TestClient(app) as public_client:
        response = public_client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_parse_job_accepts_natural_language():
    natural_job = """
    We are hiring a Data Analyst.

    You should have strong experience
    with Python, SQL, Excel and Power BI.

    Knowledge of Pandas and Tableau
    would be preferred.

    Candidates should have at least
    2 years of experience in analytics.
    """

    response = client.post(
        "/parse-job",
        json={
            "job_description":
                natural_job
        }
    )

    assert response.status_code == 200

    job = response.json()[
        "job_profile"
    ]

    assert job[
        "required_skills"
    ] == [
        "python",
        "sql",
        "excel",
        "power bi"
    ]

    assert job[
        "preferred_skills"
    ] == [
        "pandas",
        "tableau"
    ]

    assert (
        job[
            "minimum_experience"
        ]
        == 2.0
    )


def test_screen_valid_resume():
    resume_content = b"""
Alice Sharma
Data Analyst

Email: alice@example.com
Phone: 9999999999
Location: Bengaluru, India

Skills:
Python
SQL
Excel
Power BI
Pandas

Experience:
3 years of experience.
"""

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "alice_resume.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "files_received"
        ]
        == 1
    )

    assert (
        data["summary"][
            "successfully_processed"
        ]
        == 1
    )

    assert (
        data["summary"]["failed"]
        == 0
    )

    candidate = (
        data[
            "ranked_candidates"
        ][0]
    )

    assert (
        candidate["candidate_name"]
        == "Alice Sharma"
    )

    assert (
        candidate["score"]
        == 92.5
    )

    assert (
        candidate["recommendation"]
        == "Strong Match"
    )

    assert (
        candidate[
            "score_breakdown"
        ][
            "final_score"
        ]
        == 92.5
    )


def test_unsupported_file_is_rejected_but_valid_resume_continues():
    resume_content = b"""
Valid Candidate

Skills:
Python
SQL
Excel
Power BI

Experience:
2 years of experience.
"""

    csv_content = (
        b"Name,Skill\n"
        b"Unsupported Candidate,Python\n"
    )

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "valid_resume.txt",
                    resume_content,
                    "text/plain"
                )
            ),
            (
                "resumes",
                (
                    "unsupported.csv",
                    csv_content,
                    "text/csv"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "files_received"
        ]
        == 2
    )

    assert (
        data["summary"][
            "supported_files"
        ]
        == 1
    )

    assert (
        data["summary"][
            "unsupported_files"
        ]
        == 1
    )

    assert (
        data[
            "rejected_files"
        ][0][
            "file_name"
        ]
        == "unsupported.csv"
    )


def test_exact_duplicate_upload_is_skipped():
    resume_content = b"""
Duplicate Candidate

Skills:
Python
SQL
Excel
Power BI

Experience:
2 years of experience.
"""

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "resume_one.txt",
                    resume_content,
                    "text/plain"
                )
            ),
            (
                "resumes",
                (
                    "resume_two.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "files_received"
        ]
        == 2
    )

    assert (
        data["summary"][
            "unique_resumes"
        ]
        == 1
    )

    assert (
        data["summary"][
            "duplicates_skipped"
        ]
        == 1
    )

    assert (
        data["summary"][
            "successfully_processed"
        ]
        == 1
    )

    assert (
        len(
            data["duplicates"]
        )
        == 1
    )


def test_broken_pdf_does_not_stop_valid_resume():
    valid_resume = b"""
Valid Candidate

Skills:
Python
SQL
Excel
Power BI
Pandas

Experience:
3 years of experience.
"""

    broken_pdf = (
        b"This is deliberately "
        b"not a real PDF file."
    )

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=[
            (
                "resumes",
                (
                    "valid_resume.txt",
                    valid_resume,
                    "text/plain"
                )
            ),
            (
                "resumes",
                (
                    "broken_resume.pdf",
                    broken_pdf,
                    "application/pdf"
                )
            )
        ]
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["summary"][
            "unique_resumes"
        ]
        == 2
    )

    assert (
        data["summary"][
            "successfully_processed"
        ]
        == 1
    )

    assert (
        data["summary"]["failed"]
        == 1
    )

    assert (
        len(
            data["ranked_candidates"]
        )
        == 1
    )

    assert (
        data["failures"][0][
            "file_name"
        ]
        == "broken_resume.pdf"
    )


def test_empty_job_description_is_rejected():
    resume_content = b"""
Test Candidate

Skills:
Python

Experience:
1 year of experience.
"""

    response = client.post(
        "/screen",
        data={
            "job_description": "   "
        },
        files=[
            (
                "resumes",
                (
                    "resume.txt",
                    resume_content,
                    "text/plain"
                )
            )
        ]
    )

    assert response.status_code == 400

    assert response.json()[
        "detail"
    ] == (
        "Job description cannot "
        "be empty."
    )


@pytest.mark.parametrize("extension", ["txt", "csv"])
def test_more_than_20_resumes_is_rejected(extension):
    files = []

    for index in range(21):
        files.append(
            (
                "resumes",
                (
                    f"resume_{index}.{extension}",
                    b"Test Candidate",
                    "text/plain"
                )
            )
        )

    response = client.post(
        "/screen",
        data={
            "job_description":
                JOB_TEXT
        },
        files=files
    )

    assert response.status_code == 400

    assert response.json()[
        "detail"
    ] == (
        "Maximum 20 resumes "
        "are allowed."
    )


def test_parse_job_returns_required_skill_groups():
    response = client.post(
        "/parse-job",
        json={
            "job_description": """
Basic Qualifications:
- Knowledge of SQL or Python.
- Knowledge of Excel.

Preferred Qualifications:
- Experience with Tableau.

Minimum 2 years of experience.
"""
        }
    )

    assert response.status_code == 200

    job_profile = response.json()[
        "job_profile"
    ]

    assert job_profile[
        "required_skill_groups"
    ] == [
        [
            "sql",
            "python",
        ]
    ]

    assert set(
        job_profile[
            "required_skills"
        ]
    ) == {
        "excel",
    }


async def call_raw_asgi(path, chunks, headers, refuse_body=False):
    """Send raw chunks so tests do not rely on an honest Content-Length."""
    chunks = list(chunks)
    receive_count = 0
    messages = []

    async def receive():
        nonlocal receive_count
        if refuse_body:
            pytest.fail("The unauthorized request body was read.")
        index = receive_count
        receive_count += 1
        if index >= len(chunks):
            return {"type": "http.disconnect"}
        return {
            "type": "http.request",
            "body": chunks[index],
            "more_body": index < len(chunks) - 1,
        }

    async def send(message):
        messages.append(message)

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "headers": [
                (key.lower().encode(), value.encode())
                for key, value in headers.items()
            ],
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 12345),
        },
        receive,
        send,
    )
    status = next(
        message["status"]
        for message in messages
        if message["type"] == "http.response.start"
    )
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return status, json.loads(body), receive_count


def multipart_request(files):
    request = httpx.Request(
        "POST",
        "http://testserver/screen",
        data={"job_description": JOB_TEXT},
        files=files,
    )
    return request.read(), request.headers["content-type"]


def empty_ranking(*args):
    return [], [], {
        "successful": 0,
        "failed": 0,
        "total_seconds": 0.0,
        "average_seconds_per_resume": 0.0,
    }


@pytest.mark.parametrize("path", ["/screen", "/screen-demo", "/screen/"])
@pytest.mark.parametrize("password", [None, "incorrect-password"])
def test_screening_rejects_bad_password_before_reading_body(path, password):
    headers = {"content-type": "application/octet-stream"}
    if password is not None:
        headers["X-Screening-Password"] = password

    status, payload, reads = asyncio.run(
        call_raw_asgi(path, [], headers, refuse_body=True)
    )

    assert status == 401
    assert payload["detail"] == "Incorrect or missing screening password."
    assert reads == 0


def test_screening_is_unavailable_when_password_is_not_configured(monkeypatch):
    monkeypatch.delenv("SCREENING_PASSWORD")
    status, payload, reads = asyncio.run(
        call_raw_asgi(
            "/screen",
            [],
            {"X-Screening-Password": TEST_PASSWORD},
            refuse_body=True,
        )
    )

    assert status == 503
    assert payload["detail"] == (
        "Screening access is not configured. Please try again later."
    )
    assert reads == 0
    with TestClient(app) as public_client:
        assert public_client.get("/health").json() == {"status": "healthy"}


def test_authenticated_demo_keeps_existing_response(monkeypatch):
    monkeypatch.setattr(api, "rank_candidates", empty_ranking)
    response = client.post("/screen-demo", json={"job_description": JOB_TEXT})

    assert response.status_code == 200
    assert response.json()["summary"]["files_discovered"] == 30
    assert "top_candidates" in response.json()
    assert "duplicates" in response.json()
    assert "failures" in response.json()


def test_20_resumes_are_accepted_even_when_they_are_duplicates():
    response = client.post(
        "/screen",
        data={"job_description": JOB_TEXT},
        files=[
            ("resumes", (f"resume_{index}.txt", b"Candidate\nSkills: Python"))
            for index in range(20)
        ],
    )

    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["files_received"] == 20
    assert summary["unique_resumes"] == 1
    assert summary["duplicates_skipped"] == 19


def test_file_exactly_2_mb_is_accepted(monkeypatch):
    monkeypatch.setattr(api, "rank_candidates", empty_ranking)
    response = client.post(
        "/screen",
        data={"job_description": JOB_TEXT},
        files=[("resumes", ("resume.txt", b"x" * 2_000_000))],
    )

    assert response.status_code == 200
    assert response.json()["summary"]["supported_files"] == 1


@pytest.mark.parametrize("extension", ["txt", "csv"])
def test_oversized_file_is_rejected_and_uploads_are_cleaned(
    extension, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    response = client.post(
        "/screen",
        data={"job_description": JOB_TEXT},
        files=[
            ("resumes", ("valid.txt", b"Candidate\nSkills: Python")),
            ("resumes", (f"large.{extension}", b"x" * 2_000_001)),
        ],
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Each resume must be 2 MB or smaller."
    upload_root = tmp_path / "data" / "uploads"
    assert not upload_root.exists() or list(upload_root.iterdir()) == []


@pytest.mark.parametrize("declared_length", ["actual", None, "1"])
def test_total_upload_limit_counts_actual_body_and_multipart_overhead(
    declared_length, monkeypatch
):
    monkeypatch.setattr(api, "rank_candidates", empty_ranking)
    body, content_type = multipart_request(
        [
            ("resumes", (f"resume_{index}.txt", b"x" * 2_000_000))
            for index in range(10)
        ]
    )
    # File contents total 20 MB, but the complete upload also includes the form.
    assert len(body) > 20_000_000
    headers = {
        "content-type": content_type,
        "X-Screening-Password": TEST_PASSWORD,
    }
    if declared_length == "actual":
        headers["content-length"] = str(len(body))
    elif declared_length is not None:
        headers["content-length"] = declared_length
    else:
        headers["transfer-encoding"] = "chunked"

    status, payload, reads = asyncio.run(
        call_raw_asgi(
            "/screen",
            (body[index:index + 65_536] for index in range(0, len(body), 65_536)),
            headers,
        )
    )

    assert status == 413
    assert payload["detail"] == "The complete upload must be 20 MB or smaller."
    if declared_length == "actual":
        assert reads == 0


def test_complete_upload_exactly_20_mb_is_accepted(monkeypatch):
    monkeypatch.setattr(api, "rank_candidates", empty_ranking)
    files = [
        ("resumes", (f"resume_{index}.txt", b"x" * 2_000_000))
        for index in range(9)
    ]
    initial_body, _ = multipart_request(
        files + [("resumes", ("last.txt", b""))]
    )
    body, content_type = multipart_request(
        files + [("resumes", ("last.txt", b"x" * (20_000_000 - len(initial_body))))]
    )
    assert len(body) == 20_000_000

    response = client.post(
        "/screen", content=body, headers={"content-type": content_type}
    )

    assert response.status_code == 200
    assert response.json()["summary"]["files_received"] == 10


def test_hosted_frontend_cors_allows_password_requests_and_error_messages(
    monkeypatch,
):
    origin = "https://resume-demo.vercel.app"
    monkeypatch.setenv("FRONTEND_URL", origin + "/")
    allowed_origins = api.get_allowed_origins()
    assert allowed_origins == ["http://localhost:3000", origin]

    cors_middleware = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls is CORSMiddleware
    )
    monkeypatch.setitem(cors_middleware.kwargs, "allow_origins", allowed_origins)
    monkeypatch.setattr(app, "middleware_stack", None)

    response = client.options(
        "/screen",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Screening-Password",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "x-screening-password" in response.headers[
        "access-control-allow-headers"
    ].lower()

    response = client.post(
        "/screen",
        headers={"Origin": origin, "X-Screening-Password": "incorrect"},
    )
    assert response.status_code == 401
    assert response.headers["access-control-allow-origin"] == origin

    response = client.options(
        "/screen",
        headers={
            "Origin": "https://unapproved.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_pdf_and_docx_uploads_still_work():
    sample_folder = Path(__file__).resolve().parents[1] / "data" / "sample_resumes"
    files = [
        ("resumes", (name, (sample_folder / name).read_bytes()))
        for name in ["alice_resume.pdf", "bob_resume.docx"]
    ]
    response = client.post(
        "/screen", data={"job_description": JOB_TEXT}, files=files
    )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["successfully_processed"] == 2
    assert data["summary"]["failed"] == 0
    assert {candidate["file_name"] for candidate in data["ranked_candidates"]} == {
        "alice_resume.pdf",
        "bob_resume.docx",
    }


def test_health_is_responsive_during_screening_and_uploads_are_cleaned(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    started = Event()
    release = Event()
    saved_paths = []
    original_rank = api.rank_candidates

    def waiting_rank(resume_paths, job, job_text):
        saved_paths.extend(Path(path) for path in resume_paths)
        started.set()
        if not release.wait(timeout=5):
            raise TimeoutError("The health request did not finish during screening.")
        return original_rank(resume_paths, job, job_text)

    monkeypatch.setattr(api, "rank_candidates", waiting_rank)

    async def check_health_during_screening():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as async_client:
            screening = asyncio.create_task(
                async_client.post(
                    "/screen",
                    headers={"X-Screening-Password": TEST_PASSWORD},
                    data={"job_description": JOB_TEXT},
                    files=[("resumes", ("resume.txt", b"Candidate\nSkills: Python"))],
                )
            )
            try:
                assert await asyncio.to_thread(started.wait, 2)
                assert not screening.done()
                health = await asyncio.wait_for(async_client.get("/health"), 1)
                assert health.status_code == 200
                assert health.json() == {"status": "healthy"}
                assert all(path.exists() for path in saved_paths)
            finally:
                release.set()
                response = await asyncio.wait_for(screening, 5)
            assert response.status_code == 200

    asyncio.run(check_health_during_screening())
    assert saved_paths
    assert all(not path.exists() for path in saved_paths)
    assert list((tmp_path / "data" / "uploads").iterdir()) == []
