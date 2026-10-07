import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    name: "Demo Student",
    email: "student@upscacademy.com",
    joinDate: "January 2026",
    testsCompleted: 5,
    totalQuestions: 100,
    avgAccuracy: 52,
    strongAreas: [
      { topic: "Geography", accuracy: 85 },
      { topic: "Science", accuracy: 78 },
    ],
    weakAreas: [
      { topic: "Polity", accuracy: 35 },
      { topic: "Economy", accuracy: 42 },
    ],
    improvementTrend: [
      { month: "Jan", accuracy: 30 },
      { month: "Feb", accuracy: 38 },
      { month: "Mar", accuracy: 45 },
      { month: "Apr", accuracy: 52 },
    ],
    subjectPerformance: [
      { name: "Polity", correct: 15, wrong: 12, skipped: 3, color: "#ef4444" },
      { name: "Economy", correct: 20, wrong: 8, skipped: 2, color: "#f59e0b" },
      { name: "Geography", correct: 25, wrong: 5, skipped: 0, color: "#10b981" },
      { name: "Science", correct: 18, wrong: 7, skipped: 1, color: "#3b82f6" },
      { name: "Environment", correct: 12, wrong: 10, skipped: 2, color: "#8b5cf6" },
      { name: "History", correct: 22, wrong: 6, skipped: 1, color: "#ec4899" },
    ],
    recentActivity: [
      { date: "2026-10-07", action: "Completed Polity Test", details: "Score: 12/20" },
      { date: "2026-10-06", action: "Started Economy Sectional", details: "In progress" },
      { date: "2026-10-05", action: "Reviewed mistakes", details: "5 cards reviewed" },
    ],
  });
}
