// Laya Analysis Engine - Core analysis pipeline for UPSC Prelims test responses

import {
  TestSession,
  TestSubmission,
  StudentResponse,
  Question,
  MistakeCard,
  MistakeType,
  PatternAnalysis,
  Recommendation,
  TestAnalysis,
  SubjectPerformance,
  Severity,
} from './types';
import { getLongCatClient } from './longcat';

/**
 * Laya Analysis Engine
 * Ingests test submissions, classifies mistakes, identifies patterns,
 * generates mistake cards with severity, and creates personalized recommendations.
 */
export class LayaAnalysisEngine {
  /**
   * Main analysis pipeline: processes a test submission and returns full analysis.
   */
  async analyzeTest(
    testSession: TestSession,
    submission: TestSubmission
  ): Promise<TestAnalysis> {
    const { questions } = testSession;
    const { responses } = submission;

    // Step 1: Build response map
    const responseMap = new Map<string, StudentResponse>();
    responses.forEach((r) => responseMap.set(r.question_id, r));

    // Step 2: Classify each response
    const classifiedResponses = questions.map((q) => {
      const response = responseMap.get(q.id);
      return {
        question: q,
        response: response || null,
        isCorrect: response ? response.selected_option_id === q.correct_option_id : false,
        isUnanswered: !response || response.selected_option_id === null,
      };
    });

    // Step 3: Compute basic stats
    const totalCorrect = classifiedResponses.filter((r) => r.isCorrect).length;
    const totalIncorrect = classifiedResponses.filter((r) => !r.isCorrect && !r.isUnanswered).length;
    const totalUnanswered = classifiedResponses.filter((r) => r.isUnanswered).length;
    const accuracyPercentage = (totalCorrect / questions.length) * 100;
    const overallScore = totalCorrect * 2 - totalIncorrect * 0.66; // UPSC scoring

    // Step 4: Generate mistake cards for incorrect/unanswered questions
    const incorrectResponses = classifiedResponses.filter((r) => !r.isCorrect);
    const mistakeCards = await this.generateMistakeCards(incorrectResponses, submission);

    // Step 5: Identify patterns across all mistakes
    const patterns = await this.identifyPatterns(mistakeCards, testSession);

    // Step 6: Compute subject-wise performance
    const subjectPerformance = this.computeSubjectPerformance(classifiedResponses);

    // Step 7: Generate recommendations
    const recommendations = await this.generateRecommendations(
      mistakeCards,
      patterns,
      subjectPerformance,
      testSession
    );

    // Step 8: Assemble full analysis
    const analysis: TestAnalysis = {
      test_id: testSession.id,
      student_id: submission.student_id,
      overall_score: Math.round(overallScore * 100) / 100,
      total_correct: totalCorrect,
      total_incorrect: totalIncorrect,
      total_unanswered: totalUnanswered,
      accuracy_percentage: Math.round(accuracyPercentage * 100) / 100,
      mistake_cards: mistakeCards,
      patterns,
      subject_performance: subjectPerformance,
      recommendations,
      analysis_timestamp: new Date().toISOString(),
    };

    return analysis;
  }

  /**
   * Generate mistake cards for each incorrect or unanswered question.
   */
  private async generateMistakeCards(
    incorrectResponses: Array<{ question: Question; response: StudentResponse | null; isCorrect: boolean; isUnanswered: boolean }>,
    submission: TestSubmission
  ): Promise<MistakeCard[]> {
    const cards: MistakeCard[] = [];

    // Batch questions for LLM analysis - group by 5 to stay within token limits
    const batchSize = 5;
    for (let i = 0; i < incorrectResponses.length; i += batchSize) {
      const batch = incorrectResponses.slice(i, i + batchSize);
      const batchCards = await this.analyzeBatchWithLLM(batch, submission);
      cards.push(...batchCards);
    }

    return cards;
  }

