import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/store';
import { ApiResponse, StudentDashboard } from '@/lib/types';

// GET /api/students/[id]/dashboard - Get student progress dashboard
export async function GET(
  req: NextRequest,
  props: { params: Promise<{ id: string }> }
) {
  try {
    const { id: studentId } = await props.params;

    const dashboard = db.getStudentDashboard(studentId);

    if (!dashboard) {
      const emptyDashboard: StudentDashboard = {
        student_id: studentId,
        total_tests_taken: 0,
        average_accuracy: 0,
        accuracy_trend: [],
        subject_wise_performance: [],
        recent_mistake_cards: [],
        top_patterns: [],
        pending_recommendations: [],
        improvement_areas: [],
        strengths: [],
      };

      return NextResponse.json(
        { success: true, data: emptyDashboard, message: 'No test history found for this student' },
        { status: 200 }
      );
    }

    const response: ApiResponse<StudentDashboard> = {
      success: true,
      data: dashboard,
    };

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    console.error('Error fetching student dashboard:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch student dashboard' },
      { status: 500 }
    );
  }
}
