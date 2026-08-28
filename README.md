# Automated Resume Screening Tool

[![CI](https://github.com/BassamBasheer05/automated-resume-screening-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/BassamBasheer05/automated-resume-screening-tool/actions/workflows/ci.yml)

An explainable resume-screening prototype that compares a job description against multiple resumes, ranks candidates using configurable hiring criteria, and shows recruiters why each candidate received their score.

Built with **Python, FastAPI, scikit-learn, Next.js, and TypeScript**.

> This project is a decision-support prototype, not an automated hiring decision system. Candidate rankings should always be reviewed by a human.

---

## What It Does

A recruiter can:

- Paste a job description
- Upload up to 500 resumes
- Use TXT, PDF, or DOCX files
- Extract candidate skills and experience
- Identify matched and missing required skills
- Interpret alternative requirements such as `SQL or Python` as one requirement
- Identify matched and missing preferred skills
- Compare candidate experience against the minimum requirement
- Rank candidates using an explainable scoring model
- View TF-IDF text similarity as a secondary signal
- Search and filter screening results
- Inspect a score breakdown for each candidate
- Export filtered results to CSV
- Continue processing even when an individual resume fails
- Detect exact duplicate resume files

Uploaded resumes are processed in a temporary session folder and removed after the API request completes.

---

## Why I Built It

Resume screening is often difficult to audit because a recruiter may receive a score without understanding how it was produced.

This project explores a more transparent approach.

Instead of returning only a ranking, the system shows:

- which required skills matched
- which required skills are missing
- which alternative required groups were satisfied or missed
- which preferred skills matched
- whether minimum experience was met
- how much each criterion contributed to the final score
- a secondary text-similarity score

The goal is to make the screening logic easier to inspect, test, and challenge.

---

## System Architecture

```text
Job Description
      │
      ▼
Job Description Parser
      │
      ├── Required skills
      ├── Alternative required skill groups
      ├── Preferred skills
      └── Minimum experience
      │
      ▼
Resume Uploads
      │
      ▼
TXT / PDF / DOCX Extraction
      │
      ▼
Candidate Information Extraction
      │
      ├── Name
      ├── Email
      ├── Phone
      ├── Location
      ├── Skills
      └── Experience
      │
      ▼
Matching Engine
      │
      ├── Required skill matching
      ├── Alternative-group matching
      ├── Preferred skill matching
      └── Experience comparison
      │
      ▼
Explainable Scoring Engine
      │
      ├── Rule-based compatibility score
      └── TF-IDF text similarity
      │
      ▼
Ranking Engine
      │
      ▼
FastAPI
      │
      ▼
Next.js Recruiter Dashboard
```

---

## Scoring Model

The primary match score is rule-based and explainable.

Default weighting:

| Criterion | Weight |
|---|---:|
| Required skills | 60% |
| Preferred skills | 15% |
| Experience | 25% |

Alternative required skill groups are counted as one required requirement. For example, if a job states `SQL or Python`, a candidate can satisfy that requirement with either skill, and knowing both does not earn double credit.

The parser also handles example-style lists conservatively. Technologies introduced with cues such as `such as`, `like`, `for example`, or `including` are not automatically converted into separate mandatory requirements.

If a job description does not contain one of these criteria, the remaining weights are automatically normalized.

For example, if a job has required skills and experience but no preferred skills, candidates are not given free points for the missing category.

### Recommendation Guardrails

The system uses recommendation categories:

- **Strong Match**
- **Good Match**
- **Review**
- **Weak Match**

A candidate who is missing a required skill, fails an alternative required skill group, or does not meet the minimum experience requirement cannot automatically receive a Strong or Good Match recommendation purely because of a high numerical score.

This means recommendation priority can intentionally rank a candidate who meets all minimum requirements above a higher-scoring candidate who does not.

---

## TF-IDF Similarity

The project also calculates local text similarity using:

- `TfidfVectorizer`
- cosine similarity
- scikit-learn

This compares the overall resume text with the job description.

TF-IDF similarity is shown as a **secondary signal** and is not included in the primary compatibility score.

No paid AI API is required.

---

## Job Description Parsing

The parser supports several common formats, including headings such as:

```text
Required Skills
Must Have
Required Qualifications
Requirements
What You'll Bring

Preferred Skills
Nice to Have
Preferred Qualifications
Bonus Skills
Good to Have
```

It also includes a conservative sentence-based fallback for job descriptions written without clear headings.

Example:

```text
You should have strong experience with Python, SQL, Excel and Power BI.
Knowledge of Pandas and Tableau would be preferred.
Candidates should have at least 2 years of experience.
```

The parser can identify:

```text
Required:
Python
SQL
Excel
Power BI

Preferred:
Pandas
Tableau

Minimum experience:
2 years
```

---

## Resume Processing

Supported formats:

```text
.txt
.pdf
.docx
```

The current PDF implementation supports text-based PDFs.

Scanned/image-only PDFs are not currently processed with OCR.

The system also isolates file failures so one broken resume does not stop the rest of the batch.

---

## Duplicate Detection

Uploaded resumes are hashed using SHA-256.

If two uploaded files contain exactly the same bytes, the duplicate is skipped and reported separately.

---

## Recruiter Dashboard

The Next.js frontend includes:

- bulk resume upload
- job-description input
- candidate ranking
- recommendation summary
- processing statistics
- candidate search
- recommendation filters
- pagination
- configurable page size
- matched skills
- missing skills
- experience comparison
- detailed score explanation
- TF-IDF similarity
- CSV export

CSV export applies basic spreadsheet formula-injection protection.

---

## API

The FastAPI backend currently includes:

```text
GET  /
GET  /health
POST /parse-job
POST /screen-demo
POST /screen
```

Interactive FastAPI documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

---

## Example Screening Result

Using the included sample Data Analyst job description:

```text
Required:
Python
SQL
Excel
Power BI

Preferred:
Pandas
Tableau

Minimum experience:
2 years
```

An example candidate with:

```text
Required skills matched: 4 / 4
Preferred skills matched: 1 / 2
Experience: 3 years
```

receives:

```text
Required contribution:   60.0
Preferred contribution:   7.5
Experience contribution: 25.0
                         -----
Final match score:        92.5
Recommendation: Strong Match
```

This is a configured compatibility score, **not a probability that the candidate should be hired**.

---

## Automated Testing

The backend currently has **72 automated tests** covering:

| Area | Tests |
|---|---:|
| API | 9 |
| Basic-qualification and alternative parsing | 3 |
| Contact extraction | 6 |
| Experience extraction | 9 |
| Extended skill taxonomy | 6 |
| Job parsing | 7 |
| Matching | 5 |
| Ranking | 5 |
| Required skill groups | 5 |
| Requirement interpretation | 5 |
| Scoring | 5 |
| Screen/API alternative-group integration | 2 |
| Skill extraction and normalization | 5 |
| **Total** | **72** |

Current local test result:

```text
72 passed
```

The frontend also passes:

```text
ESLint
Next.js production build
TypeScript compilation
```

---

## Project Structure

```text
automated-resume-screening-tool/
│
├── backend/
│   ├── api.py
│   ├── extract.py
│   ├── ingest.py
│   ├── job_parser.py
│   ├── matching.py
│   ├── ranking.py
│   ├── scoring.py
│   ├── similarity.py
│   └── skills.py
│
├── frontend/
│   └── app/
│       └── page.tsx
│
├── data/
│   ├── mixed_resumes/
│   ├── robustness_test/
│   ├── sample_jobs/
│   └── sample_resumes/
│
├── tests/
│   ├── test_api.py
│   ├── test_basic_qualifications_parser.py
│   ├── test_contact_extraction.py
│   ├── test_experience.py
│   ├── test_extended_skill_taxonomy.py
│   ├── test_job_parser.py
│   ├── test_matching.py
│   ├── test_ranking.py
│   ├── test_required_skill_groups.py
│   ├── test_requirement_interpretation.py
│   ├── test_scoring.py
│   ├── test_screen_required_skill_groups.py
│   └── test_skills.py
│
├── .gitattributes
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/BassamBasheer05/automated-resume-screening-tool.git
cd automated-resume-screening-tool
```

### 2. Create a Python virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run automated backend tests

```bash
python -m pytest
```

Expected:

```text
72 passed
```

### 5. Start the FastAPI backend

From the project root:

```bash
python -m uvicorn api:app --app-dir backend --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

## Production Checks

Backend:

```bash
python -m pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

---

## Synthetic Test Data

The repository includes synthetic sample and mixed-format resumes for demonstration and testing.

A larger 500-resume synthetic dataset is intentionally excluded from Git because it can be regenerated using:

```bash
python backend/generate_synthetic_resumes.py
```

Synthetic resumes should not be interpreted as real candidate data.

---

## Current Limitations

This is a prototype and has important limitations:

- Skill detection uses a finite skill vocabulary.
- Text matching does not understand language at the level of a large language model.
- TF-IDF captures lexical similarity rather than true semantic understanding.
- Experience extraction requires explicit experience wording and does not currently infer total experience from arbitrary employment date ranges.
- Scanned PDFs require OCR, which is not currently implemented.
- Exact duplicate detection does not identify near-duplicate resumes.
- Scoring weights and thresholds are configured rules and have not been validated as predictors of job performance.
- Job-description parsing uses deterministic rules and cannot reliably interpret every possible writing style.
- The application currently has no authentication or production user-management layer.

---

## Responsible Use

Resume-screening systems can reproduce or amplify unfair hiring patterns.

This prototype intentionally does not score candidates directly on fields such as name, email, phone number, or location. However, excluding those fields does **not** guarantee fairness because skills, experience, language, job descriptions, and other data can still contain indirect sources of bias.

The output should therefore be treated as decision support only.

Recommended use:

```text
System ranks and explains
          ↓
Recruiter reviews evidence
          ↓
Human makes the decision
```

Do not use the score as an automatic hiring or rejection decision.

---

## Privacy

Uploaded resumes may contain sensitive personal information.

In the current local prototype:

- uploads are stored in a temporary per-request folder
- the folder is deleted after processing
- screening history is not persisted to a database
- users should avoid uploading real candidate data to untrusted deployments

A production implementation would require additional security, authentication, access control, retention policies, encryption, monitoring, and compliance review.

---

## Tech Stack

**Backend**

- Python
- FastAPI
- pypdf
- python-docx
- scikit-learn
- pytest

**Frontend**

- Next.js
- React
- TypeScript
- Tailwind CSS

**Matching**

- deterministic skill matching
- experience matching
- configurable weighted scoring
- TF-IDF
- cosine similarity

---

## Status

Current prototype capabilities:

```text
Resume ingestion            ✅
TXT / PDF / DOCX            ✅
Skill extraction            ✅
Experience extraction       ✅
JD parsing                  ✅
Alternative skill groups    ✅
Candidate matching          ✅
Explainable scoring         ✅
TF-IDF similarity           ✅
Recommendation guardrails   ✅
Duplicate detection         ✅
Batch failure isolation     ✅
500-resume screening        ✅
FastAPI                     ✅
Recruiter dashboard         ✅
Search and filtering        ✅
Pagination                  ✅
CSV export                  ✅
72 backend tests            ✅
Frontend lint               ✅
Production frontend build   ✅
```

---

## Future Improvements

Potential next steps include:

- semantic embeddings
- configurable skill taxonomies
- improved employment-date parsing
- OCR for scanned resumes
- near-duplicate detection
- persistent screening sessions
- authentication and access control
- database-backed screening history
- deployment and monitoring
- fairness evaluation using controlled datasets
- recruiter feedback loops
- configurable scoring policies

---

## Disclaimer

This project is an educational and technical prototype.

It should not be used as the sole basis for employment decisions. Human review, appropriate validation, privacy safeguards, and applicable employment regulations are required before use in a real hiring process.