  /**
   * Use LongCat LLM to classify a batch of mistakes.
   */
  private async analyzeBatchWithLLM(
    batch: Array<{ question: Question; response: StudentResponse | null; isCorrect: boolean; isUnanswered: boolean }>,
    _submission: TestSubmission
  ): Promise<MistakeCard[]> {
    const client = getLongCatClient();

    const questionsData = batch.map((item, idx) => ({
      index: idx,
      question_id: item.question.id,
      subject: item.question.subject,
      topic: item.question.topic,
      subtopic: item.question.subtopic || 'N/A',
      difficulty: item.question.difficulty,
      question_text: item.question.question_text,
      options: item.question.options.map((o) => `${o.id}: ${o.text}`).join('\n'),
      correct_answer: item.question.options.find((o) => o.id === item.question.correct_option_id)?.text || 'N/A',
      student_answer: item.isUnanswered
        ? 'UNANSWERED'
        : item.response
          ? item.question.options.find((o) => o.id === item.response!.selected_option_id)?.text || 'N/A'
          : 'UNANSWERED',
      time_spent_seconds: item.response?.time_spent_seconds || 0,
      confidence: item.response?.confidence || 'N/A',
      explanation: item.question.explanation || 'N/A',
    }));

    const systemPrompt = `You are a UPSC Prelims analysis expert. Analyze the following incorrect/unanswered questions and classify each mistake.
For each question, determine:
1. mistake_type: one of [conceptual_gap, confusion_similar, partial_knowledge, factual_error, guesswork, time_pressure, misinterpretation]
2. severity: one of [low, medium, high, critical] based on how fundamental the concept is and exam importance
3. root_cause: brief explanation of why the student likely got it wrong
4. remediation: specific actionable step to fix this gap
5. confidence_score: 0.0-1.0 how confident you are in this classification

Return a JSON array with one object per question.`;

    const userPrompt = `Analyze these UPSC questions and their mistakes:

${JSON.stringify(questionsData, null, 2)}

Return JSON array format:
[
  {
    "question_id": "...",
    "mistake_type": "...",
    "severity": "...",
    "root_cause": "...",
    "remediation": "...",
    "confidence_score": 0.95
  }
]`;

    try {
      const result = await client
        .completeJson<Array<{
          question_id: string;
          mistake_type: MistakeType;
          severity: Severity;
          root_cause: string;
          remediation: string;
          confidence_score: number;
        }>>(systemPrompt, userPrompt);

      return result.map((r) => {
        const item = batch.find((b) => b.question.id === r.question_id);
        if (!item) return null;

        const studentAnswer = item.isUnanswered
          ? 'Unanswered'
          : item.response
            ? item.question.options.find((o) => o.id === item.response!.selected_option_id)?.text || 'Unknown'
            : 'Unknown';

        const correctAnswer = item.question.options.find((o) => o.id === item.question.correct_option_id)?.text || 'Unknown';

        return {
          question_id: item.question.id,
          subject: item.question.subject,
          topic: item.question.topic,
          subtopic: item.question.subtopic,
          mistake_type: r.mistake_type,
          severity: r.severity,
          student_answer: studentAnswer,
          correct_answer: correctAnswer,
          explanation: item.question.explanation || 'No explanation available',
          root_cause: r.root_cause,
          remediation: r.remediation,
          confidence_score: r.confidence_score,
        } as MistakeCard;
      }).filter((c): c is MistakeCard => c !== null);
    } catch (error) {
      // Fallback: use rule-based classification if LLM fails
      console.error('LLM batch analysis failed, using rule-based fallback:', error);
      return batch.map((item) => this.ruleBasedClassification(item));
    }
  }

