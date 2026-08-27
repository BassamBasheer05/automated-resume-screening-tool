"use client";

import { useState } from "react";
import type { ReactNode } from "react";


type SkillScoreBreakdown = {
  matched: number;
  total: number;
  match_percentage: number;
  weight_percentage: number;
  contribution_points: number;
};


type ExperienceScoreBreakdown = {
  candidate_years: number;
  minimum_years: number;
  match_percentage: number;
  weight_percentage: number;
  contribution_points: number;
};


type ScoreBreakdown = {
  required_skills: SkillScoreBreakdown;
  preferred_skills: SkillScoreBreakdown;
  experience: ExperienceScoreBreakdown;
  final_score: number;
};


type Candidate = {
  candidate_name: string;
  email: string;
  phone: string;
  location: string;
  file_name: string;
  score: number;
  score_breakdown: ScoreBreakdown;
  text_similarity: number;
  recommendation: string;
  matched_required_skills: string[];
  missing_required_skills: string[];
  matched_preferred_skills: string[];
  candidate_experience: number;
  experience_met: boolean;
};


type DuplicateFile = {
  file_name: string;
  duplicate_of: string;
};


type RejectedFile = {
  file_name: string;
  reason: string;
};


type FailedFile = {
  file_name: string;
  error: string;
  processing_seconds?: number;
};


type ScreeningResponse = {
  summary: {
    files_received: number;
    supported_files: number;
    unsupported_files: number;
    unique_resumes: number;
    duplicates_skipped: number;
    successfully_processed: number;
    failed: number;
    total_processing_seconds: number;
    average_seconds_per_resume: number;
  };

  recommendations: {
    "Strong Match": number;
    "Good Match": number;
    Review: number;
    "Weak Match": number;
  };

  ranked_candidates: Candidate[];
  duplicates: DuplicateFile[];
  rejected_files: RejectedFile[];
  failures: FailedFile[];
};


type RecommendationFilter =
  | "All"
  | "Strong Match"
  | "Good Match"
  | "Review"
  | "Weak Match";


