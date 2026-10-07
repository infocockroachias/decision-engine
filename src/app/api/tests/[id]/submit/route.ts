import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/store';
import { getLayaEngine } from '@/lib';
import { ApiResponse, TestSubmission, TestAnalysis, StudentResponse } from '@/lib/types';

// POST /api/tests/[id]/submit - Submit responses and trigger analysis
export async function POST(
  req: NextRequest,
  props: { params: Promise<{ id: string }> }
) {
  try {
    const { id: testId } = await props.params;
    const body = await req.json();
    const { student_id, responses, total_time_minutes } = body;

    const testSession = db.getTestSession(testId);
    if (!testSession) {
      return NextResponse.json(
        { success: false, error: 'Test session not found' },
        { status: 404 }
      );
    }

    if (!student_id || testSession.student_id !== student_id) {
      return NextResponse.json(
        { success: false, error: 'Invalid student_id for this test session' },
        { status: 403 }
      );
    }

    if (!responses || !Array.isArray(responses)) {
      return NextResponse.json(
        { success: false, error: 'responses array is required' },
        { status: 400 }
      );
    }

    const submission: TestSubmission = {
      test_id: testId,
      student_id,
      responses: responses as StudentResponse[],
      total_time_minutes: total_time_minutes || 0,
    };

    db.updateTestSession(testId, {
      status: 'submitted',
      submitted_at: new Date().toISOString(),
    });

    const engine = getLayaEngine();
    const analysis = await engine.analyzeTest(testSession, submission);

    db.saveTestAnalysis(analysis);

    db.updateTestSession(testId, {
      status: 'analyzed',
    });

    const response: ApiResponse<TestAnalysis> = {
      success: true,
      data: analysis,
      message: 'Test submitted and analyzed successfully',
    };

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    console.error('Error submitting test:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to submit and analyze test' },
      { status: 500 }
    );
  }
}
