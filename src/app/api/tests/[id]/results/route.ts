import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    testId: "demo-test-001",
    title: "UPSC Prelims Mock Test - Demo",
    score: 8,
    maxScore: 20,
    correct: 8,
    wrong: 2,
    skipped: 0,
    timeTaken: "18:42",
    percentile: 65,
    mistakes: [
      {
        questionNumber: 3,
        questionText: "The Ring of Fire is associated with:",
        userAnswer: "Atlantic Ocean",
        correctAnswer: "Pacific Ocean",
        explanation: "The Ring of Fire is in the Pacific Ocean with 75% of active volcanoes and 90% of earthquakes.",
        topic: "Geography",
        difficulty: "medium",
        missedReason: "Confused Pacific with Atlantic",
      },
      {
        questionNumber: 6,
        questionText: "Which is NOT a quantitative tool of RBI?",
        userAnswer: "Bank Rate",
        correctAnswer: "Margin Requirements",
        explanation: "Margin requirements are qualitative/selective credit control, not quantitative.",
        topic: "Economy",
        difficulty: "medium",
        missedReason: "Confused qualitative with quantitative tools",
      },
    ],
    subjectPerformance: [
      { name: "Polity", correct: 3, wrong: 0, skipped: 0, color: "#10b981" },
      { name: "Economy", correct: 1, wrong: 1, skipped: 0, color: "#f59e0b" },
      { name: "Geography", correct: 2, wrong: 1, skipped: 0, color: "#3b82f6" },
      { name: "Science", correct: 1, wrong: 0, skipped: 0, color: "#8b5cf6" },
      { name: "Environment", correct: 1, wrong: 0, skipped: 0, color: "#ec4899" },
    ],
    recommendations: [
      {
        id: "rec-1",
        type: "improvement",
        title: "Improve Economy",
        description: "Focus on RBI monetary policy tools. Quantitative vs qualitative distinction is frequently tested.",
        priority: "high",
        subject: "Economy",
      },
      {
        id: "rec-2",
        type: "improvement",
        title: "Improve Geography",
        description: "Review physical geography concepts. Ring of Fire, ocean currents, and tectonic features are important.",
        priority: "high",
        subject: "Geography",
      },
      {
        id: "rec-3",
        type: "strength",
        title: "Maintain Polity",
        description: "Your polity accuracy is 100%. Keep it up with current affairs linkage.",
        priority: "low",
        subject: "Polity",
      },
      {
        id: "rec-4",
        type: "practice",
        title: "Practice More Tests",
        description: "Take 2+ full-length mocks per week to improve speed and accuracy.",
        priority: "medium",
      },
    ],
  });
}