export default function Home() {
  const [jobDescription, setJobDescription] =
    useState("");

  const [files, setFiles] =
    useState<File[]>([]);

  const [results, setResults] =
    useState<ScreeningResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [
    expandedCandidate,
    setExpandedCandidate
  ] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] =
    useState("");

  const [
    recommendationFilter,
    setRecommendationFilter
  ] = useState<RecommendationFilter>("All");

  const [currentPage, setCurrentPage] =
    useState(1);

  const [pageSize, setPageSize] =
    useState(10);


  const filteredCandidates =
    results
      ? results.ranked_candidates
          .map((candidate, index) => ({
            candidate,
            rank: index + 1
          }))
          .filter(({ candidate }) => {
            const search =
              searchTerm
                .trim()
                .toLowerCase();

            const matchesSearch =
              search === "" ||
              candidate.candidate_name
                .toLowerCase()
                .includes(search) ||
              candidate.email
                .toLowerCase()
                .includes(search) ||
              candidate.location
                .toLowerCase()
                .includes(search) ||
              candidate.file_name
                .toLowerCase()
                .includes(search);

            const matchesRecommendation =
              recommendationFilter === "All" ||
              candidate.recommendation ===
                recommendationFilter;

            return (
              matchesSearch &&
              matchesRecommendation
            );
          })
      : [];


  const totalPages =
    Math.max(
      1,
      Math.ceil(
        filteredCandidates.length /
          pageSize
      )
    );


  const safeCurrentPage =
    Math.min(
      currentPage,
      totalPages
    );


  const firstIndex =
    (safeCurrentPage - 1) *
    pageSize;


  const lastIndex =
    Math.min(
      firstIndex + pageSize,
      filteredCandidates.length
    );


  const paginatedCandidates =
    filteredCandidates.slice(
      firstIndex,
      lastIndex
    );


  async function handleScreen() {
    setError("");

    if (!jobDescription.trim()) {
      setError(
        "Please enter a job description."
      );
      return;
    }

    if (files.length === 0) {
      setError(
        "Please upload at least one resume."
      );
      return;
    }

    if (files.length > 500) {
      setError(
        "Maximum 500 resumes are allowed."
      );
      return;
    }

    setLoading(true);
    setResults(null);
    setExpandedCandidate(null);
    setSearchTerm("");
    setRecommendationFilter("All");
    setCurrentPage(1);

    try {
      const formData =
        new FormData();

      formData.append(
        "job_description",
        jobDescription
      );

      files.forEach((file) => {
        formData.append(
          "resumes",
          file
        );
      });

      const response =
        await fetch(
          "http://127.0.0.1:8000/screen",
          {
            method: "POST",
            body: formData
          }
        );

      if (!response.ok) {
        const errorData =
          await response.json();

        throw new Error(
          errorData.detail ||
            "Screening failed."
        );
      }

      const data: ScreeningResponse =
        await response.json();

      setResults(data);

    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
      } else {
        setError(
          "Something went wrong."
        );
      }

    } finally {
      setLoading(false);
    }
  }


  function exportCSV() {
    if (
      !results ||
      filteredCandidates.length === 0
    ) {
      return;
    }

    const headers = [
      "Rank",
      "Candidate Name",
      "Email",
      "Phone",
      "Location",
      "File",
      "Match Score",
      "Recommendation",
      "Experience Years",
      "Experience Requirement Met",
      "Required Skills Matched",
      "Preferred Skills Matched",
      "Missing Required Skills",
      "Required Score Contribution",
      "Preferred Score Contribution",
      "Experience Score Contribution",
      "Text Similarity"
    ];


    const rows =
      filteredCandidates.map(
        ({ candidate, rank }) => {
          const phoneForCSV =
            candidate.phone
              ? `\u200E${candidate.phone}`
              : "";

          return [
            rank,
            candidate.candidate_name,
            candidate.email,
            phoneForCSV,
            candidate.location,
            candidate.file_name,
            candidate.score,
            candidate.recommendation,
            candidate.candidate_experience,
            candidate.experience_met
              ? "Yes"
              : "No",
            candidate
              .matched_required_skills
              .join("; "),
            candidate
              .matched_preferred_skills
              .join("; "),
            candidate
              .missing_required_skills
              .join("; "),
            candidate
              .score_breakdown
              .required_skills
              .contribution_points,
            candidate
              .score_breakdown
              .preferred_skills
              .contribution_points,
            candidate
              .score_breakdown
              .experience
              .contribution_points,
            candidate.text_similarity
          ];
        }
      );


    function escapeCSV(
      value: string | number
    ) {
      let text =
        String(value);

      if (/^[=+\-@]/.test(text)) {
        text = `'${text}`;
      }

      return `"${text.replace(
        /"/g,
        '""'
      )}"`;
    }


    const csvContent = [
      headers
        .map(escapeCSV)
        .join(","),

      ...rows.map((row) =>
        row
          .map(escapeCSV)
          .join(",")
      )
    ].join("\n");


    const csvWithBOM =
      "\uFEFF" + csvContent;


    const blob =
      new Blob(
        [csvWithBOM],
        {
          type:
            "text/csv;charset=utf-8;"
        }
      );


    const url =
      URL.createObjectURL(
        blob
      );


    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      "resume_screening_results.csv";

    document.body
      .appendChild(link);

    link.click();

    document.body
      .removeChild(link);

    URL.revokeObjectURL(
      url
    );
  }


  function toggleCandidate(
    fileName: string
  ) {
    if (
      expandedCandidate ===
      fileName
    ) {
      setExpandedCandidate(null);
    } else {
      setExpandedCandidate(
        fileName
      );
    }
  }


  function clearFilters() {
    setSearchTerm("");
    setRecommendationFilter("All");
    setCurrentPage(1);
  }


  function changeSearch(
    value: string
  ) {
    setSearchTerm(value);
    setCurrentPage(1);
    setExpandedCandidate(null);
  }


  function changeRecommendation(
    value: RecommendationFilter
  ) {
    setRecommendationFilter(
      value
    );

    setCurrentPage(1);
    setExpandedCandidate(null);
  }


  function changePageSize(
    value: number
  ) {
    setPageSize(value);
    setCurrentPage(1);
    setExpandedCandidate(null);
  }


  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">

      <div className="mx-auto max-w-6xl px-6 py-12">

        <header className="mb-10">

          <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-blue-600">
            Automated Resume Screening
          </p>

          <h1 className="text-4xl font-bold tracking-tight">
            Find the strongest candidates faster.
          </h1>

          <p className="mt-4 max-w-2xl text-lg text-slate-600">
            Paste a job description,
            upload candidate resumes,
            and receive an explainable
            ranked shortlist based on
            skills and experience.
          </p>

        </header>


        <section className="grid gap-6 lg:grid-cols-2">

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <div className="mb-5">

              <h2 className="text-xl font-semibold">
                1. Job Description
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Paste the role requirements
                you want candidates screened
                against.
              </p>

            </div>


            <textarea
              rows={16}
              value={jobDescription}
              onChange={(event) =>
                setJobDescription(
                  event.target.value
                )
              }
