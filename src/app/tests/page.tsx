"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navigation from "@/components/Navigation";
import TestItem from "@/components/TestItem";

interface TestData {
  id: string;
  title: string;
  date: string;
  score: number;
  totalMarks: number;
  subjects: string[];
  status: "completed" | "in-progress" | "pending";
}

export default function TestsListPage() {
  const router = useRouter();
  const [tests, setTests] = useState<TestData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Demo tests data
    const demoTests: TestData[] = [
      {
        id: "demo-test-001",
        title: "UPSC Prelims Mock Test - Demo",
        date: "2026-10-07",
        score: 12,
        totalMarks: 20,
        subjects: ["Polity", "Economy", "Geography", "Science", "Environment"],
        status: "pending",
      },
      {
        id: "test-001",
        title: "UPSC Prelims Mock - Full Length",
        date: "2026-10-07",
        score: 18,
        totalMarks: 40,
        subjects: ["Polity", "Economy", "Geography"],
        status: "completed",
      },
      {
        id: "test-002",
        title: "Polity Sectional Test",
        date: "2026-10-06",
        score: 12,
        totalMarks: 20,
        subjects: ["Polity"],
        status: "completed",
      },
      {
        id: "test-003",
        title: "Economy & Environment",
        date: "2026-10-05",
        score: 14,
        totalMarks: 20,
        subjects: ["Economy", "Environment"],
        status: "completed",
      },
      {
        id: "test-004",
        title: "Geography & Science",
        date: "2026-10-04",
        score: 0,
        totalMarks: 20,
        subjects: ["Geography", "Science"],
        status: "in-progress",
      },
    ];
    setTests(demoTests);
    setLoading(false);
  }, []);

  const pendingTests = tests.filter(t => t.status === "pending" || t.status === "in-progress");
  const completedTests = tests.filter(t => t.status === "completed");

  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation currentPage="tests" />
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900">Tests</h1>
          <p className="mt-1 text-slate-500">Take mock tests and track your progress</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center min-h-[40vh]">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand/30 border-t-brand" />
          </div>
        ) : (
          <>
            {/* Available Tests */}
            {pendingTests.length > 0 && (
              <div className="mb-8">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Available Tests</h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {pendingTests.map((test) => (
                    <TestItem
                      key={test.id}
                      {...test}
                      onResume={() => router.push(`/tests/${test.id}`)}
                      onViewResults={() => router.push(`/tests/${test.id}/results`)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Completed Tests */}
            {completedTests.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Completed Tests</h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {completedTests.map((test) => (
                    <TestItem
                      key={test.id}
                      {...test}
                      onResume={() => router.push(`/tests/${test.id}`)}
                      onViewResults={() => router.push(`/tests/${test.id}/results`)}
                    />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
