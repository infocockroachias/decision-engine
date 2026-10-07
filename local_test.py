#!/usr/bin/env python3
"""
Local Testing Script - UPSC Prelims Laya Engine
================================================
Uses SQLite database and in-memory processing.
No API routes needed - direct engine calls.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
WORKSPACE = Path(__file__).parent
sys.path.insert(0, str(WORKSPACE))

# Database path
DB_PATH = WORKSPACE / "data" / "test.db"
OUTPUT_PATH = WORKSPACE / "output"
OUTPUT_PATH.mkdir(exist_ok=True)

# ====== DATABASE LAYER (SQLite in-memory or file) ======

import sqlite3
from contextlib import contextmanager


class LocalDatabase:
    """SQLite database for local testing."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or ":memory:"
        self.conn = sqlite3.connect(str(self.db_path) if db_path != ":memory:" else ":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    def _create_tables(self):
        """Create all tables."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                target_exam TEXT DEFAULT 'UPSC CSE 2027',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                year INTEGER,
                subject TEXT,
                topic TEXT,
                subtopic TEXT,
                question_text TEXT,
                options_json TEXT,
                correct_answer TEXT,
                explanation TEXT,
                difficulty TEXT DEFAULT 'medium',
                question_type TEXT DEFAULT 'factual',
                syllabus_pointer TEXT,
                pyq_pattern TEXT
            );

            CREATE TABLE IF NOT EXISTS test_sessions (
                id TEXT PRIMARY KEY,
                student_id TEXT,
                test_name TEXT,
                status TEXT DEFAULT 'pending',
                total_questions INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                question_id TEXT,
                selected_answer TEXT,
                is_correct BOOLEAN,
                time_spent_seconds INTEGER DEFAULT 0,
                confidence TEXT DEFAULT 'medium',
                marked_for_review BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES test_sessions(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );

            CREATE TABLE IF NOT EXISTS mistake_cards (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                response_id TEXT,
                subject TEXT,
                topic TEXT,
                subtopic TEXT,
                mistake_type TEXT,
                severity TEXT DEFAULT 'medium',
                student_answer TEXT,
                correct_answer TEXT,
                explanation TEXT,
                root_cause TEXT,
                remediation TEXT,
                confidence_score REAL DEFAULT 0.5,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES test_sessions(id),
                FOREIGN KEY (response_id) REFERENCES responses(id)
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                category TEXT,
                priority TEXT DEFAULT 'medium',
                message TEXT,
                action_items_json TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES test_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY,
                session_id TEXT UNIQUE,
                overall_score REAL,
                total_correct INTEGER,
                total_incorrect INTEGER,
                total_unanswered INTEGER,
                accuracy_percentage REAL,
                patterns_json TEXT,
                subject_performance_json TEXT,
                analysis_timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES test_sessions(id)
            );
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()


# ====== QUESTION BANK (Real UPSC PYQs) ======

QUESTION_BANK = [
    # 2024 PYQs
    {"id": "PYQ-2024-001", "year": 2024, "subject": "Polity", "topic": "Parliament", "subtopic": "Money Bill", "question": "With reference to the Parliament of India, consider the following statements: 1. A bill pending in the Lok Sabha lapses on its dissolution. 2. A bill passed by the Lok Sabha and pending in the Rajya Sabha lapses on the dissolution of the Lok Sabha. Which is/are correct?", "options": {"a": "1 only", "b": "2 only", "c": "Both 1 and 2", "d": "Neither 1 nor 2"}, "correct": "d", "explanation": "Statement 1 is incorrect: A bill pending in Lok Sabha does NOT lapse if it has been passed by Lok Sabha and is pending in Rajya Sabha. Statement 2 is incorrect: Such a bill continues in Rajya Sabha.", "difficulty": "medium", "type": "StatementBased"},
    {"id": "PYQ-2024-002", "year": 2024, "subject": "Polity", "topic": "Fundamental Rights", "subtopic": "Right to Privacy", "question": "Under which Article has the Supreme Court placed the Right to Privacy?", "options": {"a": "Article 15", "b": "Article 16", "c": "Article 19", "d": "Article 21"}, "correct": "d", "explanation": "In K.S. Puttaswamy case (2017), SC recognized Right to Privacy under Article 21.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2024-003", "year": 2024, "subject": "Economy", "topic": "Financial Markets", "subtopic": "Corporate Bonds", "question": "In India, which of the following can trade in Corporate Bonds and Government Securities? 1. Insurance Companies 2. Pension Funds 3. Retail Investors", "options": {"a": "1 and 2 only", "b": "2 and 3 only", "c": "1 and 3 only", "d": "1, 2 and 3"}, "correct": "d", "explanation": "All three can trade in Corporate Bonds and Government Securities.", "difficulty": "medium", "type": "StatementBased"},
    {"id": "PYQ-2024-004", "year": 2024, "subject": "Geography", "topic": "Climatology", "subtopic": "Coriolis Force", "question": "With reference to Coriolis force: 1. It increases with wind velocity. 2. Maximum at poles, absent at equator. Correct?", "options": {"a": "1 only", "b": "2 only", "c": "Both 1 and 2", "d": "Neither"}, "correct": "c", "explanation": "Coriolis force is proportional to wind velocity and varies with latitude (max at poles, zero at equator).", "difficulty": "medium", "type": "StatementBased"},
    {"id": "PYQ-2024-005", "year": 2024, "subject": "Environment", "topic": "Pollution", "subtopic": "PFAS", "question": "Consider statements about PFAS: 1. Found in some water sources. 2. Known as 'forever chemicals'. Correct?", "options": {"a": "1 only", "b": "2 only", "c": "Both 1 and 2", "d": "Neither"}, "correct": "c", "explanation": "PFAS are synthetic chemicals called 'forever chemicals' found in water, soil, and human blood.", "difficulty": "easy", "type": "StatementBased"},

    # 2023 PYQs
    {"id": "PYQ-2023-001", "year": 2023, "subject": "Polity", "topic": "Prisons", "subtopic": "State Subject", "question": "Consider: Statement-I: Prisons are managed by State Governments with their own rules. Statement-II: Prison is a State subject under Seventh Schedule.", "options": {"a": "I correct, II incorrect", "b": "I incorrect, II correct", "c": "Both correct", "d": "Both incorrect"}, "correct": "c", "explanation": "Both are correct. Prisons is Entry 4, State List.", "difficulty": "medium", "type": "AssertionReason"},
    {"id": "PYQ-2023-002", "year": 2023, "subject": "Economy", "topic": "Financial Markets", "subtopic": "InvITs", "question": "Consider: Statement-I: Interest income from InvITs is tax-exempt. Statement-II: InvITs are regulated by SEBI.", "options": {"a": "I incorrect, II correct", "b": "I correct, II incorrect", "c": "Both correct", "d": "Both incorrect"}, "correct": "a", "explanation": "I is incorrect (taxable), II is correct (SEBI regulates InvITs).", "difficulty": "hard", "type": "AssertionReason"},
    {"id": "PYQ-2023-003", "year": 2023, "subject": "Geography", "topic": "Indian Geography", "subtopic": "Ports", "question": "Match: 1. Kamarajar Port - First corporatized major port. 2. Mundra Port - Largest private port. 3. Mundra - Largest cargo port.", "options": {"a": "Only one", "b": "Only two", "c": "All three", "d": "None"}, "correct": "b", "explanation": "1 and 2 are correct. Deendayal (Kandla) handles most cargo, not Mundra.", "difficulty": "medium", "type": "Matching"},
    {"id": "PYQ-2023-004", "year": 2023, "subject": "Science", "topic": "Biology", "subtopic": "Animal Behavior", "question": "Which makes a tool with a stick to scrape insects from a hole?", "options": {"a": "Chimpanzee", "b": "Orangutan", "c": "Eagle", "d": "Crow"}, "correct": "a", "explanation": "Chimpanzees use tools to extract insects - documented by Jane Goodall.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2023-005", "year": 2023, "subject": "Environment", "topic": "Biodiversity", "subtopic": "Deciduous Trees", "question": "How many are deciduous? 1. Jackfruit 2. Mahua 3. Teak", "options": {"a": "Only one", "b": "Only two", "c": "All three", "d": "None"}, "correct": "c", "explanation": "All three are deciduous trees that shed leaves seasonally.", "difficulty": "hard", "type": "Factual"},

    # 2022 PYQs
    {"id": "PYQ-2022-001", "year": 2022, "subject": "Economy", "topic": "International Organizations", "subtopic": "IMF", "question": '"Rapid Financing Instrument" and "Rapid Credit Facility" are related to lending by:', "options": {"a": "ADB", "b": "IMF", "c": "World Bank", "d": "NDB"}, "correct": "b", "explanation": "Both RFI and RCF are IMF lending instruments.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2022-002", "year": 2022, "subject": "Economy", "topic": "Exchange Rate", "subtopic": "NEER/REER", "question": "Consider: 1. Increase in NEER indicates rupee appreciation. 2. Increase in REER indicates rupee appreciation.", "options": {"a": "1 only", "b": "2 only", "c": "Both", "d": "Neither"}, "correct": "c", "explanation": "Both are correct. NEER (trade-weighted) and REER (inflation-adjusted) increases both indicate appreciation.", "difficulty": "medium", "type": "StatementBased"},
    {"id": "PYQ-2022-003", "year": 2022, "subject": "Geography", "topic": "Climatology", "subtopic": "Solar Storms", "question": "Effects of major solar storm: 1. GPS failure 2. Tsunamis in equator 3. Power grid damage", "options": {"a": "1 and 2", "b": "2 and 3", "c": "1 and 3", "d": "All three"}, "correct": "c", "explanation": "Solar storms disrupt GPS and damage power grids. Tsunamis are caused by earthquakes, not solar storms.", "difficulty": "medium", "type": "StatementBased"},
    {"id": "PYQ-2022-004", "year": 2022, "subject": "Environment", "topic": "Agriculture", "subtopic": "SRI", "question": "SRI (alternate wetting/drying) results in: 1. Reduced seed 2. Reduced methane 3. Higher yield", "options": {"a": "1 and 2", "b": "2 and 3", "c": "1 and 3", "d": "All three"}, "correct": "d", "explanation": "SRI gives all three benefits: 80-90% less seed, reduced methane, 20-50% higher yield.", "difficulty": "easy", "type": "StatementBased"},
    {"id": "PYQ-2022-005", "year": 2022, "subject": "Science", "topic": "IT", "subtopic": "Web 3.0", "question": "Consider Web 3.0: 1. Users control their data 2. Blockchain apps possible", "options": {"a": "1 only", "b": "2 only", "c": "Both", "d": "Neither"}, "correct": "c", "explanation": "Both are correct. Web 3.0 is decentralized blockchain internet.", "difficulty": "easy", "type": "StatementBased"},

    # Additional questions for robust testing
    {"id": "PYQ-2021-001", "year": 2021, "subject": "Polity", "topic": "Parliament", "subtopic": "Money Bill", "question": "A Money Bill under Article 110 can be introduced in:", "options": {"a": "Lok Sabha only", "b": "Rajya Sabha only", "c": "Either House", "d": "Joint Session"}, "correct": "a", "explanation": "Money Bills can only be introduced in Lok Sabha on President's recommendation.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2021-002", "year": 2021, "subject": "Economy", "topic": "Banking", "subtopic": "RBI Tools", "question": "Which is NOT a quantitative tool of RBI monetary policy?", "options": {"a": "Bank Rate", "b": "OMO", "c": "SLR", "d": "Margin Requirements"}, "correct": "d", "explanation": "Margin requirements are qualitative/selective credit control, not quantitative.", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2021-003", "year": 2021, "subject": "Geography", "topic": "Physical Geography", "subtopic": "Ring of Fire", "question": "The Ring of Fire is associated with:", "options": {"a": "Atlantic", "b": "Pacific", "c": "Indian", "d": "Arctic"}, "correct": "b", "explanation": "The Ring of Fire is in the Pacific Ocean with 75% of active volcanoes and 90% of earthquakes.", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2021-004", "year": 2021, "subject": "Environment", "topic": "Biodiversity", "subtopic": "Hotspots", "question": "Which is NOT a biodiversity hotspot in India?", "options": {"a": "Western Ghats", "b": "Himalayas", "c": "Sundarbans", "d": "Indo-Burma"}, "correct": "c", "explanation": "India has 4 hotspots: Western Ghats, Himalayas, Indo-Burma, Sundaland. Sundarbans is not one.", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2020-001", "year": 2020, "subject": "Polity", "topic": "Fundamental Rights", "subtopic": "Equality", "question": "Article 14 guarantees equality before law to:", "options": {"a": "Citizens only", "b": "Persons (including non-citizens)", "c": "Indian citizens residing in India", "d": "Natural persons only"}, "correct": "b", "explanation": "Article 14 uses 'persons' not 'citizens', so it applies to all within Indian territory.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2020-002", "year": 2020, "subject": "Economy", "topic": "Fiscal Policy", "subtopic": "Deficits", "question": "Primary Deficit equals:", "options": {"a": "Fiscal Deficit - Interest Payments", "b": "Revenue Deficit - Interest", "c": "Fiscal Deficit + Interest", "d": "Total Expenditure - Total Receipts"}, "correct": "a", "explanation": "Primary Deficit = Fiscal Deficit - Interest Payments on previous borrowings.", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2020-003", "year": 2020, "subject": "Science", "topic": "Biotechnology", "subtopic": "CRISPR", "question": "CRISPR-Cas9 is primarily used for:", "options": {"a": "Cloning", "b": "Gene editing", "c": "DNA fingerprinting", "d": "Stem cells"}, "correct": "b", "explanation": "CRISPR-Cas9 is a revolutionary gene editing technology (Nobel Prize 2020).", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2019-001", "year": 2019, "subject": "Polity", "topic": "Parliament", "subtopic": "Prorogation", "question": "Prorogation of a Lok Sabha by the President requires:", "options": {"a": "Cabinet advice", "b": "Parliament resolution", "c": "Supreme Court approval", "d": "No approval needed"}, "correct": "a", "explanation": "The President prorogues the House on the advice of the Council of Ministers.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2019-002", "year": 2019, "subject": "Economy", "topic": "External Sector", "subtopic": "FEMA/FERA", "question": "FEMA replaced FERA in which year?", "options": {"a": "1997", "b": "1999", "c": "2001", "d": "2003"}, "correct": "b", "explanation": "FEMA (Foreign Exchange Management Act) replaced FERA in 1999 to relax foreign exchange controls.", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2018-001", "year": 2018, "subject": "Geography", "topic": "Climatology", "subtopic": "Jet Streams", "question": "Sub-tropical westerly jet streams are caused by:", "options": {"a": "Rotation of Earth only", "b": "Temperature contrast between latitudes", "c": "Monsoon winds only", "d": "Mountain barriers"}, "correct": "b", "explanation": "Jet streams are caused by temperature/pressure contrasts between tropical and sub-tropical air masses.", "difficulty": "medium", "type": "Factual"},
    {"id": "PYQ-2018-002", "year": 2018, "subject": "Science", "topic": "Space", "subtopic": "ISRO", "question": 'Which satellite is used for "South Asia Satellite"?', "options": {"a": "GSAT-9", "b": "GSAT-11", "c": "GSAT-17", "d": "GSAT-29"}, "correct": "a", "explanation": "GSAT-9 was launched as South Asia Satellite (SAARC satellite) in 2017.", "difficulty": "hard", "type": "Factual"},
    {"id": "PYQ-2017-001", "year": 2017, "subject": "Environment", "topic": "Climate Change", "subtopic": "Montreal Protocol", "question": "Montreal Protocol is related to:", "options": {"a": "Ozone depletion", "b": "Climate change", "c": "Biodiversity", "d": "Desertification"}, "correct": "a", "explanation": "Montreal Protocol (1987) phases out ozone-depleting substances like CFCs.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2016-001", "year": 2016, "subject": "Polity", "topic": "Judiciary", "subtopic": "Appointments", "question": "High Court judges are appointed by:", "options": {"a": "President", "b": "Chief Justice of India", "c": "Governor", "d": "Parliament"}, "correct": "a", "explanation": "High Court judges are appointed by the President after consultation with CJI and Governor.", "difficulty": "easy", "type": "Factual"},
    {"id": "PYQ-2015-001", "year": 2015, "subject": "Economy", "topic": "Planning", "subtopic": "NITI Aayog", "question": "NITI Aayog replaced the Planning Commission in:", "options": {"a": "2014", "b": "2015", "c": "2016", "d": "2017"}, "correct": "b", "explanation": "NITI Aayog replaced Planning Commission on 1 January 2015.", "difficulty": "easy", "type": "Factual"},
]


# ====== LAYA ENGINE ======

MISTAKE_TYPES = [
    "conceptual_gap", "confusion_similar", "partial_knowledge",
    "factual_error", "guesswork", "time_pressure", "misinterpretation"
]

SEVERITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def classify_mistake(question, student_answer, time_spent, confidence):
    """Classify mistake type using rule-based + pattern matching."""
    is_unanswered = student_answer is None
    correct_answer = question["options"].get(question["correct"], "Unknown")

    if is_unanswered:
        if time_spent < 30:
            return {"type": "guesswork", "severity": "low", "cause": "Skipped due to low confidence", "remediation": f"Build confidence in {question['topic']} through practice"}
        elif time_spent > 120:
            return {"type": "time_pressure", "severity": "medium", "cause": "Ran out of time", "remediation": "Improve time management; practice timed tests"}
        else:
            return {"type": "partial_knowledge", "severity": "medium", "cause": "Insufficient knowledge", "remediation": f"Study {question['topic']} in {question['subject']} more deeply"}

    # Check for similar option confusion
    if student_answer and question["correct"]:
        correct_text = question["options"].get(question["correct"], "").lower()
        student_text = question["options"].get(student_answer, "").lower()

        if similarity_score(correct_text, student_text) > 0.4:
            return {"type": "confusion_similar", "severity": "high", "cause": "Confused between similar options", "remediation": f"Create comparison tables for {question['topic']} concepts"}

    if confidence == "low":
        return {"type": "guesswork", "severity": "low", "cause": "Guessed with low confidence", "remediation": f"Strengthen {question['topic']} fundamentals"}

    if question["difficulty"] == "hard":
        return {"type": "partial_knowledge", "severity": "medium", "cause": "Partial understanding", "remediation": f"Deep dive into {question['subtopic'] or question['topic']}"}

    # Default: factual error
    severity = "high" if question["difficulty"] == "easy" else "medium"
    return {"type": "factual_error", "severity": severity, "cause": "Factual recall error", "remediation": f"Create flashcards for {question['topic']}"}


def similarity_score(a, b):
    """Calculate word overlap similarity."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0
    intersection = words_a & words_b
    return len(intersection) / max(len(words_a), len(words_b))


def identify_patterns(mistake_cards):
    """Identify recurring patterns in mistakes."""
    patterns = []
    type_groups = {}
    topic_groups = {}
    subject_groups = {}

    for card in mistake_cards:
        mt = card["mistake_type"]
        topic = card["topic"]
        subject = card["subject"]

        type_groups.setdefault(mt, []).append(card)
        topic_groups.setdefault(topic, []).append(card)
        subject_groups.setdefault(subject, []).append(card)

    # Group by mistake type
    for mtype, cards in type_groups.items():
        if len(cards) >= 2:
            severity = "high" if any(c["severity"] in ("critical", "high") for c in cards) else "medium"
            patterns.append({
                "pattern_id": f"type_{mtype}",
                "pattern_name": f"Recurring {mtype.replace('_', ' ')} errors",
                "description": f"{len(cards)} instances of {mtype.replace('_', ' ')} mistakes",
                "affected_topics": list(set(c["topic"] for c in cards)),
                "occurrence_count": len(cards),
                "severity": severity,
                "recommendation": f"Address {mtype.replace('_', ' ')} through targeted practice"
            })

    # Group by subject
    for subject, cards in subject_groups.items():
        if len(cards) >= 2:
            patterns.append({
                "pattern_id": f"subject_{subject.lower().replace(' ', '_')}",
                "pattern_name": f"Weakness in {subject}",
                "description": f"{len(cards)} mistakes across {subject} topics",
                "affected_topics": list(set(c["topic"] for c in cards)),
                "occurrence_count": len(cards),
                "severity": "high" if len(cards) >= 3 else "medium",
                "recommendation": f"Dedicated revision needed for {subject}"
            })

    return sorted(patterns, key=lambda p: SEVERITY_LEVELS.get(p["severity"], 2), reverse=True)


def generate_recommendations(mistake_cards, patterns, subject_performance):
    """Generate personalized recommendations."""
    recommendations = []

    # Focus on weak subjects (< 60% accuracy)
    for perf in subject_performance:
        if perf["accuracy"] < 60:
            recommendations.append({
                "category": "Subject Focus",
                "priority": "HIGH" if perf["accuracy"] < 40 else "MEDIUM",
                "message": f"Focus on {perf['subject']} - accuracy is {perf['accuracy']}%. Recommended: Revise NCERT basics and solve 50+ PYQs.",
                "action_items": [
                    f"Complete NCERT {perf['subject']} fundamentals",
                    f"Solve 30+ PYQs on {', '.join(perf['weak_topics'][:3])}",
                    f"Take 2 sectional tests on {perf['subject']}"
                ]
            })

    # Address common mistake patterns
    if patterns:
        top_pattern = patterns[0]
        recommendations.append({
            "category": "Mistake Pattern",
            "priority": "HIGH",
            "message": f"Your most common mistake: '{top_pattern['pattern_name']}'. {top_pattern['recommendation']}.",
            "action_items": [
                f"Review {top_pattern['occurrence_count']} questions with this pattern",
                f"Practice elimination techniques",
                f"Focus on {', '.join(top_pattern['affected_topics'][:3])}"
            ]
        })

    # Time management
    avg_time = sum(c.get("time_spent", 0) for c in mistake_cards) / len(mistake_cards) if mistake_cards else 0
    if avg_time > 60:
        recommendations.append({
            "category": "Time Management",
            "priority": "MEDIUM",
            "message": f"Average time on wrong answers: {avg_time:.0f}s. Practice timed tests.",
            "action_items": [
                "Take 5 sectional tests with 20-min limit",
                "Practice first-pass elimination",
                "Skip difficult questions on first pass"
            ]
        })

    # Strength maintenance
    for perf in subject_performance:
        if perf["accuracy"] >= 80:
            recommendations.append({
                "category": "Strength Maintenance",
                "priority": "LOW",
                "message": f"Maintain {perf['subject']} ({perf['accuracy']}% accuracy). Focus on advanced questions.",
                "action_items": [
                    f"Solve advanced PYQs on {perf['subject']}",
                    f"Link static topics with current affairs",
                    f"Take 1 sectional test per week"
                ]
            })

    return recommendations


def analyze_test(student_id, session_id, questions, responses, db):
    """Run full Laya analysis on a test session."""

    print(f"\n{'='*60}")
    print(f"  LAYA ENGINE - Analyzing Test: {session_id}")
    print(f"{'='*60}")

    # Step 1: Classify each response
    print("\n[1/6] Classifying responses...")
    response_map = {r["question_id"]: r for r in responses}
    classified = []
    mistake_cards = []

    for q in questions:
        resp = response_map.get(q["id"])
        is_correct = resp and resp["selected_answer"] == q["correct"]

        if is_correct:
            classified.append({"question": q, "correct": True, "unanswered": False})
        else:
            classified.append({"question": q, "correct": False, "unanswered": resp is None or resp["selected_answer"] is None})

            # Generate mistake card
            student_answer = resp["selected_answer"] if resp else None
            time_spent = resp["time_spent_seconds"] if resp else 0
            confidence = resp["confidence"] if resp else "low"

            classification = classify_mistake(q, student_answer, time_spent, confidence)
            student_answer_text = q["options"].get(student_answer, "Unanswered") if student_answer else "Unanswered"

            mistake_card = {
                "id": f"mc-{session_id}-{q['id']}",
                "session_id": session_id,
                "response_id": f"resp-{session_id}-{q['id']}",
                "subject": q["subject"],
                "topic": q["topic"],
                "subtopic": q.get("subtopic", ""),
                "mistake_type": classification["type"],
                "severity": classification["severity"],
                "student_answer": student_answer_text,
                "correct_answer": q["options"].get(q["correct"], "Unknown"),
                "explanation": q["explanation"],
                "root_cause": classification["cause"],
                "remediation": classification["remediation"],
                "confidence_score": 0.8 if classification["type"] != "guesswork" else 0.5,
                "time_spent": time_spent
            }
            mistake_cards.append(mistake_card)

            # Save to database
            db.conn.execute("""
                INSERT OR REPLACE INTO mistake_cards
                (id, session_id, response_id, subject, topic, subtopic, mistake_type,
                 severity, student_answer, correct_answer, explanation, root_cause, remediation, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mistake_card["id"], mistake_card["session_id"], mistake_card["response_id"],
                mistake_card["subject"], mistake_card["topic"], mistake_card["subtopic"],
                mistake_card["mistake_type"], mistake_card["severity"],
                mistake_card["student_answer"], mistake_card["correct_answer"],
                mistake_card["explanation"], mistake_card["root_cause"],
                mistake_card["remediation"], mistake_card["confidence_score"]
            ))
    db.conn.commit()

    # Step 2: Compute statistics
    print("[2/6] Computing statistics...")
    total_correct = sum(1 for c in classified if c["correct"])
    total_incorrect = sum(1 for c in classified if not c["correct"] and not c["unanswered"])
    total_unanswered = sum(1 for c in classified if c["unanswered"])
    accuracy = (total_correct / len(questions)) * 100 if questions else 0
    overall_score = total_correct * 2 - total_incorrect * 0.66

    # Step 3: Identify patterns
    print("[3/6] Identifying patterns...")
    patterns = identify_patterns(mistake_cards)

    # Step 4: Subject-wise performance
    print("[4/6] Computing subject-wise performance...")
    subject_map = {}
    for c in classified:
        subj = c["question"]["subject"]
        if subj not in subject_map:
            subject_map[subj] = {"total": 0, "correct": 0, "incorrect": 0}
        subject_map[subj]["total"] += 1
        if c["correct"]:
            subject_map[subj]["correct"] += 1
        else:
            subject_map[subj]["incorrect"] += 1

    subject_performance = []
    for subj, data in subject_map.items():
        acc = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0
        subject_performance.append({
            "subject": subj,
            "total": data["total"],
            "correct": data["correct"],
            "incorrect": data["incorrect"],
            "accuracy": round(acc, 1),
            "status": "strong" if acc >= 70 else "average" if acc >= 50 else "weak",
            "weak_topics": [c["question"]["topic"] for c in classified if c["question"]["subject"] == subj and not c["correct"]][:3]
        })

    # Step 5: Generate recommendations
    print("[5/6] Generating recommendations...")
    recommendations = generate_recommendations(mistake_cards, patterns, subject_performance)

    for rec in recommendations:
        rec_id = f"rec-{session_id}-{recommendations.index(rec)}"
        db.conn.execute("""
            INSERT OR REPLACE INTO recommendations
            (id, session_id, category, priority, message, action_items_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rec_id, session_id, rec["category"], rec["priority"],
            rec["message"], json.dumps(rec["action_items"])
        ))
    db.conn.commit()

    # Step 6: Save analysis summary
    print("[6/6] Saving analysis...")
    db.conn.execute("""
        INSERT OR REPLACE INTO analysis_sessions
        (id, session_id, overall_score, total_correct, total_incorrect, total_unanswered,
         accuracy_percentage, patterns_json, subject_performance_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"analysis-{session_id}", session_id, overall_score,
        total_correct, total_incorrect, total_unanswered,
        accuracy, json.dumps(patterns), json.dumps(subject_performance)
    ))

    # Update test session
    db.conn.execute("""
        UPDATE test_sessions SET status='completed', completed_at=datetime('now'),
        total_questions=?
        WHERE id=?
    """, (len(questions), session_id))
    db.conn.commit()

    # Assemble analysis
    analysis = {
        "session_id": session_id,
        "student_id": student_id,
        "overall_score": round(overall_score, 2),
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "total_unanswered": total_unanswered,
        "accuracy_percentage": round(accuracy, 1),
        "mistake_cards": mistake_cards,
        "patterns": patterns,
        "subject_performance": subject_performance,
        "recommendations": recommendations,
        "analysis_timestamp": datetime.now().isoformat()
    }

    return analysis


def run_test():
    """Run complete local test with mock student data."""

    print("=" * 70)
    print("  UPSC PRELIMS TEST ANALYSIS ENGINE - LOCAL TEST")
    print("  Using SQLite Database + In-Memory Processing")
    print("=" * 70)

    # Initialize database
    print("\n[INIT] Creating SQLite database...")
    db = LocalDatabase(DB_PATH)
    print(f"  Database: {DB_PATH}")

    # Seed questions
    print("\n[INIT] Seeding question bank...")
    for q in QUESTION_BANK:
        db.conn.execute("""
            INSERT OR REPLACE INTO questions
            (id, year, subject, topic, subtopic, question_text, options_json,
             correct_answer, explanation, difficulty, question_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["id"], q["year"], q["subject"], q["topic"],
            q.get("subtopic", ""), q["question"],
            json.dumps(q["options"]), q["correct"],
            q["explanation"], q["difficulty"], q["type"]
        ))
    db.conn.commit()

    q_count = db.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    print(f"  Loaded {q_count} questions")

    # Create student
    print("\n[INIT] Creating student profile...")
    student_id = "STU001"
    db.conn.execute("""
        INSERT OR REPLACE INTO students (id, name, email, target_exam)
        VALUES (?, ?, ?, ?)
    """, (student_id, "Rahul Sharma", "rahul@example.com", "UPSC CSE 2027"))
    db.conn.commit()
    print(f"  Student: Rahul Sharma (STU001)")

    # Create test session
    session_id = "TEST-2024-MOCK-001"
    db.conn.execute("""
        INSERT OR REPLACE INTO test_sessions (id, student_id, test_name, status, started_at)
        VALUES (?, ?, ?, 'in_progress', datetime('now'))
    """, (session_id, student_id, "UPSC Prelims Mock Test - Full Length"))
    db.conn.commit()
    print(f"  Session: {session_id}")

    # Select 20 questions for the test
    questions = QUESTION_BANK[:20]
    print(f"  Questions: {len(questions)} selected")

    # Generate mock student responses with realistic mistake patterns
    print("\n[TEST] Simulating student responses...")
    responses = []

    for q in questions:
        qid = q["id"]
        correct = q["correct"]

        # Simulate different student behaviors based on subject
        subject = q["subject"]

        if subject == "Polity":
            # Student is WEAK in Polity - gets many wrong
            if qid in ["PYQ-2024-001", "PYQ-2024-003", "PYQ-2022-001"]:
                selected = correct  # Correct
                confidence = "high"
            else:
                # Wrong answers - common confusion
                wrong_options = [k for k in q["options"] if k != correct]
                selected = wrong_options[0] if wrong_options else None
                confidence = "low"
            time_spent = 45 + (hash(qid) % 30)

        elif subject == "Economy":
            # Student is AVERAGE in Economy
            if qid in ["PYQ-2024-002", "PYQ-2023-002"]:
                selected = correct
                confidence = "medium"
            elif qid == "PYQ-2021-002":
                # Confused between similar options
                selected = "d" if correct != "d" else "a"
                confidence = "low"
            else:
                selected = correct
                confidence = "high"
            time_spent = 60 + (hash(qid) % 45)

        elif subject == "Geography":
            # Student is STRONG in Geography
            if qid in ["PYQ-2023-003", "PYQ-2022-003"]:
                selected = correct
                confidence = "high"
            else:
                selected = correct
                confidence = "medium"
            time_spent = 30 + (hash(qid) % 25)

        elif subject == "Environment":
            # Student is AVERAGE in Environment
            if qid in ["PYQ-2024-005", "PYQ-2022-004"]:
                selected = correct
                confidence = "high"
            else:
                selected = None  # Unanswered
                confidence = "low"
            time_spent = 50 + (hash(qid) % 40)

        elif subject == "Science":
            # Student is STRONG in Science
            selected = correct
            confidence = "high"
            time_spent = 25 + (hash(qid) % 20)

        else:
            # Default: mix of correct and incorrect
            if hash(qid) % 3 == 0:
                selected = None
                confidence = "low"
            elif hash(qid) % 2 == 0:
                selected = correct
                confidence = "medium"
            else:
                wrong_options = [k for k in q["options"] if k != correct]
                selected = wrong_options[0] if wrong_options else None
                confidence = "low"
            time_spent = 40 + (hash(qid) % 50)

        resp = {
            "id": f"resp-{session_id}-{qid}",
            "session_id": session_id,
            "question_id": qid,
            "selected_answer": selected,
            "is_correct": selected == correct,
            "time_spent_seconds": time_spent,
            "confidence": confidence,
            "marked_for_review": selected is None
        }
        responses.append(resp)

        db.conn.execute("""
            INSERT OR REPLACE INTO responses
            (id, session_id, question_id, selected_answer, is_correct,
             time_spent_seconds, confidence, marked_for_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resp["id"], resp["session_id"], resp["question_id"],
            resp["selected_answer"], resp["is_correct"],
            resp["time_spent_seconds"], resp["confidence"],
            resp["marked_for_review"]
        ))

    db.conn.commit()
    print(f"  Generated {len(responses)} responses")

    # Run Laya Engine Analysis
    analysis = analyze_test(student_id, session_id, questions, responses, db)

    # Display Results
    print(f"\n{'='*60}")
    print(f"  ANALYSIS RESULTS")
    print(f"{'='*60}")
    print(f"\n  Student: Rahul Sharma (STU001)")
    print(f"  Session: {session_id}")
    print(f"  Score: {analysis['overall_score']:.2f}/40")
    print(f"  Correct: {analysis['total_correct']}/{len(questions)}")
    print(f"  Wrong: {analysis['total_incorrect']}")
    print(f"  Unanswered: {analysis['total_unanswered']}")
    print(f"  Accuracy: {analysis['accuracy_percentage']}%")

    print(f"\n  Subject Performance:")
    for perf in analysis["subject_performance"]:
        icon = "✓" if perf["status"] == "strong" else "✗" if perf["status"] == "weak" else "~"
        print(f"    {icon} {perf['subject']}: {perf['accuracy']}% ({perf['status']})")

    print(f"\n  Top Patterns:")
    for pat in analysis["patterns"][:5]:
        print(f"    • {pat['pattern_name']}: {pat['occurrence_count']} occurrences")

    print(f"\n  Recommendations:")
    for rec in analysis["recommendations"]:
        priority_icon = "🔴" if rec["priority"] == "HIGH" else "🟡" if rec["priority"] == "MEDIUM" else "🟢"
        print(f"    {priority_icon} [{rec['category']}] {rec['message'][:80]}...")

    # Save JSON report
    json_path = OUTPUT_PATH / "test_analysis_report.json"
    with open(json_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"\n  JSON Report: {json_path}")

    # Generate LaTeX PDF
    tex_path = generate_latex_report(analysis, questions)
    print(f"  LaTeX Report: {tex_path}")

    # Database statistics
    print(f"\n{'='*60}")
    print(f"  DATABASE STATISTICS")
    print(f"{'='*60}")
    print(f"  Questions: {db.conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]}")
    print(f"  Students: {db.conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]}")
    print(f"  Sessions: {db.conn.execute('SELECT COUNT(*) FROM test_sessions').fetchone()[0]}")
    print(f"  Responses: {db.conn.execute('SELECT COUNT(*) FROM responses').fetchone()[0]}")
    print(f"  Mistake Cards: {db.conn.execute('SELECT COUNT(*) FROM mistake_cards').fetchone()[0]}")
    print(f"  Recommendations: {db.conn.execute('SELECT COUNT(*) FROM recommendations').fetchone()[0]}")

    # Close database
    db.close()
    print(f"\n{'='*60}")
    print(f"  TEST COMPLETE ✓")
    print(f"{'='*60}")

    return analysis


def generate_latex_report(analysis, questions):
    """Generate a professional PDF report using LaTeX."""

    brandblue = "brandblue"
    wrongred = "wrongred"
    correctgreen = "correctgreen"
    brandgold = "brandgold"

    def esc(s):
        return str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("$", "\\$")

    def acolor(acc):
        if acc >= 70:
            return correctgreen
        elif acc < 50:
            return wrongred
        else:
            return brandgold

    L = []

    L.append(r"\documentclass[a4paper,12pt]{article}")
    L.append(r"\usepackage[utf8]{inputenc}")
    L.append(r"\usepackage{geometry}")
    L.append(r"\usepackage{longtable}")
    L.append(r"\usepackage{array}")
    L.append(r"\usepackage{xcolor}")
    L.append(r"\usepackage{hyperref}")
    L.append(r"\usepackage{titlesec}")
    L.append(r"\usepackage{fancyhdr}")
    L.append(r"\usepackage{enumitem}")

    L.append(r"\geometry{margin=2cm,headheight=15pt}")
    L.append(r"\definecolor{brandblue}{RGB}{30,64,175}")
    L.append(r"\definecolor{wrongred}{RGB}{220,20,60}")
    L.append(r"\definecolor{correctgreen}{RGB}{34,139,34}")
    L.append(r"\definecolor{brandgold}{RGB}{181,135,52}")

    L.append(r"\pagestyle{fancy}")
    L.append(r"\fancyhf{}")
    L.append(r"\fancyhead[L]{\textcolor{brandblue}{\textbf{Approach KAS}}}")
    L.append(r"\fancyhead[R]{\textcolor{brandblue}{\textbf{UPSC Prelims Test Analysis}}}")
    L.append(r"\fancyfoot[L]{\textcolor{gray}{\small kas.approachestoias.com}}")
    L.append(r"\fancyfoot[R]{\textcolor{gray}{\small @ApproachKAS}}")

    L.append(r"\begin{document}")

    L.append(r"\begin{center}")
    L.append(r"\vspace*{1cm}")
    L.append(r"{\Huge\bfseries\color{brandblue} UPSC PRELIMS TEST ANALYSIS}\\[0.5cm]")
    L.append(r"{\Large\color{black} Personalized Performance Report}\\[1cm]")
    L.append(r"\end{center}")

    L.append(r"\section{Executive Summary}")
    L.append(r"\begin{center}")
    L.append(r"\begin{tabular}{|c|c|c|c|c|}")
    L.append(r"\hline")
    L.append(r"\textbf{Score} & \textbf{Correct} & \textbf{Wrong} & \textbf{Unanswered} & \textbf{Accuracy} \\")
    L.append(r"\hline")
    L.append(f"{analysis['overall_score']:.1f} & {analysis['total_correct']} & {analysis['total_incorrect']} & {analysis['total_unanswered']} & {analysis['accuracy_percentage']}\\% \\\\")
    L.append(r"\hline")
    L.append(r"\end{tabular}")
    L.append(r"\end{center}")

    L.append(r"\section{Subject-wise Performance}")
    L.append(r"\begin{center}")
    L.append(r"\begin{tabular}{|l|c|c|c|c|}")
    L.append(r"\hline")
    L.append(r"\textbf{Subject} & \textbf{Total} & \textbf{Correct} & \textbf{Accuracy} & \textbf{Status} \\")
    L.append(r"\hline")
    for perf in analysis["subject_performance"]:
        color = acolor(perf["accuracy"])
        L.append(f"{esc(perf['subject'])} & {perf['total']} & {perf['correct']} & \\textcolor{{{color}}}{{{perf['accuracy']}\\%}} & {perf['status']} \\\\")
        L.append(r"\hline")
    L.append(r"\end{tabular}")
    L.append(r"\end{center}")

    L.append(r"\section{Mistake Patterns}")
    for pat in analysis["patterns"]:
        L.append(r"\subsection*{" + esc(pat["pattern_name"]) + "}")
        L.append(esc(pat["description"]) + r"\\")
        L.append(r"\textbf{Recommendation:} " + esc(pat["recommendation"]) + r"\\")

    L.append(r"\section{Recommendations}")
    for rec in analysis["recommendations"]:
        L.append(r"\subsection*{[" + rec["priority"] + "] " + esc(rec["category"]) + "}")
        L.append(esc(rec["message"]) + r"\\")
        L.append(r"\textbf{Action Items:}")
        L.append(r"\begin{itemize}")
        for item in rec["action_items"]:
            L.append(r"\item " + esc(item))
        L.append(r"\end{itemize}")

    L.append(r"\section{Detailed Mistake Analysis}")
    for card in analysis["mistake_cards"]:
        L.append(r"\subsection*{Question: " + esc(card["topic"]) + "}")
        L.append(r"\textbf{Your Answer:} \textcolor{wrongred}{" + esc(card["student_answer"]) + r"} \\")
        L.append(r"\textbf{Correct Answer:} " + esc(card["correct_answer"]) + r"\\")
        L.append(r"\textbf{Mistake Type:} " + esc(card["mistake_type"]) + r"\\")
        L.append(r"\textbf{Root Cause:} " + esc(card["root_cause"]) + r"\\")
        L.append(r"\textbf{Remediation:} " + esc(card["remediation"]) + r"\\")

    L.append(r"\end{document}")

    tex_path = OUTPUT_PATH / "test_analysis_report.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    # Try to compile PDF
    try:
        import subprocess
        subprocess.run([
            "xelatex", "-interaction=nonstopmode",
            "-output-directory", str(OUTPUT_PATH),
            str(tex_path)
        ], check=True, timeout=120, capture_output=True)
        print(f"  PDF Generated: {OUTPUT_PATH / 'test_analysis_report.pdf'}")
    except Exception as e:
        print(f"  PDF compilation skipped (xelatex may not be in PATH): {e}")

    return tex_path


if __name__ == "__main__":
    analysis = run_test()