placeholder="Paste the full job description here..."
              className="w-full resize-none rounded-xl border border-slate-300 p-4 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />

          </div>


          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

            <div className="mb-5">

              <h2 className="text-xl font-semibold">
                2. Upload Resumes
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Upload PDF, DOCX, or TXT
                resumes. Maximum 500 files
                per screening.
              </p>

            </div>


            <div className="flex min-h-72 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center">

              <div>

                <div className="mb-4 text-4xl">
                  📄
                </div>

                <p className="font-medium">
                  Upload candidate resumes
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  PDF, DOCX and TXT supported
                </p>


                <label className="mt-6 inline-block cursor-pointer rounded-lg bg-slate-900 px-5 py-3 text-sm font-medium text-white hover:bg-slate-700">

                  Choose Files

                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.txt"
                    className="hidden"
                    onChange={(event) => {
                      const selected =
                        Array.from(
                          event.target.files ||
                            []
                        );

                      setFiles(
                        selected
                      );
                    }}
                  />

                </label>


                {files.length > 0 && (

                  <div className="mt-4">

                    <p className="text-sm font-semibold text-blue-600">
                      {files.length} file
                      {files.length === 1
                        ? ""
                        : "s"}{" "}
                      selected
                    </p>


                    <div className="mt-2 max-h-24 overflow-y-auto text-left text-xs text-slate-500">

                      {files.map(
                        (file, index) => (

                          <p
                            key={`${file.name}-${index}`}
                            className="truncate"
                          >
                            {file.name}
                          </p>

                        )
                      )}

                    </div>

                  </div>

                )}

              </div>

            </div>

          </div>

        </section>


        {error && (

          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>

        )}


        <div className="mt-8 flex justify-end">

          <button
            type="button"
            onClick={handleScreen}
            disabled={loading}
            className="rounded-xl bg-blue-600 px-7 py-3 font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading
              ? "Screening..."
              : "Screen Candidates"}
          </button>

        </div>


        <section className="mt-12 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

            <div>

              <h2 className="text-xl font-semibold">
                Screening Results
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Search, filter,
                review and export
                ranked candidates.
              </p>

            </div>


            <div className="flex items-center gap-3">

              {results && (

                <button
                  type="button"
                  onClick={exportCSV}
                  disabled={
                    filteredCandidates.length ===
                    0
                  }
                  className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Export CSV
                </button>

              )}


              <span className="w-fit rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-500">

                {results
                  ? `${results.summary.successfully_processed} processed`
                  : "No screening yet"}

              </span>

            </div>

          </div>


          {!results && (

            <div className="mt-8 flex min-h-40 items-center justify-center rounded-xl bg-slate-50">

              <p className="text-sm text-slate-500">
                Add a job description
                and resumes to begin.
              </p>

            </div>

          )}


          {results && (

            <div className="mt-8">

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                <SummaryCard
                  label="Strong Match"
                  value={
                    results.recommendations[
                      "Strong Match"
                    ]
                  }
                />

                <SummaryCard
                  label="Good Match"
                  value={
                    results.recommendations[
                      "Good Match"
                    ]
                  }
                />

                <SummaryCard
                  label="Review"
                  value={
                    results.recommendations[
                      "Review"
                    ]
                  }
                />

                <SummaryCard
                  label="Weak Match"
                  value={
                    results.recommendations[
                      "Weak Match"
                    ]
                  }
                />

              </div>


              <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                <MetricCard
                  label="Files received"
                  value={
                    results.summary
                      .files_received
                  }
                />

                <MetricCard
                  label="Unique resumes"
                  value={
                    results.summary
                      .unique_resumes
                  }
                />

                <MetricCard
                  label="Duplicates skipped"
                  value={
                    results.summary
                      .duplicates_skipped
                  }
                />

                <MetricCard
                  label="Failed"
                  value={
                    results.summary
                      .failed
                  }
                />

              </div>


              <ProcessingQuality
                duplicates={
                  results.duplicates
                }
                rejectedFiles={
                  results.rejected_files
                }
                failures={
                  results.failures
                }
              />


              <div className="mt-8 rounded-xl border border-slate-200 bg-slate-50 p-5">

                <div className="grid gap-4 md:grid-cols-2">

                  <div>

                    <label className="text-sm font-semibold text-slate-700">
                      Search candidates
                    </label>

                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(event) =>
                        changeSearch(
                          event.target.value
                        )
                      }
                      placeholder="Search name, email, location or file..."
                      className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />

                  </div>


                  <div>

                    <label className="text-sm font-semibold text-slate-700">
                      Recommendation
                    </label>

                    <select
                      value={
                        recommendationFilter
                      }
                      onChange={(event) =>
                        changeRecommendation(
                          event.target.value as RecommendationFilter
                        )
                      }
                      className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    >

                      <option value="All">
                        All recommendations
                      </option>

                      <option value="Strong Match">
                        Strong Match
                      </option>

                      <option value="Good Match">
                        Good Match
                      </option>

                      <option value="Review">
                        Review
                      </option>

                      <option value="Weak Match">
                        Weak Match
                      </option>

                    </select>

                  </div>

                </div>


                <div className="mt-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">

                  <p className="text-sm text-slate-600">

                    Showing{" "}

                    <span className="font-semibold text-slate-900">
                      {
                        filteredCandidates.length
                      }
                    </span>

                    {" "}of{" "}

                    <span className="font-semibold text-slate-900">
                      {
                        results.ranked_candidates
                          .length
                      }
                    </span>

                    {" "}candidates

                  </p>


                  <div className="flex flex-wrap items-center gap-3">

                    <label className="text-sm text-slate-600">
                      Candidates per page
                    </label>

                    <select
                      value={pageSize}
                      onChange={(event) =>
                        changePageSize(
                          Number(
                            event.target.value
                          )
                        )
                      }
                      className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                    >

                      <option value={10}>
                        10
                      </option>

                      <option value={25}>
                        25
                      </option>

                      <option value={50}>
                        50
                      </option>

                    </select>


                    {(searchTerm ||
                      recommendationFilter !==
                        "All") && (

                      <button
                        type="button"
                        onClick={
                          clearFilters
                        }
                        className="text-sm font-semibold text-blue-600 hover:text-blue-800"
                      >
                        Clear filters
                      </button>

                    )}

                  </div>

                </div>

              </div>


              {filteredCandidates.length ===
                0 && (

                <div className="mt-8 flex min-h-40 items-center justify-center rounded-xl border border-dashed border-slate-300">

                  <div className="text-center">

                    <p className="font-medium text-slate-700">
                      No candidates found
                    </p>

                    <p className="mt-1 text-sm text-slate-500">
                      Try changing your search
                      or recommendation filter.
                    </p>

                  </div>

                </div>

              )}


              {filteredCandidates.length > 0 && (

                <>

                  <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                    <p className="text-sm text-slate-600">

                      Showing{" "}

                      <span className="font-semibold text-slate-900">
                        {firstIndex + 1}
                      </span>

                      {" – "}

                      <span className="font-semibold text-slate-900">
                        {lastIndex}
                      </span>

                      {" "}of{" "}

                      <span className="font-semibold text-slate-900">
                        {
                          filteredCandidates.length
                        }
                      </span>

                    </p>


                    <p className="text-sm text-slate-500">

                      Page{" "}

                      <span className="font-semibold text-slate-700">
                        {safeCurrentPage}
                      </span>

                      {" "}of{" "}

                      <span className="font-semibold text-slate-700">
                        {totalPages}
                      </span>

                    </p>

                  </div>


                  <div className="mt-5 space-y-5">

                    {paginatedCandidates.map(
                      ({
                        candidate,
                        rank
                      }) => (

                        <CandidateCard
                          key={
                            candidate.file_name
                          }
                          candidate={
                            candidate
                          }
                          rank={rank}
                          expanded={
                            expandedCandidate ===
                            candidate.file_name
                          }
                          onToggle={() =>
                            toggleCandidate(
                              candidate.file_name
                            )
                          }
                        />

                      )
                    )}

                  </div>


                  <div className="mt-8 flex flex-col gap-4 border-t border-slate-200 pt-6 sm:flex-row sm:items-center sm:justify-between">

                    <button
                      type="button"
                      disabled={
                        safeCurrentPage === 1
                      }
                      onClick={() => {
                        setCurrentPage(
                          Math.max(
                            safeCurrentPage - 1,
                            1
                          )
                        );

                        setExpandedCandidate(
                          null
                        );
                      }}
                      className="rounded-lg border border-slate-300 bg-white px-5 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Previous
                    </button>


                    <p className="text-center text-sm text-slate-600">

                      Page{" "}

                      <span className="font-semibold text-slate-900">
                        {safeCurrentPage}
                      </span>

                      {" "}of{" "}

                      <span className="font-semibold text-slate-900">
                        {totalPages}
                      </span>

                    </p>


                    <button
                      type="button"
                      disabled={
                        safeCurrentPage ===
                        totalPages
                      }
                      onClick={() => {
                        setCurrentPage(
                          Math.min(
                            safeCurrentPage + 1,
                            totalPages
                          )
                        );

                        setExpandedCandidate(
                          null
                        );
                      }}
                      className="rounded-lg border border-slate-300 bg-white px-5 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Next
                    </button>

                  </div>

                </>

              )}

            </div>

          )}

        </section>

      </div>

    </main>
  );
}


