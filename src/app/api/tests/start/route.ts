import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/store';
import { ApiResponse, TestSession, TestStatus, Question, Option } from '@/lib/types';

// POST /api/tests/start - Create a new test session
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { student_id, test_name, subject_filter, total_questions, questions, time_limit_minutes } = body;

    if (!student_id || !test_name) {
      return NextResponse.json(
        { success: false, error: 'student_id and test_name are required' },
        { status: 400 }
      );
    }

    const testId = `test_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    let testQuestions: Question[] = [];
    if (questions && Array.isArray(questions) && questions.length > 0) {
      testQuestions = questions;
    } else if (total_questions) {
      for (let i = 0; i < Math.min(total_questions, 100); i++) {
        const options: Option[] = [
          { id: 'a', text: `Option A for Q${i + 1}` },
          { id: 'b', text: `Option B for Q${i + 1}` },
          { id: 'c', text: `Option C for Q${i + 1}` },
          { id: 'd', text: `Option D for Q${i + 1}` },
        ];
        testQuestions.push({
          id: `q_${testId}_${i + 1}`,
          subject: subject_filter?.[i % (subject_filter?.length || 1)] || 'General Studies',
          topic: `Topic ${(i % 10) + 1}`,
          difficulty: ['easy', 'medium', 'hard'][i % 3] as 'easy' | 'medium' | 'hard',
          question_text: `Question ${i + 1} for ${test_name}`,
          options,
          correct_option_id: ['a', 'b', 'c', 'd'][i % 4],
          explanation: `Explanation for question ${i + 1}`,
          marks: 2,
          negative_marks: 0.66,
        });
      }
    }

    const testSession: TestSession = {
      id: testId,
      student_id,
      test_name,
      subject_filter,
      total_questions: testQuestions.length,
      questions: testQuestions,
      status: 'pending' as TestStatus,
      created_at: new Date().toISOString(),
      time_limit_minutes: time_limit_minutes || 120,
    };

    db.createTestSession(testSession);

    const response: ApiResponse<TestSession> = {
      success: true,
      data: testSession,
      message: 'Test session created successfully',
    };

    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    console.error('Error creating test session:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to create test session' },
      { status: 500 }
    );
  }
}
