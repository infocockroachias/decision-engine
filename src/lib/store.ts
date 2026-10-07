// In-memory storage for test sessions and analyses
// In production, replace with a proper database (PostgreSQL, MongoDB, etc.)

import { TestSession, TestAnalysis, StudentDashboard } from './types';

const testSessions = new Map<string, TestSession>();
const testAnalyses = new Map<string, TestAnalysis>();
const studentHistory = new Map<string, string[]>(); // student_id -> test_ids

export const db = {
  // Test Sessions
  createTestSession(session: TestSession): TestSession {
    testSessions.set(session.id, session);
    const history = studentHistory.get(session.student_id) || [];
    history.push(session.id);
    studentHistory.set(session.student_id, history);
    return session;
  },

  getTestSession(id: string): TestSession | undefined {
    return testSessions.get(id);
  },

  updateTestSession(id: string, updates: Partial<TestSession>): TestSession | undefined {
    const session = testSessions.get(id);
    if (!session) return undefined;
    const updated = { ...session, ...updates };
    testSessions.set(id, updated);
    return updated;
  },

  // Test Analyses
  saveTestAnalysis(analysis: TestAnalysis): TestAnalysis {
    testAnalyses.set(analysis.test_id, analysis);
    return analysis;
  },

  getTestAnalysis(testId: string): TestAnalysis | undefined {
    return testAnalyses.get(testId);
  },

  // Student History
  getStudentTestIds(studentId: string): string[] {
    return studentHistory.get(studentId) || [];
  },

  getStudentAnalyses(studentId: string): TestAnalysis[] {
    const testIds = studentHistory.get(studentId) || [];
    return testIds
      .map((id) => testAnalyses.get(id))
      .filter((a): a is TestAnalysis => a !== undefined);
  },

  getStudentDashboard(studentId: string): StudentDashboard | undefined {
    const analyses = this.getStudentAnalyses(studentId);
    if (analyses.length === 0) return undefined;

    const totalTests = analyses.length;
    const avgAccuracy =
      analyses.reduce((sum, a) => sum + a.accuracy_percentage, 0) / totalTests;
    const trend = analyses.map((a) => a.accuracy_percentage);

    // Aggregate subject performance
    const subjectMap = new Map<string, { correct: number; total: number; incorrect: number; unanswered: number }>();
    analyses.forEach((a) => {
      a.subject_performance.forEach((sp) => {
        const existing = subjectMap.get(sp.subject) || { correct: 0, total: 0, incorrect: 0, unanswered: 0 };
        existing.correct += sp.correct_answers;
        existing.total += sp.total_questions;
        existing.incorrect += sp.incorrect_answers;
        existing.unanswered += sp.unanswered;
        subjectMap.set(sp.subject, existing);
      });
    });

    const subjectPerf = Array.from(subjectMap.entries()).map(([subject, data]) => ({
      subject,
      total_questions: data.total,
      correct_answers: data.correct,
      incorrect_answers: data.incorrect,
      unanswered: data.unanswered,
      score: data.correct,
      accuracy_percentage: data.total > 0 ? (data.correct / data.total) * 100 : 0,
      top_weak_topics: [],
      top_strong_topics: [],
    }));

    // Collect recent mistake cards
    const recentMistakes = analyses
      .sort((a, b) => new Date(b.analysis_timestamp).getTime() - new Date(a.analysis_timestamp).getTime())
      .slice(0, 3)
      .flatMap((a) => a.mistake_cards)
      .slice(0, 10);

    // Collect patterns
    const allPatterns = analyses.flatMap((a) => a.patterns);
    const uniquePatterns = Array.from(
      new Map(allPatterns.map((p) => [p.pattern_id, p])).values()
    ).slice(0, 5);

    // Collect recommendations
    const allRecommendations = analyses.flatMap((a) => a.recommendations);
    const uniqueRecs = Array.from(
      new Map(allRecommendations.map((r) => [r.id, r])).values()
    ).slice(0, 5);

    // Determine improvement areas and strengths
    const weakSubjects = subjectPerf
      .filter((s) => s.accuracy_percentage < 50)
      .map((s) => s.subject);
    const strongSubjects = subjectPerf
      .filter((s) => s.accuracy_percentage >= 70)
      .map((s) => s.subject);

    return {
      student_id: studentId,
      total_tests_taken: totalTests,
      average_accuracy: avgAccuracy,
      accuracy_trend: trend,
      subject_wise_performance: subjectPerf,
      recent_mistake_cards: recentMistakes,
      top_patterns: uniquePatterns,
      pending_recommendations: uniqueRecs,
      improvement_areas: weakSubjects,
      strengths: strongSubjects,
    };
  },
};