function CandidateCard({
  candidate,
  rank,
  expanded,
  onToggle
}: {
  candidate: Candidate;
  rank: number;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="rounded-xl border border-slate-200 p-5">

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

        <div>

          <p className="text-sm font-semibold text-blue-600">
            Rank #{rank}
          </p>

          <h3 className="mt-1 text-xl font-semibold">
            {candidate.candidate_name}
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            {candidate.email}
            {" • "}
            {candidate.location}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {candidate.file_name}
          </p>

        </div>


        <div className="text-left md:text-right">

          <p className="text-2xl font-bold">
            {candidate.score}%
          </p>

          <p className="text-sm font-medium text-slate-600">
            {candidate.recommendation}
          </p>

        </div>

      </div>


      <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">

        <InfoCard
          label="Experience"
          main={`${candidate.candidate_experience} years`}
          detail={
            candidate.experience_met
              ? "Minimum experience met"
              : "Minimum experience not met"
          }
        />

        <InfoCard
          label="Required Matched"
          main={`${candidate.matched_required_skills.length} skills`}
          detail={
            candidate
              .matched_required_skills
              .length === 0
              ? "None"
              : candidate
                  .matched_required_skills
                  .join(", ")
          }
        />

        <InfoCard
          label="Preferred Matched"
          main={`${candidate.matched_preferred_skills.length} skills`}
          detail={
            candidate
              .matched_preferred_skills
              .length === 0
              ? "None"
              : candidate
                  .matched_preferred_skills
                  .join(", ")
          }
        />

        <InfoCard
          label="Missing Required"
          main={
            candidate
              .missing_required_skills
              .length === 0
              ? "None"
              : candidate
                  .missing_required_skills
                  .join(", ")
          }
        />

      </div>


      <div className="mt-4 flex flex-col gap-2 rounded-lg border border-slate-100 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">

        <div>

          <p className="text-sm font-medium text-slate-600">
            Text similarity
          </p>

          <p className="text-xs text-slate-400">
            Secondary ranking signal
            based on JD–resume wording
            overlap
          </p>

        </div>

        <p className="text-sm font-semibold text-slate-600">
          {candidate.text_similarity}%
        </p>

      </div>


      <button
        type="button"
        onClick={onToggle}
        className="mt-4 text-sm font-semibold text-blue-600 hover:text-blue-800"
      >
        {expanded
          ? "Hide details"
          : "View details"}
      </button>


      {expanded && (

        <div className="mt-4 space-y-6 rounded-xl bg-slate-50 p-5">

          <div>

            <h4 className="font-semibold">
              Candidate Details
            </h4>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">

              <DetailRow
                label="Full name"
                value={
                  candidate.candidate_name
                }
              />

              <DetailRow
                label="Email"
                value={
                  candidate.email
                }
              />

              <DetailRow
                label="Phone"
                value={
                  candidate.phone ||
                  "Not found"
                }
              />

              <DetailRow
                label="Location"
                value={
                  candidate.location ||
                  "Not found"
                }
              />

              <DetailRow
                label="Resume file"
                value={
                  candidate.file_name
                }
              />

              <DetailRow
                label="Recommendation"
                value={
                  candidate.recommendation
                }
              />

              <DetailRow
                label="Required skills matched"
                value={
                  candidate
                    .matched_required_skills
                    .length === 0
                    ? "None"
                    : candidate
                        .matched_required_skills
                        .join(", ")
                }
              />

              <DetailRow
                label="Preferred skills matched"
                value={
                  candidate
                    .matched_preferred_skills
                    .length === 0
                    ? "None"
                    : candidate
                        .matched_preferred_skills
                        .join(", ")
                }
              />

              <DetailRow
                label="Missing required skills"
                value={
                  candidate
                    .missing_required_skills
                    .length === 0
                    ? "None"
                    : candidate
                        .missing_required_skills
                        .join(", ")
                }
              />

              <DetailRow
                label="Experience requirement"
                value={
                  candidate.experience_met
                    ? "Met"
                    : "Not met"
                }
              />

            </div>

          </div>


          <ScoreExplanation
            candidate={candidate}
          />

        </div>

      )}

    </div>
  );
}