  /**
   * Rule-based fallback classification when LLM is unavailable.
   */
  private ruleBasedClassification(item: {
    question: Question;
    response: StudentResponse | null;
    isCorrect: boolean;
    isUnanswered: boolean;
  }): MistakeCard {
    let mistakeType: MistakeType = 'conceptual_gap';
    let severity: Severity = 'medium';
    let rootCause = 'Unable to determine specific cause';
    let remediation = 'Review the topic thoroughly';

    if (item.isUnanswered) {
      if (item.response && item.response.time_spent_seconds < 30) {
        mistakeType = 'guesswork';
        severity = 'low';
        rootCause = 'Low confidence led to skipping';
        remediation = 'Practice building confidence through timed exercises';
      } else if (item.response && item.response.time_spent_seconds > 120) {
        mistakeType = 'time_pressure';
        severity = 'medium';
        rootCause = 'Spent too much time, possibly ran out of time';
        remediation = 'Improve time management; practice timed mock tests';
      } else {
        mistakeType = 'partial_knowledge';
        severity = 'medium';
        rootCause = 'Insufficient knowledge to attempt the question';
        remediation = `Study ${item.question.topic} in ${item.question.subject} more deeply`;
      }
    } else if (item.response) {
      // Check for similar option patterns
      const correctOption = item.question.options.find((o) => o.id === item.question.correct_option_id);
      const selectedOption = item.question.options.find((o) => o.id === item.response!.selected_option_id);

      if (item.response.confidence === 'low') {
        mistakeType = 'guesswork';
        severity = 'low';
        rootCause = 'Answer was a guess with low confidence';
        remediation = `Strengthen fundamentals in ${item.question.topic}`;
      } else if (
        correctOption &&
        selectedOption &&
        this.isSimilarText(correctOption.text, selectedOption.text)
      ) {
        mistakeType = 'confusion_similar';
        severity = 'high';
        rootCause = 'Confused between two similar-sounding options';
        remediation = `Create comparison tables for similar concepts in ${item.question.topic}`;
      } else if (item.question.difficulty === 'hard') {
        mistakeType = 'partial_knowledge';
        severity = 'medium';
        rootCause = 'Partial understanding of the concept';
        remediation = `Deep dive into ${item.question.subtopic || item.question.topic} with advanced material`;
      } else {
        mistakeType = 'factual_error';
        severity = item.question.difficulty === 'easy' ? 'high' : 'medium';
        rootCause = 'Factual recall error';
        remediation = `Create flashcards for key facts in ${item.question.topic}`;
      }
    }

    return {
      question_id: item.question.id,
      subject: item.question.subject,
      topic: item.question.topic,
      subtopic: item.question.subtopic,
      mistake_type: mistakeType,
      severity,
      student_answer: item.response
        ? item.question.options.find((o) => o.id === item.response!.selected_option_id)?.text || 'Unknown'
        : 'Unanswered',
      correct_answer: item.question.options.find((o) => o.id === item.question.correct_option_id)?.text || 'Unknown',
      explanation: item.question.explanation || 'No explanation available',
      root_cause: rootCause,
      remediation,
      confidence_score: 0.5, // Low confidence for rule-based
    };
  }

  /**
   * Simple heuristic to detect if two option texts are suspiciously similar.
   */
  private isSimilarText(a: string, b: string): boolean {
    if (!a || !b) return false;
    const wordsA = new Set(a.toLowerCase().split(/\s+/));
    const wordsB = new Set(b.toLowerCase().split(/\s+/));
    const intersection = [...wordsA].filter((w) => wordsB.has(w));
    const similarity = intersection.length / Math.max(wordsA.size, wordsB.size);
    return similarity > 0.5;
  }

