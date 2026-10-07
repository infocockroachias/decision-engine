import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    success: true,
    data: {
      overallStats: {
        totalTests: 5,
        avgAccuracy: 52,
        bestScore: 18,
        streak: 3,
      },
      subjectPerformance: [
        { name: 'Polity', correct: 15, wrong: 12, skipped: 3, color: '#ef4444' },
        { name: 'Economy', correct: 20, wrong: 8, skipped: 2, color: '#f59e0b' },
        { name: 'Geography', correct: 25, wrong: 5, skipped: 0, color: '#10b981' },
        { name: 'Science', correct: 18, wrong: 7, skipped: 1, color: '#3b82f6' },
        { name: 'Environment', correct: 12, wrong: 10, skipped: 2, color: '#8b5cf6' },
        { name: 'History', correct: 22, wrong: 6, skipped: 1, color: '#ec4899' },
      ],
      focusAreas: [
        { topic: 'Fundamental Rights', accuracy: 35, questionsAttempted: 8, trend: 'declining' },
        { topic: 'Banking', accuracy: 42, questionsAttempted: 6, trend: 'improving' },
        { topic: 'Climatology', accuracy: 65, questionsAttempted: 5, trend: 'stable' },
        { topic: 'Budgeting', accuracy: 28, questionsAttempted: 7, trend: 'declining' },
      ],
      recentTests: [
        {
          id: 'test-001',
          title: 'UPSC Prelims Mock - Full Length',
          date: '2026-10-07',
          score: 18,
          totalMarks: 40,
          subjects: ['Polity', 'Economy', 'Geography'],
          status: 'completed',
        },
        {
          id: 'test-002',
          title: 'Polity Sectional Test',
          date: '2026-10-06',
          score: 12,
          totalMarks: 20,
          subjects: ['Polity'],
          status: 'completed',
        },
        {
          id: 'test-003',
          title: 'Economy & Environment',
          date: '2026-10-05',
          score: 14,
          totalMarks: 20,
          subjects: ['Economy', 'Environment'],
          status: 'completed',
        },
      ],
    },
  });
}