function ScoreExplanation({
  candidate
}: {
  candidate: Candidate;
}) {
  const breakdown =
    candidate.score_breakdown;

  return (
    <div className="border-t border-slate-200 pt-6">

      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">

        <div>

          <h4 className="font-semibold">
            Why this score?
          </h4>

          <p className="mt-1 text-sm text-slate-500">
            The match score is calculated
            from required skills,
            preferred skills, and
            minimum experience.
          </p>

        </div>


        <div className="text-left sm:text-right">

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Match Score
          </p>

          <p className="text-2xl font-bold text-slate-900">
            {
              breakdown.final_score
            }
            %
          </p>

        </div>

      </div>


      <div className="mt-5 grid gap-4 lg:grid-cols-3">

        <ScoreFactorCard
          title="Required Skills"
          primary={
            `${breakdown.required_skills.matched}/${breakdown.required_skills.total} matched`
          }
          matchPercentage={
            breakdown.required_skills
              .match_percentage
          }
          weightPercentage={
            breakdown.required_skills
              .weight_percentage
          }
          contribution={
            breakdown.required_skills
              .contribution_points
          }
        />


        <ScoreFactorCard
          title="Preferred Skills"
          primary={
            `${breakdown.preferred_skills.matched}/${breakdown.preferred_skills.total} matched`
          }
          matchPercentage={
            breakdown.preferred_skills
              .match_percentage
          }
          weightPercentage={
            breakdown.preferred_skills
              .weight_percentage
          }
          contribution={
            breakdown.preferred_skills
              .contribution_points
          }
        />


        <ScoreFactorCard
          title="Experience"
          primary={
            `${breakdown.experience.candidate_years} years vs ${breakdown.experience.minimum_years} required`
          }
          matchPercentage={
            breakdown.experience
              .match_percentage
          }
          weightPercentage={
            breakdown.experience
              .weight_percentage
          }
          contribution={
            breakdown.experience
              .contribution_points
          }
        />

      </div>


      <div className="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4">

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">

          <div>

            <p className="font-semibold text-blue-900">
              Score calculation
            </p>

            <p className="mt-1 text-sm text-blue-700">
              {
                breakdown.required_skills
                  .contribution_points
              }
              {" + "}
              {
                breakdown.preferred_skills
                  .contribution_points
              }
              {" + "}
              {
                breakdown.experience
                  .contribution_points
              }
              {" = "}
              {
                breakdown.final_score
              }
              {" points"}
            </p>

          </div>


          <p className="text-xl font-bold text-blue-900">
            {
              breakdown.final_score
            }
            %
          </p>

        </div>

      </div>


      <RecommendationExplanation
        candidate={candidate}
      />

    </div>
  );
}


