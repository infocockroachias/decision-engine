"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import Timer from "@/components/Timer";
import QuestionCard from "@/components/QuestionCard";
import QuestionPalette from "@/components/QuestionPalette";
import Navigation from "@/components/Navigation";

interface Option {
  id: string;
  text: string;
}

interface Question {
  id: string;
  number: number;
  text: string;
  options: Option[];
  imageUrl?: string;
}

interface TestDetails {
  id: string;
  title: string;
  totalQuestions: number;
  durationMinutes: number;
  subjects: string[];
}

export default function TestPage() {
  const params = useParams();
  const testId = params.id as string;

  const [test, setTest] = useState<TestDetails | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<number, { option: string; marked: boolean }>>({});
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [secondsRemaining, setSecondsRemaining] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function fetchTest() {
      try {
        const res = await fetch(`/api/tests/${testId}`);
        if (!res.ok) throw new Error("Failed to fetch test details");
        const data = await res.json();
        setTest(data.test);
        setQuestions(data.questions);
        setSecondsRemaining(data.test.durationMinutes * 60);
        setIsRunning(true);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    fetchTest();
  }, [testId]);

  const handleSelectOption = useCallback((optionId: string) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion]: {
        ...prev[currentQuestion],
        option: optionId,
      },
    }));
  }, [currentQuestion]);

  const handleMarkForReview = useCallback(() => {
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion]: {
        ...prev[currentQuestion],
        option: prev[currentQuestion]?.option || "",
        marked: !prev[currentQuestion]?.marked,
      },
    }));
  }, [currentQuestion]);

  const handleTimeUp = useCallback(() => {
    setIsRunning(false);
    setShowSubmitModal(true);
  }, []);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      // For demo: navigate to results page with testId
      window.location.href = `/tests/${testId}/results`;
    } catch (err) {
      setError("Submission failed");
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage="tests" />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand/30 border-t-brand" />
              <p className="mt-4 text-sm text-slate-500">Loading test...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation currentPage="tests" />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        </main>
      </div>
    );
  }

  const currentQ = questions.find((q) => q.number === currentQuestion);
  const answeredCount = Object.values(answers).filter((a) => a.option).length;
  const markedCount = Object.values(answers).filter((a) => a.marked).length;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navigation currentPage="tests" />

      {/* Test Header */}
      <div className="sticky top-16 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto max-w-6xl px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-sm sm:text-base font-semibold text-slate-900 truncate">{test?.title}</h1>
              <p className="text-xs text-slate-500 hidden sm:block">{test?.subjects.join(", ")}</p>
            </div>
            <Timer
              secondsRemaining={secondsRemaining}
              isRunning={isRunning}
              onTimeUp={handleTimeUp}
              onTick={(remaining) => setSecondsRemaining(remaining)}
            />
          </div>
        </div>
      </div>

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-4">
          {/* Question Area */}
          <div className="lg:col-span-3">
            {currentQ && (
              <QuestionCard
                questionNumber={currentQ.number}
                totalQuestions={test?.totalQuestions ?? 0}
                questionText={currentQ.text}
                options={currentQ.options}
                selectedOption={answers[currentQ.number]?.option || null}
                onSelect={handleSelectOption}
                onMarkForReview={handleMarkForReview}
                isMarkedForReview={answers[currentQ.number]?.marked || false}
                imageUrl={currentQ.imageUrl}
              />
            )}

            {/* Navigation Buttons */}
            <div className="mt-4 flex items-center justify-between">
              <button
                onClick={() => setCurrentQuestion((q) => Math.max(1, q - 1))}
                disabled={currentQuestion <= 1}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                ← Previous
              </button>
              <span className="text-sm text-slate-500">
                {currentQuestion} / {test?.totalQuestions}
              </span>
              <button
                onClick={() => setCurrentQuestion((q) => Math.min(test?.totalQuestions ?? 1, q + 1))}
                disabled={currentQuestion >= (test?.totalQuestions ?? 1)}
                className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                Next →
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <QuestionPalette
              totalQuestions={test?.totalQuestions ?? 0}
              currentQuestion={currentQuestion}
              answers={answers}
              onNavigate={setCurrentQuestion}
            />

            {/* Submit Button */}
            <button
              onClick={() => setShowSubmitModal(true)}
              className="w-full rounded-xl bg-brand px-4 py-3 text-sm font-semibold text-white hover:bg-brand-dark transition-all shadow-sm"
            >
              Submit Test
            </button>
          </div>
        </div>
      </main>

      {/* Submit Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true" aria-labelledby="submit-title">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h2 id="submit-title" className="text-lg font-bold text-slate-900 mb-2">Submit Test?</h2>
            <div className="space-y-2 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Answered</span>
                <span className="font-semibold text-green-700">{answeredCount}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Marked for Review</span>
                <span className="font-semibold text-amber-700">{markedCount}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Not Attempted</span>
                <span className="font-semibold text-slate-700">{(test?.totalQuestions ?? 0) - answeredCount}</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowSubmitModal(false)}
                className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-all"
                disabled={submitting}
              >
                Continue Test
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="flex-1 rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-dark transition-all disabled:opacity-50"
              >
                {submitting ? "Submitting..." : "Submit"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