  /**
   * Identify recurring patterns across mistake cards using LLM.
   */
  private async identifyPatterns(
    mistakeCards: MistakeCard[],
    testSession: TestSession
  ): Promise<PatternAnalysis[]> {
    if (mistakeCards.length === 0) return [];

    const client = getLongCatClient();

    const mistakeData = mistakeCards.map((mc) => ({
      question_id: mc.question_id,
      subject: mc.subject,
      topic: mc.topic,
      mistake_type: mc.mistake_type,
      severity: mc.severity,
      root_cause: mc.root_cause,
    }));

    const systemPrompt = `You are a UPSC analysis expert. Given a set of mistake cards, identify recurring patterns that indicate systematic weaknesses.
Return a JSON array of patterns. Each pattern should group related mistakes and provide a high-level recommendation.`;

    const userPrompt = `Mistakes from UPSC test "${testSession.test_name}":
${JSON.stringify(mistakeData, null, 2)}

Identify 2-4 key patterns. Return JSON:
[
  {
    "pattern_id": "unique_id",
    "pattern_name": "...",
    "description": "...",
    "affected_topics": ["topic1", "topic2"],
    "occurrence_count": 3,
    "severity": "high",
    "recommendation": "..."
  }
]`;

    try {
      const patterns = await client.completeJson<PatternAnalysis[]>(systemPrompt, userPrompt);
      return patterns;
    } catch (error) {
      console.error('LLM pattern analysis failed:', error);
      return this.ruleBasedPatterns(mistakeCards);
    }
  }

  /**
   * Rule-based fallback for pattern identification.
   */
  private ruleBasedPatterns(mistakeCards: MistakeCard[]): PatternAnalysis[] {
    const typeCount = new Map<MistakeType, MistakeCard[]>();
    const topicCount = new Map<string, MistakeCard[]>();

    mistakeCards.forEach((mc) => {
      const typeCards = typeCount.get(mc.mistake_type) || [];
      typeCards.push(mc);
      typeCount.set(mc.mistake_type, typeCards);

      const topicCards = topicCount.get(mc.topic) || [];
      topicCards.push(mc);
      topicCount.set(mc.topic, topicCards);
    });

    const patterns: PatternAnalysis[] = [];

    // Group by mistake type
    typeCount.forEach((cards, type) => {
      if (cards.length >= 2) {
        const severity = cards.some((c) => c.severity === 'critical' || c.severity === 'high')
          ? 'high'
          : 'medium';
        patterns.push({
          pattern_id: `type_${type}`,
          pattern_name: `Recurring ${type.replace('_', ' ')} errors`,
          description: `Found ${cards.length} instances of ${type.replace('_', ' ')} mistakes`,
          affected_topics: [...new Set(cards.map((c) => c.topic))],
          occurrence_count: cards.length,
          severity,
          recommendation: `Focus on addressing ${type.replace('_ ', ' ')} weaknesses through targeted practice and concept review`,
        });
      }
    });

    // Group by topic
    topicCount.forEach((cards, topic) => {
      if (cards.length >= 2) {
        patterns.push({
          pattern_id: `topic_${topic.replace(/\s+/g, '_')}`,
          pattern_name: `Weakness in ${topic}`,
          description: `${cards.length} mistakes in topic "${topic}"`,
          affected_topics: [topic],
          occurrence_count: cards.length,
          severity: cards.length >= 3 ? 'high' : 'medium',
          recommendation: `Dedicate focused study time to strengthen ${topic} concepts`,
        });
      }
    });

    return patterns.slice(0, 5);
  }