function ScoreFactorCard({
  title,
  primary,
  matchPercentage,
  weightPercentage,
  contribution
}: {
  title: string;
  primary: string;
  matchPercentage: number;
  weightPercentage: number;
  contribution: number;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </p>

      <p className="mt-2 font-semibold text-slate-900">
        {primary}
      </p>

      <div className="mt-4 space-y-2 text-sm">

        <div className="flex justify-between gap-4">

          <span className="text-slate-500">
            Match
          </span>

          <span className="font-medium">
            {matchPercentage}%
          </span>

        </div>


        <div className="flex justify-between gap-4">

          <span className="text-slate-500">
            Weight
          </span>

          <span className="font-medium">
            {weightPercentage}%
          </span>

        </div>


        <div className="flex justify-between gap-4 border-t border-slate-100 pt-2">

          <span className="text-slate-500">
            Contribution
          </span>

          <span className="font-semibold text-blue-600">
            +{contribution}
          </span>

        </div>

      </div>

    </div>
  );
}


function RecommendationExplanation({
  candidate
}: {
  candidate: Candidate;
}) {
  const hasMissingRequired =
    candidate
      .missing_required_skills
      .length > 0;

  const failedMinimum =
    hasMissingRequired ||
    !candidate.experience_met;


  if (failedMinimum) {
    return (
      <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4">

        <p className="font-semibold text-amber-900">
          Why the recommendation is{" "}
          {candidate.recommendation}
        </p>

        <p className="mt-1 text-sm text-amber-800">
          The numerical match score does
          not override minimum job
          requirements.
        </p>


        <div className="mt-3 space-y-1 text-sm text-amber-900">

          {hasMissingRequired && (

            <p>
              Missing required skill
              {candidate
                .missing_required_skills
                .length === 1
                ? ""
                : "s"}
              :{" "}
              {
                candidate
                  .missing_required_skills
                  .join(", ")
              }
            </p>

          )}


          {!candidate.experience_met && (

            <p>
              Minimum experience requirement
              was not met.
            </p>

          )}

        </div>

      </div>
    );
  }


  return (
    <div className="mt-5 rounded-xl border border-green-200 bg-green-50 p-4">

      <p className="font-semibold text-green-900">
        Minimum requirements satisfied
      </p>

      <p className="mt-1 text-sm text-green-800">
        All required skills and the
        minimum experience requirement
        were met. The recommendation
        therefore follows the configured
        score thresholds.
      </p>

    </div>
  );
}


