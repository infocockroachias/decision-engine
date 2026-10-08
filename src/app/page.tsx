"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import ScoreCard from "@/components/ScoreCard";
import SubjectPieChart from "@/components/SubjectPieChart";
import FocusArea from "@/components/FocusArea";
import TestItem from "@/components/TestItem";

interface SubjectData {
  name: string;
  correct: number;
  wrong: number;
  skipped: number;
  color: string;
}

interface FocusAreaData {
  topic: string;
  accuracy: number;
  questionsAttempted: number;
  trend: "improving" | "declining" | "stable";
}

interface TestData {
  id: string;
  title: string;
  date: string;
  score: number;
  totalMarks: number;
  subjects: string[];
  status: "completed" | "in-progress" | "pending";
}

export default function DashboardPage() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [dashboardData, setDashboardData] = useState<{
    overallStats: { totalTests: number; avgAccuracy: number; bestScore: number; streak: number };
    subjectPerformance: SubjectData[];
    focusAreas: FocusAreaData[];
    recentTests: TestData[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const res = await fetch("/api/dashboard");
        if (!res.ok) throw new Error("Failed to fetch dashboard data");
        const data = await res.json();
        setDashboardData(data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand/30 border-t-brand" />
              <p className="mt-4 text-sm text-slate-500">Loading dashboard...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="text-red-700 font-medium">{error}</p>
            <p className="text-sm text-red-500 mt-2">Please try again later.</p>
          </div>
        </main>
      </div>
    );
  }

  const data = dashboardData;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
            Welcome back, Aspirant! 🎯
          </h1>
          <p className="mt-1 text-slate-500">
            Here&apos;s your preparation overview
          </p>
        </div>

        {/* Stats Grid */}
        <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <ScoreCard label="Total Tests" value={data?.overallStats.totalTests ?? 0} sublabel="Mock tests taken" />
          <ScoreCard label="Avg Accuracy" value={`${data?.overallStats.avgAccuracy ?? 0}%`} sublabel="Overall performance" variant="correct" />
          <ScoreCard label="Best Score" value={data?.overallStats.bestScore ?? 0} sublabel="Highest marks scored" variant="warning" />
          <ScoreCard label="Study Streak" value={`${data?.overallStats.streak ?? 0} days`} sublabel="Consecutive days" variant="default" />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Subject Performance */}
          <div className="lg:col-span-2">
            <SubjectPieChart data={data?.subjectPerformance ?? []} />
          </div>

          {/* Focus Areas */}
          <div className="lg:col-span-1">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-semibold text-slate-900">Focus Areas</h3>
              <div className="space-y-4">
                {data?.focusAreas.map((area) => (
                  <FocusArea
                    key={area.topic}
                    topic={area.topic}
                    accuracy={area.accuracy}
                    questionsAttempted={area.questionsAttempted}
                    trend={area.trend}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Tests */}
        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-slate-900">Recent Tests</h2>
            <button
              onClick={() => setCurrentPage("tests")}
              className="text-sm font-medium text-brand hover:text-brand-dark"
            >
              View all →
            </button>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data?.recentTests.map((test) => (
              <TestItem
                key={test.id}
                {...test}
                onResume={() => setCurrentPage(`test-${test.id}`)}
                onViewResults={() => setCurrentPage(`results-${test.id}`)}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}