import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/store';
import { ApiResponse, TestAnalysis } from '@/lib/types';

// GET /api/tests/[id]/results - Get analysis results for a test
export async function GET(
  req: NextRequest,
  props: { params: Promise<{ id: string }> }
) {
  try {
    const { id: testId } = await props.params;
    const { searchParams } = new URL(req.url);
    const studentId = searchParams.get('student_id');

    const testSession = db.getTestSession(testId);
    if (!testSession) {
      return NextResponse.json(
        { success: false, error: 'Test session not found' },
        { status: 404 }
      );
    }

    const analysis = db.getTestAnalysis(testId);
    if (!analysis) {
      return NextResponse.json(
        { success: false, error: 'Analysis not available. Test may not have been submitted yet.' },
        { status: 404 }
      );
    }

    if (studentId && analysis.student_id !== studentId) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized access to this analysis' },
        { status: 403 }
      );
    }

    const response: ApiResponse<TestAnalysis> = {
      success: true,
      data: analysis,
    };

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    console.error('Error fetching test results:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch test results' },
      { status: 500 }
    );
  }
}