function ProcessingQuality({
  duplicates,
  rejectedFiles,
  failures
}: {
  duplicates: DuplicateFile[];
  rejectedFiles: RejectedFile[];
  failures: FailedFile[];
}) {
  const hasIssues =
    duplicates.length > 0 ||
    rejectedFiles.length > 0 ||
    failures.length > 0;


  if (!hasIssues) {
    return (
      <div className="mt-6 rounded-xl border border-green-200 bg-green-50 p-5">

        <p className="font-semibold text-green-800">
          Processing completed cleanly
        </p>

        <p className="mt-1 text-sm text-green-700">
          No duplicate,
          unsupported,
          or failed resume files
          were detected.
        </p>

      </div>
    );
  }


  return (
    <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-5">

      <h3 className="font-semibold text-amber-900">
        Processing notices
      </h3>

      <p className="mt-1 text-sm text-amber-800">
        Some uploaded files needed
        special handling.
      </p>


      <div className="mt-5 grid gap-4 lg:grid-cols-3">

        <IssuePanel
          title="Duplicates"
          count={
            duplicates.length
          }
        >

          {duplicates.length === 0 ? (

            <p className="text-sm text-slate-500">
              None
            </p>

          ) : (

            duplicates.map(
              (
                duplicate,
                index
              ) => (

                <div
                  key={`${duplicate.file_name}-${index}`}
                  className="text-sm"
                >

                  <p className="font-medium text-slate-800">
                    {
                      duplicate.file_name
                    }
                  </p>

                  <p className="text-xs text-slate-500">
                    Duplicate of{" "}
                    {
                      duplicate.duplicate_of
                    }
                  </p>

                </div>

              )
            )

          )}

        </IssuePanel>


        <IssuePanel
          title="Unsupported"
          count={
            rejectedFiles.length
          }
        >

          {rejectedFiles.length ===
          0 ? (

            <p className="text-sm text-slate-500">
              None
            </p>

          ) : (

            rejectedFiles.map(
              (
                rejected,
                index
              ) => (

                <div
                  key={`${rejected.file_name}-${index}`}
                  className="text-sm"
                >

                  <p className="font-medium text-slate-800">
                    {
                      rejected.file_name
                    }
                  </p>

                  <p className="text-xs text-slate-500">
                    {
                      rejected.reason
                    }
                  </p>

                </div>

              )
            )

          )}

        </IssuePanel>


        <IssuePanel
          title="Failed"
          count={
            failures.length
          }
        >

          {failures.length === 0 ? (

            <p className="text-sm text-slate-500">
              None
            </p>

          ) : (

            failures.map(
              (
                failure,
                index
              ) => (

                <div
                  key={`${failure.file_name}-${index}`}
                  className="text-sm"
                >

                  <p className="font-medium text-slate-800">
                    {
                      failure.file_name
                    }
                  </p>

                  <p className="break-words text-xs text-slate-500">
                    {
                      failure.error
                    }
                  </p>

                </div>

              )
            )

          )}

        </IssuePanel>

      </div>

    </div>
  );
}


function IssuePanel({
  title,
  count,
  children
}: {
  title: string;
  count: number;
  children: ReactNode;
}) {
  return (
    <div className="rounded-lg border border-amber-200 bg-white p-4">

      <div className="mb-3 flex items-center justify-between">

        <p className="font-semibold text-slate-800">
          {title}
        </p>

        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
          {count}
        </span>

      </div>

      <div className="space-y-3">
        {children}
      </div>

    </div>
  );
}


function SummaryCard({
  label,
  value
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">

      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-2xl font-bold">
        {value}
      </p>

    </div>
  );
}


function MetricCard({
  label,
  value
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl border border-slate-200 p-4">

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-lg font-semibold">
        {value}
      </p>

    </div>
  );
}


function InfoCard({
  label,
  main,
  detail
}: {
  label: string;
  main: string;
  detail?: string;
}) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 font-medium">
        {main}
      </p>

      {detail && (

        <p className="mt-1 text-xs text-slate-500">
          {detail}
        </p>

      )}

    </div>
  );
}


function DetailRow({
  label,
  value
}: {
  label: string;
  value: string;
}) {
  return (
    <div>

      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-sm text-slate-800">
        {value}
      </p>

    </div>
  );
}