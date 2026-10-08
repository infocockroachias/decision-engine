"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Navigation from "@/components/Navigation";
import ScoreCard from "@/components/ScoreCard";
import MistakeCard from "@/components/MistakeCard";
import SubjectPieChart from "@/components/SubjectPieChart";
import RecommendationList from "@/components/RecommendationList";

interface MistakeData {
  questionNumber: number;
  questionText: string;
  userAnswer: string;
  correctAnswer: string;
  explanation: string;
  topic: string;
  difficulty: "easy" | "medium" | "hard";
  missedReason?: string;
}

interface SubjectPerformance {
  name: string;
  correct: number;
  wrong: number;
  skipped: number;
  color: string;
}

interface Recommendation {
  id: string;
  type: "improvement" | "strength" | "practice" | "resource";
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  subject?: string;
}

interface ResultsData {
  testId: string;
  title: string;
  score: number;
  maxScore: number;
  correct: number;
  wrong: number;
  skipped: number;
  timeTaken: string;
  percentile?: number;
  mistakes: MistakeData[];
  subjectPerformance: SubjectPerformance[];
  recommendations: Recommendation[];
}

export default function ResultsPage() {
  const params = useParams();
  const testId = params.id as string;

  const [results, setResults] = useState<ResultsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "mistakes" | "recommendations">("overview");

  useEffect(() => {
    async function fetchResults() {
      try {
        const res = await fetch(`/api/tests/${testId}/results`);
        if (!res.ok) throw new Error("Failed to fetch results");
        const data = await res.json();
        setResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    fetchResults();
  }, [testId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage="tests" />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand/30 border-t-brand" />
              <p className="mt-4 text-sm text-slate-500">Loading results...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage="tests" />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="text-red-700 font-medium">{error || "Results not found"}</p>
          </div>
        </main>
      </div>
    );
  }

  const accuracy = Math.round((results.correct / (results.correct + results.wrong + results.skipped)) * 100);

  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation currentPage="tests" />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Test Results</h1>
            <p className="text-slate-500">{results.title}</p>
          </div>
        </div>

        {/* Score Summary */}
        <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-5">
          <ScoreCard label="Score" value={`${results.score}/${results.maxScore}`} variant="default" />
          <ScoreCard label="Correct" value={results.correct} variant="correct" />
          <ScoreCard label="Wrong" value={results.wrong} variant="wrong" />
          <ScoreCard label="Skipped" value={results.skipped} variant="warning" />
          <ScoreCard label="Accuracy" value={`${accuracy}%`} variant="default" />
        </div>

        {/* Tabs */}
        <div className="mb-6 border-b border-slate-200">
          <div className="flex gap-1" role="tablist">
            {(["overview", "mistakes", "recommendations"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-all capitalize
                  ${activeTab === tab ? "border-brand text-brand" : "border-transparent text-slate-500 hover:text-slate-700"}`}
                role="tab"
                aria-selected={activeTab === tab}
              >
                {tab === "mistakes" ? "Mistake Analysis" : tab}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <SubjectPieChart data={results.subjectPerformance} title="Subject-wise Breakdown" />

            {/* Quick Stats */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-semibold text-slate-900">Test Summary</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="text-center p-4 rounded-lg bg-slate-50">
                  <p className="text-sm text-slate-500">Time Taken</p>
                  <p className="text-lg font-bold text-slate-900">{results.timeTaken}</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-slate-50">
                  <p className="text-sm text-slate-500">Questions Attempted</p>
                  <p className="text-lg font-bold text-slate-900">{results.correct + results.wrong}/{results.correct + results.wrong + results.skipped}</p>
                </div>
                {results.percentile && (
                  <div className="text-center p-4 rounded-lg bg-slate-50">
                    <p className="text-sm text-slate-500">Estimated Percentile</p>
                    <p className="text-lg font-bold text-brand">{results.percentile}th</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "mistakes" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-slate-900">
                Mistake Analysis ({results.mistakes.length} errors)
              </h3>
            </div>
            {results.mistakes.length > 0 ? (
              results.mistakes.map((mistake, index) => (
                <MistakeCard key={index} {...mistake} />
              ))
            ) : (
              <div className="rounded-xl border border-green-200 bg-green-50 p-8 text-center">
                <p className="text-green-700 font-medium text-lg">Perfect Score! 🎉</p>
                <p className="text-sm text-green-600 mt-1">No mistakes found in this test.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === "recommendations" && (
          <RecommendationList recommendations={results.recommendations} />
        )}
      </main>
    </div>
  );
}
