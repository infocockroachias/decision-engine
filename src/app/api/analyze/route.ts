import { NextRequest, NextResponse } from 'next/server';
import { getLayaEngine } from '@/lib';
import { ApiResponse, Question, MistakeCard } from '@/lib/types';

// POST /api/analyze - Standalone analysis endpoint
// Analyze a single question-answer pair or a batch of questions
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { question, selected_option_id, time_spent_seconds, questions_batch } = body;

    const engine = getLayaEngine();

    // Batch analysis
    if (questions_batch && Array.isArray(questions_batch)) {
      const results: Array<{ question_id: string; analysis: Partial<MistakeCard> }> = [];

      for (const item of questions_batch) {
        if (!item.question) continue;

        const result = await engine.analyzeSingleQuestion(
          item.question as Question,
          item.selected_option_id || null,
          item.time_spent_seconds || 0
        );

        results.push({
          question_id: item.question.id,
          analysis: result,
        });
      }

      return NextResponse.json(
        { success: true, data: results, message: 'Batch analysis complete' },
        { status: 200 }
      );
    }

    // Single question analysis
    if (!question) {
      return NextResponse.json(
        { success: false, error: 'question object is required (or questions_batch for batch analysis)' },
        { status: 400 }
      );
    }

    const result = await engine.analyzeSingleQuestion(
      question as Question,
      selected_option_id || null,
      time_spent_seconds || 0
    );

    const response: ApiResponse<Partial<MistakeCard>> = {
      success: true,
      data: result,
      message: 'Analysis complete',
    };

    return NextResponse.json(response, { status: 200 });
  } catch (error) {
    console.error('Error in standalone analysis:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to analyze question' },
      { status: 500 }
    );
  }
}