  /**
   * Compute subject-wise performance metrics.
   */
  private computeSubjectPerformance(
    classifiedResponses: Array<{
      question: Question;
      response: StudentResponse | null;
      isCorrect: boolean;
      isUnanswered: boolean;
    }>
  ): SubjectPerformance[] {
    const subjectMap = new Map<
      string,
      { correct: Question[]; incorrect: Question[]; unanswered: Question[]; all: Question[] }
    >();

    classifiedResponses.forEach((cr) => {
      const subject = cr.question.subject;
      const data = subjectMap.get(subject) || { correct: [], incorrect: [], unanswered: [], all: [] };
      data.all.push(cr.question);
      if (cr.isCorrect) data.correct.push(cr.question);
      else if (cr.isUnanswered) data.unanswered.push(cr.question);
      else data.incorrect.push(cr.question);
      subjectMap.set(subject, data);
    });

    return Array.from(subjectMap.entries()).map(([subject, data]) => {
      const topicAccuracy = new Map<string, { correct: number; total: number }>();
      data.all.forEach((q) => {
        const acc = topicAccuracy.get(q.topic) || { correct: 0, total: 0 };
        acc.total++;
        if (data.correct.includes(q)) acc.correct++;
        topicAccuracy.set(q.topic, acc);
      });

      const topicEntries = Array.from(topicAccuracy.entries());
      const sorted = topicEntries.sort(
        (a, b) => a[1].correct / a[1].total - b[1].correct / b[1].total
      );

      const topWeak = sorted.slice(0, 3).filter(([, v]) => v.total > 0).map(([t]) => t);
      const topStrong = sorted
        .filter(([, v]) => v.total > 0)
        .slice(-3)
        .reverse()
        .map(([t]) => t);

      return {
        subject,
        total_questions: data.all.length,
        correct_answers: data.correct.length,
        incorrect_answers: data.incorrect.length,
        unanswered: data.unanswered.length,
        score: data.correct.length * 2 - data.incorrect.length * 0.66,
        accuracy_percentage: data.all.length > 0 ? (data.correct.length / data.all.length) * 100 : 0,
        top_weak_topics: topWeak,
        top_strong_topics: topStrong,
      };
    });
  }

  /**
   * Generate personalized recommendations based on analysis.
   */
  private async generateRecommendations(
    mistakeCards: MistakeCard[],
    patterns: PatternAnalysis[],
    subjectPerformance: SubjectPerformance[],
    testSession: TestSession
  ): Promise<Recommendation[]> {
    const client = getLongCatClient();

    // Build context for LLM
    const weakSubjects = subjectPerformance
      .filter((sp) => sp.accuracy_percentage < 50)
      .map((sp) => `${sp.subject} (${sp.accuracy_percentage.toFixed(1)}%)`);

    const context = {
      test_name: testSession.test_name,
      total_mistakes: mistakeCards.length,
      mistake_types: [...new Set(mistakeCards.map((mc) => mc.mistake_type))],
      weak_subjects: weakSubjects,
      patterns: patterns.map((p) => p.pattern_name),
      top_weak_topics: [
        ...new Set(
          subjectPerformance.flatMap((sp) => sp.top_weak_topics)
        ),
      ].slice(0, 5),
    };

    const systemPrompt = `You are a UPSC preparation strategy expert. Based on the test analysis, generate personalized recommendations.
Return a JSON array of 3-5 actionable recommendations. Each should have a specific type, priority, and concrete steps.`;

    const userPrompt = `Analysis context:
${JSON.stringify(context, null, 2)}

Generate recommendations. Return JSON:
[
  {
    "id": "rec_1",
    "type": "topic_review" | "practice" | "strategy" | "time_management" | "resource",
    "title": "...",
    "description": "...",
    "priority": "high" | "medium" | "low",
    "related_topics": ["topic1"],
    "actionable_steps": ["step 1", "step 2"]
  }
]`;

    try {
      const recs = await client.completeJson<Recommendation[]>(systemPrompt, userPrompt);
      return recs;
    } catch (error) {
      console.error('LLM recommendation generation failed:', error);
      return this.ruleBasedRecommendations(mistakeCards, patterns, subjectPerformance);
    }
  }

