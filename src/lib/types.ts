// Types for UPSC Test Analysis App

export type MistakeType =
  | 'conceptual_gap'
  | 'confusion_similar'
  | 'partial_knowledge'
  | 'factual_error'
  | 'guesswork'
  | 'time_pressure'
  | 'misinterpretation';

export type Severity = 'low' | 'medium' | 'high' | 'critical';

export type TestStatus = 'pending' | 'in_progress' | 'submitted' | 'analyzed';

export interface Option {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  subject: string;
  topic: string;
  subtopic?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  question_text: string;
  options: Option[];
  correct_option_id: string;
  explanation?: string;
  marks?: number;
  negative_marks?: number;
}

export interface TestSession {
  id: string;
  student_id: string;
  test_name: string;
  subject_filter?: string[];
  total_questions: number;
  questions: Question[];
  status: TestStatus;
  created_at: string;
  submitted_at?: string;
  time_limit_minutes?: number;
}

export interface StudentResponse {
  question_id: string;
  selected_option_id: string | null;
  time_spent_seconds: number;
  marked_for_review: boolean;
  confidence: 'high' | 'medium' | 'low';
}

export interface TestSubmission {
  test_id: string;
  student_id: string;
  responses: StudentResponse[];
  total_time_minutes: number;
}

export interface MistakeCard {
  question_id: string;
  subject: string;
  topic: string;
  subtopic?: string;
  mistake_type: MistakeType;
  severity: Severity;
  student_answer: string;
  correct_answer: string;
  explanation: string;
  root_cause: string;
  remediation: string;
  confidence_score: number;
}

export interface PatternAnalysis {
  pattern_id: string;
  pattern_name: string;
  description: string;
  affected_topics: string[];
  occurrence_count: number;
  severity: Severity;
  recommendation: string;
}

export interface SubjectPerformance {
  subject: string;
  total_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  unanswered: number;
  score: number;
  accuracy_percentage: number;
  top_weak_topics: string[];
  top_strong_topics: string[];
}

export interface TestAnalysis {
  test_id: string;
  student_id: string;
  overall_score: number;
  total_correct: number;
  total_incorrect: number;
  total_unanswered: number;
  accuracy_percentage: number;
  percentile_estimate?: number;
  mistake_cards: MistakeCard[];
  patterns: PatternAnalysis[];
  subject_performance: SubjectPerformance[];
  recommendations: Recommendation[];
  analysis_timestamp: string;
}

export interface Recommendation {
  id: string;
  type: 'topic_review' | 'practice' | 'strategy' | 'time_management' | 'resource';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  related_topics: string[];
  actionable_steps: string[];
}

export interface StudentDashboard {
  student_id: string;
  student_name?: string;
  total_tests_taken: number;
  average_accuracy: number;
  accuracy_trend: number[];
  subject_wise_performance: SubjectPerformance[];
  recent_mistake_cards: MistakeCard[];
  top_patterns: PatternAnalysis[];
  pending_recommendations: Recommendation[];
  improvement_areas: string[];
  strengths: string[];
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface LongCatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface LongCatChoice {
  index: number;
  message: LongCatMessage;
  finish_reason: string;
}

export interface LongCatResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: LongCatChoice[];
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}