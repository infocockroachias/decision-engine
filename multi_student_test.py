#!/usr/bin/env python3
"""
Multi-Student Profile Testing - UPSC Prelims Laya Engine
=======================================================
Tests different student profiles with various parameters.
Each profile has different strengths, weaknesses, and mistake patterns.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent
DB_PATH = WORKSPACE / "data" / "multi_test.db"
OUTPUT_PATH = WORKSPACE / "output"
OUTPUT_PATH.mkdir(exist_ok=True)

# Clean previous test
if DB_PATH.exists():
    DB_PATH.unlink()

# ====== DATABASE LAYER ======

class LocalDatabase:
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY, name TEXT, email TEXT, target_exam TEXT,
                prep_level TEXT, study_hours_per_day INTEGER, background TEXT
            );
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY, year INTEGER, subject TEXT, topic TEXT,
                subtopic TEXT, question_text TEXT, options_json TEXT,
                correct_answer TEXT, explanation TEXT, difficulty TEXT, question_type TEXT
            );
            CREATE TABLE IF NOT EXISTS test_sessions (
                id TEXT PRIMARY KEY, student_id TEXT, test_name TEXT,
                status TEXT, total_questions INTEGER, started_at TEXT, completed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY, session_id TEXT, question_id TEXT,
                selected_answer TEXT, is_correct BOOLEAN,
                time_spent_seconds INTEGER, confidence TEXT
            );
            CREATE TABLE IF NOT EXISTS mistake_cards (
                id TEXT PRIMARY KEY, session_id TEXT, subject TEXT, topic TEXT,
                subtopic TEXT, mistake_type TEXT, severity TEXT,
                student_answer TEXT, correct_answer TEXT, explanation TEXT,
                root_cause TEXT, remediation TEXT, confidence_score REAL
            );
            CREATE TABLE IF NOT EXISTS recommendations (
                id TEXT PRIMARY KEY, session_id TEXT, category TEXT,
                priority TEXT, message TEXT, action_items_json TEXT
            );
            CREATE TABLE IF NOT EXISTS analysis_sessions (
                id TEXT PRIMARY KEY, session_id TEXT, overall_score REAL,
                total_correct INTEGER, total_incorrect INTEGER,
                total_unanswered INTEGER, accuracy_percentage REAL,
                patterns_json TEXT, subject_performance_json TEXT
            );
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()


# ====== QUESTION BANK (Real UPSC PYQs) ======

QUESTION_BANK = [
    # Polity (7)
    {"id": "P-001", "year": 2024, "subject": "Polity", "topic": "Parliament", "subtopic": "Money Bill", "question": "A Money Bill under Article 110 can be introduced in:", "options": {"a": "Lok Sabha only", "b": "Rajya Sabha only", "c": "Either House", "d": "Joint Session"}, "correct": "a", "explanation": "Money Bills can only be introduced in Lok Sabha.", "difficulty": "easy", "type": "Factual"},
    {"id": "P-002", "year": 2024, "subject": "Polity", "topic": "Fundamental Rights", "subtopic": "Right to Privacy", "question": "Under which Article has SC placed the Right to Privacy?", "options": {"a": "Article 15", "b": "Article 16", "c": "Article 19", "d": "Article 21"}, "correct": "d", "explanation": "K.S. Puttaswamy case recognized Privacy under Article 21.", "difficulty": "easy", "type": "Factual"},
    {"id": "P-003", "year": 2023, "subject": "Polity", "topic": "Prisons", "subtopic": "State Subject", "question": "Consider: I) Prisons managed by State Governments. II) Prison is State subject.", "options": {"a": "I correct", "b": "II correct", "c": "Both correct", "d": "Both incorrect"}, "correct": "c", "explanation": "Both are correct. Prisons is Entry 4, State List.", "difficulty": "medium", "type": "AssertionReason"},
    {"id": "P-004", "year": 2024, "subject": "Polity", "topic": "Parliament", "subtopic": "Prorogation", "question": "Prorogation by President requires:", "options": {"a": "Cabinet advice", "b": "Parliament resolution", "c": "SC approval", "d": "No approval"}, "correct": "a", "explanation": "President prorogues on advice of Council of Ministers.", "difficulty": "easy", "type": "Factual"},
    {"id": "P-005", "year": 2023, "subject": "Polity", "topic": "Parliament", "subtopic": "Finance Bill", "question": "Rajya Sabha can recommend amendments to:", "options": {"a": "Money Bill only", "b": "Finance Bill only", "c": "Both Money and Finance Bills", "d": "Neither"}, "correct": "c", "explanation": "Rajya Sabha can recommend amendments to both types.", "difficulty": "hard", "type": "Factual"},
    {"id": "P-006", "year": 2021, "subject": "Polity", "topic": "Judiciary", "subtopic": "Appointments", "question": "High Court judges are appointed by:", "options": {"a": "President", "b": "CJI", "c": "Governor", "d": "Parliament"}, "correct": "a", "explanation": "HC judges appointed by President after consultation.", "difficulty": "easy", "type": "Factual"},
    {"id": "P-007", "year": 2020, "subject": "Polity", "topic": "Fundamental Rights", "subtopic": "Equality", "question": "Article 14 guarantees equality to:", "options": {"a": "Citizens only", "b": "Persons", "c": "Indian citizens in India", "d": "Natural persons"}, "correct": "b", "explanation": "Article 14 uses 'persons', applying to all in territory.", "difficulty": "easy", "type": "Factual"},

    # Economy (7)
    {"id": "E-001", "year": 2022, "subject": "Economy", "topic": "International Orgs", "subtopic": "IMF", "question": "Rapid Financing Instrument is related to:", "options": {"a": "ADB", "b": "IMF", "c": "World Bank", "d": "NDB"}, "correct": "b", "explanation": "RFI is an IMF lending instrument.", "difficulty": "easy", "type": "Factual"},
    {"id": "E-002", "year": 2022, "subject": "Economy", "topic": "Exchange Rate", "subtopic": "NEER/REER", "question": "Increase in NEER indicates:", "options": {"a": "Rupee depreciation", "b": "Rupee appreciation", "c": "No change", "d": "Uncertain"}, "correct": "b", "explanation": "NEER increase means rupee appreciation against trading partners.", "difficulty": "medium", "type": "Factual"},
    {"id": "E-003", "year": 2023, "subject": "Economy", "topic": "Financial Markets", "subtopic": "InvITs", "question": "Consider: I) InvIT interest is tax-exempt. II) InvITs regulated by SEBI.", "options": {"a": "I incorrect, II correct", "b": "I correct, II incorrect", "c": "Both correct", "d": "Both incorrect"}, "correct": "a", "explanation": "I is incorrect (taxable), II is correct (SEBI).", "difficulty": "hard", "type": "AssertionReason"},
    {"id": "E-004", "year": 2024, "subject": "Economy", "topic": "Financial Markets", "subtopic": "Corporate Bonds", "question": "Who can trade in Corporate Bonds? 1) Insurance 2) Pension Funds 3) Retail", "options": {"a": "1,2", "b": "2,3", "c": "1,3", "d": "All three"}, "correct": "d", "explanation": "All three can trade in Corporate Bonds.", "difficulty": "medium", "type": "StatementBased"},
    {"id": "E-005", "year": 2021, "subject": "Economy", "topic": "Banking", "subtopic": "RBI Tools", "question": "Which is NOT quantitative tool?", "options": {"a": "Bank Rate", "b": "OMO", "c": "SLR", "d": "Margin"}, "correct": "d", "explanation": "Margin requirements are qualitative, not quantitative.", "difficulty": "medium", "type": "Factual"},
    {"id": "E-006", "year": 2020, "subject": "Economy", "topic": "Fiscal Policy", "subtopic": "Deficits", "question": "Primary Deficit =", "options": {"a": "Fiscal - Interest", "b": "Revenue - Interest", "c": "Fiscal + Interest", "d": "Expenditure - Receipts"}, "correct": "a", "explanation": "Primary Deficit = Fiscal Deficit - Interest Payments.", "difficulty": "medium", "type": "Factual"},
    {"id": "E-007", "year": 2019, "subject": "Economy", "topic": "External Sector", "subtopic": "FEMA", "question": "FEMA replaced FERA in:", "options": {"a": "1997", "b": "1999", "c": "2001", "d": "2003"}, "correct": "b", "explanation": "FEMA replaced FERA in 1999.", "difficulty": "medium", "type": "Factual"},

    # Geography (6)
    {"id": "G-001", "year": 2024, "subject": "Geography", "topic": "Climatology", "subtopic": "Coriolis", "question": "Coriolis force: 1) Increases with wind speed 2) Max at poles, zero at equator", "options": {"a": "1 only", "b": "2 only", "c": "Both", "d": "Neither"}, "correct": "c", "explanation": "Coriolis force depends on velocity and latitude.", "difficulty": "medium", "type": "StatementBased"},
    {"id": "G-002", "year": 2024, "subject": "Geography", "topic": "Physical", "subtopic": "Peatlands", "question": "World's largest tropical peatland is in:", "options": {"a": "Congo Basin", "b": "Amazon", "c": "Ganges", "d": "Mekong"}, "correct": "a", "explanation": "Congo Basin (Cuvette Centrale) has largest tropical peatland.", "difficulty": "hard", "type": "Factual"},
    {"id": "G-003", "year": 2023, "subject": "Geography", "topic": "Indian", "subtopic": "Ports", "question": "Kamarajar Port is:", "options": {"a": "First corporatized major port", "b": "Largest private port", "c": "Largest cargo port", "d": "Oldest port"}, "correct": "a", "explanation": "Kamarajar (Ennore) is first corporatized major port.", "difficulty": "medium", "type": "Factual"},
    {"id": "G-004", "year": 2023, "subject": "Geography", "topic": "Physical", "subtopic": "Minerals", "question": "Ilmenite and rutile are sources of:", "options": {"a": "Zinc", "b": "Titanium", "c": "Copper", "d": "Lead"}, "correct": "b", "explanation": "Ilmenite (FeTiO3) and Rutile (TiO2) are titanium ores.", "difficulty": "easy", "type": "Factual"},
    {"id": "G-005", "year": 2018, "subject": "Geography", "topic": "Climatology", "subtopic": "Jet Streams", "question": "Sub-tropical westerly jet streams are caused by:", "options": {"a": "Earth rotation", "b": "Temperature contrast", "c": "Monsoon", "d": "Mountains"}, "correct": "b", "explanation": "Jet streams are caused by temperature/pressure contrasts.", "difficulty": "medium", "type": "Factual"},
    {"id": "G-006", "year": 2022, "subject": "Geography", "topic": "Climatology", "subtopic": "Solar Storms", "question": "Solar storm effects: 1) GPS failure 2) Tsunamis 3) Power grid damage", "options": {"a": "1,2", "b": "2,3", "c": "1,3", "d": "All"}, "correct": "c", "explanation": "Solar storms affect GPS and power grids, not tsunamis.", "difficulty": "medium", "type": "StatementBased"},

    # Environment (5)
    {"id": "EN-001", "year": 2024, "subject": "Environment", "topic": "Pollution", "subtopic": "PFAS", "question": "PFAS: 1) Found in water 2) Called 'forever chemicals'", "options": {"a": "1 only", "b": "2 only", "c": "Both", "d": "Neither"}, "correct": "c", "explanation": "PFAS are forever chemicals found in water sources.", "difficulty": "easy", "type": "StatementBased"},
    {"id": "EN-002", "year": 2024, "subject": "Environment", "topic": "Biodiversity", "subtopic": "Legumes", "question": "How many are pea family? 1) Groundnut 2) Horse-gram 3) Soybean", "options": {"a": "One", "b": "Two", "c": "All three", "d": "None"}, "correct": "c", "explanation": "All three are Fabaceae (legumes).", "difficulty": "medium", "type": "Factual"},
    {"id": "EN-003", "year": 2022, "subject": "Environment", "topic": "Agriculture", "subtopic": "SRI", "question": "SRI gives: 1) Less seed 2) Less methane 3) Higher yield", "options": {"a": "1,2", "b": "2,3", "c": "1,3", "d": "All three"}, "correct": "d", "explanation": "SRI provides all three benefits.", "difficulty": "easy", "type": "StatementBased"},
    {"id": "EN-004", "year": 2023, "subject": "Environment", "topic": "Biodiversity", "subtopic": "Deciduous", "question": "How many are deciduous? 1) Jackfruit 2) Mahua 3) Teak", "options": {"a": "One", "b": "Two", "c": "All three", "d": "None"}, "correct": "c", "explanation": "All three are deciduous trees.", "difficulty": "hard", "type": "Factual"},
    {"id": "EN-005", "year": 2017, "subject": "Environment", "topic": "Climate Change", "subtopic": "Montreal Protocol", "question": "Montreal Protocol is related to:", "options": {"a": "Ozone depletion", "b": "Climate change", "c": "Biodiversity", "d": "Desertification"}, "correct": "a", "explanation": "Montreal Protocol phases out ozone-depleting substances.", "difficulty": "easy", "type": "Factual"},

    # Science (5)
    {"id": "S-001", "year": 2024, "subject": "Science", "topic": "Space", "subtopic": "Fuel Cells", "question": "Hydrogen fuel cell exhaust is:", "options": {"a": "CO2", "b": "Water vapour", "c": "NOx", "d": "CO2 + Water"}, "correct": "b", "explanation": "Hydrogen fuel cells produce only water vapour.", "difficulty": "easy", "type": "Factual"},
    {"id": "S-002", "year": 2023, "subject": "Science", "topic": "Biology", "subtopic": "Tool Use", "question": "Which makes tools to scrape insects?", "options": {"a": "Chimpanzee", "b": "Orangutan", "c": "Eagle", "d": "Crow"}, "correct": "a", "explanation": "Chimpanzees use sticks to extract insects.", "difficulty": "easy", "type": "Factual"},
    {"id": "S-003", "year": 2020, "subject": "Science", "topic": "Biotech", "subtopic": "CRISPR", "question": "CRISPR-Cas9 is used for:", "options": {"a": "Cloning", "b": "Gene editing", "c": "Fingerprinting", "d": "Stem cells"}, "correct": "b", "explanation": "CRISPR-Cas9 is a gene editing technology.", "difficulty": "medium", "type": "Factual"},
    {"id": "S-004", "year": 2022, "subject": "Science", "topic": "IT", "subtopic": "Web 3.0", "question": "Web 3.0: 1) User controls data 2) Blockchain apps", "options": {"a": "1 only", "b": "2 only", "c": "Both", "d": "Neither"}, "correct": "c", "explanation": "Web 3.0 is decentralized with user data control.", "difficulty": "easy", "type": "StatementBased"},
    {"id": "S-005", "year": 2018, "subject": "Science", "topic": "Space", "subtopic": "Satellites", "question": "South Asia Satellite is:", "options": {"a": "GSAT-9", "b": "GSAT-11", "c": "GSAT-17", "d": "GSAT-29"}, "correct": "a", "explanation": "GSAT-9 was launched as South Asia Satellite.", "difficulty": "hard", "type": "Factual"},
]


# ====== STUDENT PROFILES ======

STUDENT_PROFILES = [
    {
        "id": "STU-001",
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "prep_level": "intermediate",
        "study_hours": 4,
        "background": "Engineering graduate, working professional",
        "strengths": ["Geography", "Science"],
        "weaknesses": ["Polity", "Economy"],
        "mistake_tendencies": ["confusion_similar", "guesswork"],
        "avg_time_per_question": 45,
    },
    {
        "id": "STU-002",
        "name": "Priya Patel",
        "email": "priya@example.com",
        "prep_level": "advanced",
        "study_hours": 8,
        "background": "Law graduate, full-time aspirant",
        "strengths": ["Polity", "Environment"],
        "weaknesses": ["Science", "Geography"],
        "mistake_tendencies": ["time_pressure"],
        "avg_time_per_question": 35,
    },
    {
        "id": "STU-003",
        "name": "Amit Kumar",
        "email": "amit@example.com",
        "prep_level": "beginner",
        "study_hours": 2,
        "background": "Commerce student, first attempt",
        "strengths": ["Economy"],
        "weaknesses": ["Polity", "Geography", "Science", "Environment"],
        "mistake_tendencies": ["guesswork", "partial_knowledge"],
        "avg_time_per_question": 60,
    },
    {
        "id": "STU-004",
        "name": "Sneha Reddy",
        "email": "sneha@example.com",
        "prep_level": "advanced",
        "study_hours": 10,
        "background": "Medicine graduate, 2nd attempt",
        "strengths": ["Science", "Environment"],
        "weaknesses": ["Economy", "Polity"],
        "mistake_tendencies": ["factual_error"],
        "avg_time_per_question": 30,
    },
    {
        "id": "STU-005",
        "name": "Vikram Singh",
        "email": "vikram@example.com",
        "prep_level": "intermediate",
        "study_hours": 6,
        "background": "History graduate, teaching job",
        "strengths": ["Polity", "Environment"],
        "weaknesses": ["Science", "Economy"],
        "mistake_tendencies": ["misinterpretation", "partial_knowledge"],
        "avg_time_per_question": 50,
    },
]


# ====== ENGINE ======

def classify_mistake(question, student_answer, time_spent, confidence):
    is_unanswered = student_answer is None
    correct = question["correct"]
    opts = question["options"]

    if is_unanswered:
        if time_spent < 30:
            return {"type": "guesswork", "severity": "low", "cause": "Skipped - low confidence", "remediation": f"Build confidence in {question['topic']}"}
        elif time_spent > 120:
            return {"type": "time_pressure", "severity": "medium", "cause": "Ran out of time", "remediation": "Improve time management"}
        else:
            return {"type": "partial_knowledge", "severity": "medium", "cause": "Insufficient knowledge", "remediation": f"Study {question['topic']} deeply"}

    if student_answer == correct:
        return None

    correct_text = opts.get(correct, "").lower()
    student_text = opts.get(student_answer, "").lower()

    if similarity_score(correct_text, student_text) > 0.3:
        return {"type": "confusion_similar", "severity": "high", "cause": "Confused similar options", "remediation": f"Comparison tables for {question['topic']}"}

    if confidence == "low":
        return {"type": "guesswork", "severity": "low", "cause": "Low confidence guess", "remediation": f"Strengthen {question['topic']} fundamentals"}

    if question["difficulty"] == "hard":
        return {"type": "partial_knowledge", "severity": "medium", "cause": "Partial understanding", "remediation": f"Advanced study of {question['subtopic'] or question['topic']}"}

    severity = "high" if question["difficulty"] == "easy" else "medium"
    return {"type": "factual_error", "severity": severity, "cause": "Factual recall error", "remediation": f"Flashcards for {question['topic']}"}


def similarity_score(a, b):
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0
    return len(words_a & words_b) / max(len(words_a), len(words_b))


def identify_patterns(mistake_cards):
    patterns = []
    type_groups = {}
    topic_groups = {}

    for mc in mistake_cards:
        type_groups.setdefault(mc["mistake_type"], []).append(mc)
        topic_groups.setdefault(mc["topic"], []).append(mc)

    for mtype, cards in type_groups.items():
        if len(cards) >= 2:
            severity = "high" if any(c["severity"] in ("critical", "high") for c in cards) else "medium"
            patterns.append({
                "pattern_name": f"Recurring {mtype.replace('_', ' ')}",
                "count": len(cards),
                "severity": severity,
                "topics": list(set(c["topic"] for c in cards)),
            })

    for topic, cards in topic_groups.items():
        if len(cards) >= 2:
            patterns.append({
                "pattern_name": f"Weakness in {topic}",
                "count": len(cards),
                "severity": "high" if len(cards) >= 3 else "medium",
                "topics": [topic],
            })

    return sorted(patterns, key=lambda p: p["count"], reverse=True)


def generate_recommendations(mistake_cards, patterns, subject_performance):
    recs = []

    for perf in subject_performance:
        if perf["accuracy"] < 60:
            recs.append({
                "category": "Subject Focus",
                "priority": "HIGH" if perf["accuracy"] < 40 else "MEDIUM",
                "message": f"Focus on {perf['subject']} ({perf['accuracy']}% accuracy)",
                "actions": [f"Revise NCERT {perf['subject']}", f"Solve 50+ PYQs", f"Take 2 sectional tests"]
            })

    if patterns:
        top = patterns[0]
        recs.append({
            "category": "Mistake Pattern",
            "priority": "HIGH",
            "message": f"Most common: {top['pattern_name']} ({top['count']}x)",
            "actions": [f"Review {top['count']} questions", "Practice elimination", f"Focus on {', '.join(top['topics'][:3])}"]
        })

    avg_time = sum(c.get("time_spent", 0) for c in mistake_cards) / len(mistake_cards) if mistake_cards else 0
    if avg_time > 60:
        recs.append({
            "category": "Time Management",
            "priority": "MEDIUM",
            "message": f"Avg time on wrong: {avg_time:.0f}s. Practice timed tests.",
            "actions": ["Take 5 timed tests", "First-pass elimination", "Skip difficult first"]
        })

    for perf in subject_performance:
        if perf["accuracy"] >= 80:
            recs.append({
                "category": "Strength",
                "priority": "LOW",
                "message": f"Maintain {perf['subject']} ({perf['accuracy']}%)",
                "actions": ["Advanced PYQs", "Link with current affairs"]
            })

    return recs


def simulate_student_response(student, question):
    """Simulate a student response based on their profile."""
    import random
    random.seed(hash(student["id"] + question["id"]))

    subject = question["subject"]
    correct = question["correct"]
    difficulty = question["difficulty"]
    is_strength = subject in student["strengths"]
    is_weakness = subject in student["weaknesses"]

    # Base probability of correct answer
    base_prob = 0.7 if is_strength else 0.3 if is_weakness else 0.5

    # Adjust for difficulty
    if difficulty == "easy":
        base_prob += 0.15
    elif difficulty == "hard":
        base_prob -= 0.15

    # Determine answer
    rand = random.random()
    if rand < base_prob:
        selected = correct
        confidence = "high"
    elif rand < base_prob + 0.15:
        # Wrong but close (similar confusion)
        wrong_opts = [k for k in question["options"] if k != correct]
        selected = wrong_opts[0] if wrong_opts else None
        confidence = "low"
    elif rand < base_prob + 0.25:
        selected = None
        confidence = "low"
    else:
        wrong_opts = [k for k in question["options"] if k != correct]
        selected = random.choice(wrong_opts) if wrong_opts else None
        confidence = "medium"

    # Time spent based on profile and correctness
    base_time = student["avg_time_per_question"]
    if selected == correct:
        time_spent = base_time - 10
    elif selected is None:
        time_spent = base_time + 30
    else:
        time_spent = base_time + 15

    return selected, max(15, time_spent), confidence


def run_student_test(db, student, questions, test_num):
    """Run a complete test for one student."""
    session_id = f"TEST-{student['id']}-{test_num}"

    # Create session
    db.conn.execute("""
        INSERT INTO test_sessions (id, student_id, test_name, status, started_at)
        VALUES (?, ?, ?, 'in_progress', datetime('now'))
    """, (session_id, student["id"], f"Mock Test #{test_num}"))

    # Simulate responses
    responses = []
    for q in questions:
        selected, time_spent, confidence = simulate_student_response(student, q)
        resp = {
            "id": f"resp-{session_id}-{q['id']}",
            "session_id": session_id,
            "question_id": q["id"],
            "selected_answer": selected,
            "is_correct": selected == q["correct"],
            "time_spent_seconds": time_spent,
            "confidence": confidence,
        }
        responses.append(resp)

        db.conn.execute("""
            INSERT INTO responses (id, session_id, question_id, selected_answer, is_correct, time_spent_seconds, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (resp["id"], resp["session_id"], resp["question_id"], resp["selected_answer"],
              resp["is_correct"], resp["time_spent_seconds"], resp["confidence"]))

    db.conn.commit()

    # Analyze
    mistake_cards = []
    subject_map = {}

    for r in responses:
        q = next(q for q in questions if q["id"] == r["question_id"])
        subj = q["subject"]
        if subj not in subject_map:
            subject_map[subj] = {"total": 0, "correct": 0, "incorrect": 0}
        subject_map[subj]["total"] += 1

        if r["is_correct"]:
            subject_map[subj]["correct"] += 1
        else:
            subject_map[subj]["incorrect"] += 1
            classification = classify_mistake(q, r["selected_answer"], r["time_spent_seconds"], r["confidence"])
            if classification:
                card = {
                    "id": f"mc-{session_id}-{q['id']}",
                    "session_id": session_id,
                    "subject": subj,
                    "topic": q["topic"],
                    "subtopic": q.get("subtopic", ""),
                    "mistake_type": classification["type"],
                    "severity": classification["severity"],
                    "student_answer": q["options"].get(r["selected_answer"], "Unanswered") if r["selected_answer"] else "Unanswered",
                    "correct_answer": q["options"].get(q["correct"], "Unknown"),
                    "explanation": q["explanation"],
                    "root_cause": classification["cause"],
                    "remediation": classification["remediation"],
                    "confidence_score": 0.8,
                }
                mistake_cards.append(card)

                db.conn.execute(
                    "INSERT INTO mistake_cards (id, session_id, subject, topic, subtopic, mistake_type, severity, student_answer, correct_answer, explanation, root_cause, remediation, confidence_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (card["id"], card["session_id"], card["subject"], card["topic"],
                     card["subtopic"], card["mistake_type"], card["severity"],
                     card["student_answer"], card["correct_answer"], card["explanation"],
                     card["root_cause"], card["remediation"], card["confidence_score"])
                )

    db.conn.commit()

    # Compute stats
    total_correct = sum(1 for r in responses if r["is_correct"])
    total_incorrect = sum(1 for r in responses if not r["is_correct"] and r["selected_answer"] is not None)
    total_unanswered = sum(1 for r in responses if r["selected_answer"] is None)
    accuracy = (total_correct / len(responses)) * 100 if responses else 0

    # Subject performance
    subject_perf = []
    for subj, data in subject_map.items():
        acc = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0
        subject_perf.append({
            "subject": subj, "total": data["total"], "correct": data["correct"],
            "accuracy": round(acc, 1), "status": "strong" if acc >= 70 else "average" if acc >= 50 else "weak"
        })

    patterns = identify_patterns(mistake_cards)
    recommendations = generate_recommendations(mistake_cards, patterns, subject_perf)

    for i, rec in enumerate(recommendations):
        rec_id = f"rec-{session_id}-{i}"
        db.conn.execute("""
            INSERT INTO recommendations (id, session_id, category, priority, message, action_items_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rec_id, session_id, rec["category"], rec["priority"], rec["message"], json.dumps(rec["actions"])))

    db.conn.execute("""
        UPDATE test_sessions SET status='completed', completed_at=datetime('now'), total_questions=?
        WHERE id=?
    """, (len(questions), session_id))

    db.conn.commit()

    return {
        "student": student,
        "session": session_id,
        "correct": total_correct,
        "incorrect": total_incorrect,
        "unanswered": total_unanswered,
        "accuracy": round(accuracy, 1),
        "mistakes": len(mistake_cards),
        "patterns": len(patterns),
        "subject_perf": subject_perf,
    }


def main():
    print("=" * 70)
    print("  MULTI-STUDENT PROFILE TESTING")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    db = LocalDatabase(DB_PATH)

    # Seed questions
    for q in QUESTION_BANK:
        db.conn.execute("""
            INSERT OR REPLACE INTO questions
            (id, year, subject, topic, subtopic, question_text, options_json,
             correct_answer, explanation, difficulty, question_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (q["id"], q["year"], q["subject"], q["topic"],
              q.get("subtopic", ""), q["question"], json.dumps(q["options"]),
              q["correct"], q["explanation"], q["difficulty"], q["type"]))
    db.conn.commit()

    q_count = db.conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    print(f"\n[DB] Questions loaded: {q_count}")

    # Seed students
    for s in STUDENT_PROFILES:
        db.conn.execute("""
            INSERT OR REPLACE INTO students
            (id, name, email, target_exam, prep_level, study_hours_per_day, background)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (s["id"], s["name"], s["email"], "UPSC CSE 2027", s["prep_level"], s["study_hours"], s["background"]))
    db.conn.commit()

    s_count = db.conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    print(f"[DB] Student profiles created: {s_count}")

    # Run tests
    questions = QUESTION_BANK[:20]  # Use 20 questions per test
    results = []

    for student in STUDENT_PROFILES:
        result = run_student_test(db, student, questions, 1)
        results.append(result)

    # Display Results
    print(f"\n{'='*70}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*70}")

    print(f"\n{'Name':<15} {'Prep':<10} {'Score':>6} {'Acc%':>6} {'Mistakes':>8} {'Patterns':>8}")
    print("-" * 60)

    for r in results:
        print(f"{r['student']['name']:<15} {r['student']['prep_level']:<10} {r['correct']:>6} {r['accuracy']:>6.1f} {r['mistakes']:>8} {r['patterns']:>8}")

    # Detailed per-student
    for r in results:
        print(f"\n{'─'*60}")
        print(f"  {r['student']['name']} ({r['student']['prep_level']})")
        print(f"  Background: {r['student']['background']}")
        print(f"  Study hours/day: {r['student']['study_hours']}")
        print(f"  Score: {r['correct']}/{len(questions)} ({r['accuracy']}% accuracy)")
        print(f"  Mistakes: {r['mistakes']} | Patterns: {r['patterns']}")
        print(f"  Subjects:")
        for sp in r["subject_perf"]:
            icon = "✓" if sp["status"] == "strong" else "✗" if sp["status"] == "weak" else "~"
            print(f"    {icon} {sp['subject']}: {sp['accuracy']}%")

    # Save JSON
    report_path = OUTPUT_PATH / "multi_student_report.json"
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "total_questions": len(questions),
                    "total_students": len(STUDENT_PROFILES), "results": results}, f, indent=2, default=str)
    print(f"\n[OUTPUT] JSON report: {report_path}")

    # Database stats
    print(f"\n{'='*70}")
    print(f"  DATABASE STATISTICS")
    print(f"{'='*70}")
    print(f"  Questions:        {db.conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]}")
    print(f"  Students:         {db.conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]}")
    print(f"  Test Sessions:    {db.conn.execute('SELECT COUNT(*) FROM test_sessions').fetchone()[0]}")
    print(f"  Responses:        {db.conn.execute('SELECT COUNT(*) FROM responses').fetchone()[0]}")
    print(f"  Mistake Cards:    {db.conn.execute('SELECT COUNT(*) FROM mistake_cards').fetchone()[0]}")
    print(f"  Recommendations:  {db.conn.execute('SELECT COUNT(*) FROM recommendations').fetchone()[0]}")

    db.close()

    print(f"\n{'='*70}")
    print(f"  ALL TESTS COMPLETE ✓")
    print(f"{'='*70}")
    print(f"\n  Files generated:")
    print(f"    - {OUTPUT_PATH / 'multi_student_report.json'}")
    print(f"    - {DB_PATH}")
    print(f"\n  Next steps:")
    print(f"    1. Review JSON report")
    print(f"    2. Commit and push to GitHub")
    print(f"    3. Deploy to Vercel")


if __name__ == "__main__":
    main()