  /**
   * Rule-based fallback for recommendations.
   */
  private ruleBasedRecommendations(
    mistakeCards: MistakeCard[],
    patterns: PatternAnalysis[],
    subjectPerformance: SubjectPerformance[]
  ): Recommendation[] {
    const recs: Recommendation[] = [];

    // Topic review recommendations for weak subjects
    subjectPerformance
      .filter((sp) => sp.accuracy_percentage < 50)
      .forEach((sp, idx) => {
        recs.push({
          id: `rec_weak_subject_${idx}`,
          type: 'topic_review',
          title: `Strengthen ${sp.subject}`,
          description: `Your accuracy in ${sp.subject} is ${sp.accuracy_percentage.toFixed(1)}%. Focus on weak topics.`,
          priority: 'high',
          related_topics: sp.top_weak_topics,
          actionable_steps: [
            `Review NCERT and standard textbooks for ${sp.subject}`,
            `Practice 20+ MCQs daily from weak topics`,
            `Create summary notes for quick revision`,
          ],
        });
      });

    // Practice recommendations based on mistake types
    const mistakeTypes = new Set(mistakeCards.map((mc) => mc.mistake_type));
    if (mistakeTypes.has('guesswork')) {
      recs.push({
        id: 'rec_guesswork',
        type: 'strategy',
        title: 'Reduce guesswork with elimination techniques',
        description: 'Multiple incorrect answers stem from guessing. Practice elimination strategies.',
        priority: 'high',
        related_topics: [],
        actionable_steps: [
          'Practice eliminating obviously wrong options first',
          'Learn to identify "except" and "not correct" question traps',
          'Take timed quizzes to build confidence under pressure',
        ],
      });
    }

    if (mistakeTypes.has('confusion_similar')) {
      recs.push({
        id: 'rec_confusion',
        type: 'practice',
        title: 'Build comparison charts for confusing topics',
        description: 'You frequently confuse similar concepts. Create visual aids to distinguish them.',
        priority: 'medium',
        related_topics: [...new Set(mistakeCards.filter((mc) => mc.mistake_type === 'confusion_similar').map((mc) => mc.topic))],
        actionable_steps: [
          'Create side-by-side comparison tables for similar concepts',
          'Use mnemonics to differentiate between similar options',
          'Practice questions that specifically test differentiation',
        ],
      });
    }

    // Time management recommendation
    if (mistakeTypes.has('time_pressure')) {
      recs.push({
        id: 'rec_time',
        type: 'time_management',
        title: 'Improve time management during tests',
        description: 'Time pressure is causing errors. Develop a pacing strategy.',
        priority: 'medium',
        related_topics: [],
        actionable_steps: [
          'Set a per-question time limit (e.g., 45 seconds)',
          'Skip and mark questions taking too long',
          'Practice full-length timed mock tests weekly',
        ],
      });
    }

    // Add pattern-based recommendations
    patterns.forEach((pattern, idx) => {
      if (pattern.severity === 'high' || pattern.severity === 'critical') {
        recs.push({
          id: `rec_pattern_${idx}`,
          type: 'strategy',
          title: `Address pattern: ${pattern.pattern_name}`,
          description: pattern.description,
          priority: pattern.severity === 'critical' ? 'high' : 'medium',
          related_topics: pattern.affected_topics,
          actionable_steps: [pattern.recommendation],
        });
      }
    });

    return recs.slice(0, 5);
  }

  /**
   * Standalone analysis - analyze a single question-answer pair.
   */
  async analyzeSingleQuestion(
    question: Question,
    selectedOptionId: string | null,
    timeSpentSeconds: number
  ): Promise<Partial<MistakeCard>> {
    const isCorrect = selectedOptionId === question.correct_option_id;
    if (isCorrect) {
      return {
        question_id: question.id,
        mistake_type: 'factual_error', // Not actually an error, but used for type consistency
        severity: 'low',
        root_cause: 'Correct answer',
        remediation: 'Keep up the good work',
        confidence_score: 1.0,
      };
    }

    const item = {
      question,
      response: selectedOptionId
        ? {
            question_id: question.id,
            selected_option_id: selectedOptionId,
            time_spent_seconds: timeSpentSeconds,
            marked_for_review: false,
            confidence: 'medium' as const,
          }
        : null,
      isCorrect: false,
      isUnanswered: !selectedOptionId,
    };

    const cards = await this.analyzeBatchWithLLM([item], {
      test_id: '',
      student_id: '',
      responses: [],
      total_time_minutes: 0,
    });

    return cards[0] || this.ruleBasedClassification(item);
  }
}