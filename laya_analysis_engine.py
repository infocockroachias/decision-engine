#!/usr/bin/env python3
"""
UPSC Prelims Test Analysis Engine (Laya-Adapted)
================================================
Analyzes student test responses, identifies mistake patterns,
and generates focused improvement recommendations.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).parent
DATA_DIR = WORKSPACE / "data"
OUTPUT_DIR = WORKSPACE / "output"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# LongCat API Configuration (OpenAI-compatible)
LONGCAT_API_KEY = os.environ.get("HERMES_CUSTOM_LONGCAT_API_KEY", "")
LONGCAT_BASE_URL = "https://api.longcat.ai/v1"
LONGCAT_MODEL = "LongCat-2.0"

# UPSC Prelims Syllabus Topics
SYLLABUS = {
    "Polity": {
        "topics": [
            "Historical Underpennings & Evolution",
            "Features & Amendments",
            "Basic Structure",
            "Fundamental Rights",
            "Directive Principles",
            "Fundamental Duties",
            "Parliament & State Legislatures",
            "Executive – President, PM, Governor, CM",
            "Judiciary – Supreme Court, High Courts",
            "Centre-State Relations",
            "Emergency Provisions",
            "Panchayati Raj & Municipalities",
            "Constitutional Bodies",
            "Non-Constitutional Bodies",
        ],
        "weightage": 15,
    },
    "History": {
        "topics": [
            "Ancient India – Prehistoric, Indus Vedic",
            "Ancient India – Maurya, Gupta, Post-Gupta",
            "Medieval India – Delhi Sultanate, Mughal",
            "Medieval India – Bhakti & Sufi Movements",
            "Modern India – Advent of Europeans",
            "Modern India – British Policies & Impact",
            "Modern India – Revolt of 1857",
            "Modern India – Social Reform Movements",
            "Modern India – National Movement (1885-1919)",
            "Modern India – National Movement (1919-1947)",
            "Modern India – Gandhi & Mass Movements",
            "Art & Culture – Architecture, Paintings",
            "Art & Culture – Music, Dance, Literature",
        ],
        "weightage": 12,
    },
    "Geography": {
        "topics": [
            "Physical Geography – Geomorphology",
            "Physical Geography – Climatology",
            "Physical Geography – Oceanography",
            "Indian Geography – Physiography",
            "Indian Geography – Drainage System",
            "Indian Geography – Climate & Monsoon",
            "Indian Geography – Soils & Vegetation",
            "Indian Geography – Natural Resources",
            "Indian Geography – Agriculture",
            "Indian Geography – Industries & Transport",
            "World Geography – Continents & Regions",
            "World Geography – Natural Hazards",
        ],
        "weightage": 14,
    },
    "Economy": {
        "topics": [
            "Basic Concepts – GDP, GNP, National Income",
            "Planning & NITI Aayog",
            "Budgeting & Fiscal Policy",
            "Banking & Monetary Policy (RBI)",
            "Financial Markets – Stock Exchange, SEBI",
            "Taxation – Direct & Indirect, GST",
            "Agriculture & Allied Sectors",
            "Industrial Policy & Make in India",
            "Infrastructure & Investment Models",
            "External Sector – BoP, FDI, FPI",
            "Poverty, Unemployment & Inequality",
            "Government Schemes & Programs",
            "International Organizations – IMF, World Bank, WTO",
        ],
        "weightage": 12,
    },
    "Science": {
        "topics": [
            "Physics – Mechanics, Thermodynamics",
            "Physics – Optics, Electromagnetism",
            "Physics – Modern Physics, Nuclear",
            "Chemistry – Organic, Inorganic",
            "Chemistry – Physical, Biochemistry",
            "Biology – Cell Biology, Genetics",
            "Biology – Human Physiology",
            "Biology – Ecology & Environment",
            "Biology – Biotechnology",
            "Science & Technology – Space",
            "Science & Technology – Defence",
            "Science & Technology – IT & Communication",
            "Science & Technology – Nanotech, Robotics",
        ],
        "weightage": 10,
    },
    "Environment": {
        "topics": [
            "Ecology – Basics, Ecosystems",
            "Biodiversity – Hotspots, Conservation",
            "Environmental Pollution – Types & Control",
            "Climate Change – Causes, Impact, Mitigation",
            "Environmental Laws & Policies",
            "International Agreements – Paris, CBD, etc.",
            "Protected Areas – National Parks, Sanctuaries",
            "Wildlife Conservation – Projects, Species",
            "Forest Resources & Management",
            "Water Resources & Management",
        ],
        "weightage": 12,
    },
    "Current Affairs": {
        "topics": [
            "National Events – Government Policies",
            "International Events – Summits, Agreements",
            "Science & Tech – Recent Developments",
            "Awards & Honours",
            "Sports & Games",
            "Reports & Indices",
            "Appointments & Resignations",
            "Important Days & Themes",
            "Defence & Security",
            "Economic Developments",
        ],
        "weightage": 25,
    },
}

# Question Types for UPSC Prelims
QUESTION_TYPES = {
    "factual": "Direct factual recall",
    "statement_based": "Assertion-Reason or Statement-based",
    "matching": "Match the following",
    "mapping": "Map-based or location-based",
    "cause_effect": "Cause and effect relationship",
    "comparison": "Comparison between two concepts",
    "current_affairs": "Current affairs linked to static topic",
    "analytical": "Application/Analytical",
}

# Mistake Pattern Categories
MISTAKE_PATTERNS = {
    "conceptual_gap": "Fundamental misunderstanding of concept",
    "factual_error": "Incorrect factual recall",
    "misinterpretation": "Misread or misunderstood question",
    "confusion_similar": "Confused with similar concept/fact",
    "temporal_error": "Confused timeline or chronology",
    "partial_knowledge": "Incomplete knowledge leading to wrong elimination",
    "overthinking": "Over-analyzed and changed correct answer",
    "guesswork": "Random guessing without basis",
    "time_pressure": "Answered hastily due to time constraint",
    "negative_marking_trap": "Fell for UPSC's negative marking trap",
}

# Severity Levels
SEVERITY_LEVELS = {
    "CRITICAL": {"weight": 4, "description": "Recurring across 3+ tests, high-weightage topic"},
    "HIGH": {"weight": 3, "description": "Recurring in current test or high-weightage topic"},
    "MEDIUM": {"weight": 2, "description": "Isolated mistake in medium-weightage topic"},
    "LOW": {"weight": 1, "description": "Isolated mistake in low-weightage topic"},
}


def create_question_bank():
    """Create a comprehensive 50-question UPSC Prelims mock test."""

    questions = [
        # === POLITY (8 questions) ===
        {
            "q_id": 1,
            "subject": "Polity",
            "topic": "Fundamental Rights",
            "subtopic": "Right to Equality (Article 14-18)",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the following statements:\n1. Article 14 guarantees equality before law to all persons including non-citizens.\n2. Article 15 permits the State to make special provisions for women and children.\n3. Article 16 permits reservation in government jobs based on religion.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "1 and 2 only",
            "correct_index": 1,
            "explanation": "Statement 1 is correct: Article 14 uses 'persons' not 'citizens', so it applies to all. Statement 2 is correct: Article 15(3) allows special provisions for women and children. Statement 3 is incorrect: Article 16 does not permit reservation based on religion (this was struck down in Indra Sawhney case).",
            "syllabus_pointer": "Fundamental Rights - Right to Equality",
            "pyq_pattern": "Similar to 2020 Q1, 2019 Q3",
        },
        {
            "q_id": 2,
            "subject": "Polity",
            "topic": "Parliament",
            "subtopic": "Money Bill vs Financial Bill",
            "type": "factual",
            "difficulty": "easy",
            "question": "A Money Bill under Article 110 of the Constitution can be introduced in:",
            "options": ["Lok Sabha only", "Rajya Sabha only", "Either House of Parliament", "Joint Session of Parliament"],
            "correct": "Lok Sabha only",
            "correct_index": 0,
            "explanation": "Article 110 clearly states that a Money Bill can only be introduced in the Lok Sabha, and only on the recommendation of the President.",
            "syllabus_pointer": "Parliament - Money Bill provisions",
            "pyq_pattern": "Similar to 2018 Q5, 2021 Q12",
        },
        {
            "q_id": 3,
            "subject": "Polity",
            "topic": "Centre-State Relations",
            "subtopic": "President's Rule (Article 356)",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the following statements regarding President's Rule under Article 356:\n1. The proclamation requires approval of both Houses within 2 months.\n2. Judicial review of President's Rule is barred by the Constitution.\n3. The maximum duration for which President's Rule can be extended is 3 years.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 3 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "1 and 3 only",
            "correct_index": 1,
            "explanation": "Statement 1 is correct: Both Houses must approve within 2 months. Statement 2 is incorrect: Judicial review is NOT barred - the Supreme Court in S.R. Bommai case (1994) established that President's Rule can be reviewed. Statement 3 is correct: Maximum duration is 3 years.",
            "syllabus_pointer": "Centre-State Relations - Emergency Provisions",
            "pyq_pattern": "Similar to 2016 Q8, 2022 Q15",
        },
        {
            "q_id": 4,
            "subject": "Polity",
            "topic": "Constitutional Bodies",
            "subtopic": "Election Commission of India",
            "type": "factual",
            "difficulty": "easy",
            "question": "The Chief Election Commissioner of India can be removed from office before expiry of tenure by:",
            "options": [
                "President on the recommendation of Supreme Court",
                "President on the recommendation of Parliament",
                "President on the advice of Prime Minister",
                "Cannot be removed before expiry of tenure",
            ],
            "correct": "President on the recommendation of Parliament",
            "correct_index": 1,
            "explanation": "The CEC can be removed by the President on the recommendation of both Houses of Parliament (special majority).",
            "syllabus_pointer": "Constitutional Bodies - Election Commission",
            "pyq_pattern": "Similar to 2017 Q18, 2023 Q22",
        },
        {
            "q_id": 5,
            "subject": "Polity",
            "topic": "Fundamental Rights",
            "subtopic": "Right to Freedom of Religion (Article 25-28)",
            "type": "analytical",
            "difficulty": "hard",
            "question": "Article 25 guarantees freedom of conscience and the right to profess, practice and propagate religion. However, this right is subject to:",
            "options": [
                "Public order only",
                "Public order and morality only",
                "Public order, morality and health only",
                "Public order, morality, health and other provisions of Part III",
            ],
            "correct": "Public order, morality, health and other provisions of Part III",
            "correct_index": 3,
            "explanation": "Article 25(1) states that all persons are equally entitled to freedom of conscience, subject to public order, morality and health and to the other provisions of Part III.",
            "syllabus_pointer": "Fundamental Rights - Right to Freedom of Religion",
            "pyq_pattern": "Similar to 2019 Q25, 2021 Q30",
        },
        {
            "q_id": 6,
            "subject": "Polity",
            "topic": "Judiciary",
            "subtopic": "Supreme Court - Original and Appellate Jurisdiction",
            "type": "matching",
            "difficulty": "medium",
            "question": "Match the following:\nList-I (Jurisdiction Type)          List-II (Article Number)\nA. Original Jurisdiction           1. Article 131\nB. Appellate Jurisdiction          2. Articles 132-134\nC. Advisory Jurisdiction           3. Article 143\nD. Review Jurisdiction             4. Article 137",
            "options": ["A-1, B-2, C-3, D-4", "A-2, B-1, C-4, D-3", "A-1, B-3, C-2, D-4", "A-3, B-1, C-2, D-4"],
            "correct": "A-1, B-2, C-3, D-4",
            "correct_index": 0,
            "explanation": "Original Jurisdiction - Article 131. Appellate Jurisdiction - Articles 132-134. Advisory Jurisdiction - Article 143. Review Jurisdiction - Article 137.",
            "syllabus_pointer": "Judiciary - Supreme Court Jurisdiction",
            "pyq_pattern": "Similar to 2015 Q40, 2022 Q35",
        },
        {
            "q_id": 7,
            "subject": "Polity",
            "topic": "Panchayati Raj",
            "subtopic": "73rd Amendment Act",
            "type": "factual",
            "difficulty": "medium",
            "question": "The 73rd Constitutional Amendment Act, 1992 added which Parts and Schedules to the Constitution?",
            "options": ["Part IX and 11th Schedule", "Part IXA and 11th Schedule", "Part IX and 12th Schedule", "Part IXA and 12th Schedule"],
            "correct": "Part IX and 11th Schedule",
            "correct_index": 0,
            "explanation": "The 73rd Amendment added Part IX (Articles 243-243O) dealing with Panchayats and the 11th Schedule (Article 243G) containing 29 subjects.",
            "syllabus_pointer": "Panchayati Raj - 73rd Amendment",
            "pyq_pattern": "Similar to 2018 Q45, 2024 Q38",
        },
        {
            "q_id": 8,
            "subject": "Polity",
            "topic": "Fundamental Duties",
            "subtopic": "List of Fundamental Duties",
            "type": "factual",
            "difficulty": "easy",
            "question": "Which of the following is NOT a Fundamental Duty under Article 51A of the Indian Constitution?",
            "options": [
                "To develop scientific temper, humanism and spirit of inquiry",
                "To protect and improve the natural environment",
                "To pay taxes honestly and promptly",
                "To value and preserve the rich heritage of our composite culture",
            ],
            "correct": "To pay taxes honestly and promptly",
            "correct_index": 2,
            "explanation": "Paying taxes is a legal obligation under various tax laws but is NOT listed as a Fundamental Duty under Article 51A.",
            "syllabus_pointer": "Fundamental Duties - Article 51A",
            "pyq_pattern": "Similar to 2017 Q50, 2023 Q55",
        },
        # === HISTORY (7 questions) ===
        {
            "q_id": 9,
            "subject": "History",
            "topic": "Modern India – National Movement",
            "subtopic": "Gandhi & Mass Movements",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the following statements about the Civil Disobedience Movement:\n1. It began with the Dandi March in 1930.\n2. The movement was withdrawn immediately after the Gandhi-Irwin Pact.\n3. Women participated in large numbers in this movement.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "1 and 3 only", "1, 2 and 3"],
            "correct": "1 and 3 only",
            "correct_index": 2,
            "explanation": "Statement 1 is correct: The CDM began with the Salt March (Dandi March). Statement 2 is incorrect: The movement was NOT withdrawn after the Gandhi-Irwin Pact. Statement 3 is correct: Women participated in large numbers.",
            "syllabus_pointer": "Modern India - Civil Disobedience Movement",
            "pyq_pattern": "Similar to 2019 Q12, 2021 Q8",
        },
        {
            "q_id": 10,
            "subject": "History",
            "topic": "Ancient India",
            "subtopic": "Mauryan Empire - Ashoka",
            "type": "factual",
            "difficulty": "easy",
            "question": "The Kalinga War, which changed the life of Ashoka, took place in:",
            "options": ["261 BCE", "273 BCE", "232 BCE", "250 BCE"],
            "correct": "261 BCE",
            "correct_index": 0,
            "explanation": "The Kalinga War took place in 261 BCE, during the 8th year of Ashoka's reign. The massive destruction led to Ashoka's conversion to Buddhism.",
            "syllabus_pointer": "Ancient India - Mauryan Empire",
            "pyq_pattern": "Similar to 2018 Q25, 2022 Q20",
        },
        {
            "q_id": 11,
            "subject": "History",
            "topic": "Medieval India",
            "subtopic": "Mughal Administration",
            "type": "matching",
            "difficulty": "medium",
            "question": "Match the Mughal emperors with their notable contributions:\nA. Akbar – Mansabdari system\nB. Shah Jahan – Built Red Fort, Taj Mahal\nC. Aurangzeb – Expanded to Deccan, strict Islamic policies\nD. Jahangir – Married Nur Jahan, patronized painting",
            "options": ["A-2, B-1, C-3, D-4", "A-1, B-2, C-4, D-3", "A-2, B-3, C-1, D-4", "A-3, B-1, C-2, D-4"],
            "correct": "A-2, B-1, C-3, D-4",
            "correct_index": 0,
            "explanation": "Akbar introduced Mansabdari system. Shah Jahan built Red Fort and Taj Mahal. Aurangzeb expanded empire to Deccan. Jahangir patronized painting.",
            "syllabus_pointer": "Medieval India - Mughal Administration",
            "pyq_pattern": "Similar to 2016 Q30, 2023 Q28",
        },
        {
            "q_id": 12,
            "subject": "History",
            "topic": "Modern India – Social Reform",
            "subtopic": "Social Reform Movements",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the following social reformers and their associated movements:\n1. Jyotirao Phule - Satyashodhak Samaj\n2. Raja Ram Mohan Roy - Brahmo Samaj\n3. Swami Vivekananda - Arya Samaj\nWhich of the above is/are correctly matched?",
            "options": ["1 and 2 only", "2 and 3 only", "1 and 3 only", "1, 2 and 3"],
            "correct": "1 and 2 only",
            "correct_index": 0,
            "explanation": "Statement 1 is correct: Jyotirao Phule founded Satyashodhak Samaj. Statement 2 is correct: Raja Ram Mohan Roy founded Brahmo Samaj. Statement 3 is incorrect: Swami Vivekananda founded Ramakrishna Mission. Arya Samaj was founded by Swami Dayanand Saraswati.",
            "syllabus_pointer": "Modern India - Social Reform Movements",
            "pyq_pattern": "Similar to 2019 Q35, 2024 Q42",
        },
        {
            "q_id": 13,
            "subject": "History",
            "topic": "Modern India – British Policies",
            "subtopic": "Economic Impact of British Rule",
            "type": "cause_effect",
            "difficulty": "hard",
            "question": "The 'Drain of Wealth' theory during British rule in India was propounded by:",
            "options": ["Mahatma Gandhi", "Dadabhai Naoroji", "Raja Ram Mohan Roy", "Bal Gangadhar Tilak"],
            "correct": "Dadabhai Naoroji",
            "correct_index": 1,
            "explanation": "Dadabhai Naoroji first systematically articulated the 'Drain of Wealth' theory in his book 'Poverty and Un-British Rule in India' (1901).",
            "syllabus_pointer": "Modern India - Drain of Wealth Theory",
            "pyq_pattern": "Similar to 2017 Q40, 2022 Q45",
        },
        {
            "q_id": 14,
            "subject": "History",
            "topic": "Art & Culture",
            "subtopic": "Temple Architecture",
            "type": "factual",
            "difficulty": "medium",
            "question": "The Brihadeshwara Temple at Thanjavur, a UNESCO World Heritage Site, was built by:",
            "options": [
                "Krishna I of Rashtrakuta",
                "Rajaraja Chola I",
                "Narasimhavarman II of Pallava",
                "Pulakeshin II of Chalukya",
            ],
            "correct": "Rajaraja Chola I",
            "correct_index": 1,
            "explanation": "The Brihadeshwara Temple was built by Chola emperor Rajaraja I around 1010 CE. It is a masterpiece of Dravidian architecture.",
            "syllabus_pointer": "Art & Culture - Temple Architecture",
            "pyq_pattern": "Similar to 2020 Q48, 2024 Q50",
        },
        {
            "q_id": 15,
            "subject": "History",
            "topic": "Modern India – Revolt of 1857",
            "subtopic": "Causes and Leaders",
            "type": "factual",
            "difficulty": "easy",
            "question": "The 'Doctrine of Lapse' policy, which annexed many Indian princely states, was introduced by:",
            "options": ["Lord Cornwallis", "Lord Wellesley", "Lord Dalhousie", "Lord Canning"],
            "correct": "Lord Dalhousie",
            "correct_index": 2,
            "explanation": "The Doctrine of Lapse was introduced by Lord Dalhousie (Governor-General 1848-1856). This policy was a major cause of the 1857 Revolt.",
            "syllabus_pointer": "Modern India - Doctrine of Lapse",
            "pyq_pattern": "Similar to 2016 Q45, 2021 Q52",
        },
        # === GEOGRAPHY (8 questions) ===
        {
            "q_id": 16,
            "subject": "Geography",
            "topic": "Physical Geography – Climatology",
            "subtopic": "Monsoon Mechanism",
            "type": "cause_effect",
            "difficulty": "hard",
            "question": "The Indian monsoon is primarily caused by:",
            "options": [
                "Rotation of the Earth only",
                "Differential heating of land and sea only",
                "Shift of the Inter-Tropical Convergence Zone (ITCZ) only",
                "Combined effect of differential heating, ITCZ shift, and other factors",
            ],
            "correct": "Combined effect of differential heating, ITCZ shift, and other factors",
            "correct_index": 3,
            "explanation": "The Indian monsoon is a complex phenomenon caused by multiple factors: differential heating, ITCZ shift, Tibetan plateau heating, jet stream patterns, El Niño/La Niña, and Indian Ocean Dipole.",
            "syllabus_pointer": "Physical Geography - Monsoon Mechanism",
            "pyq_pattern": "Similar to 2018 Q55, 2023 Q58",
        },
        {
            "q_id": 17,
            "subject": "Geography",
            "topic": "Indian Geography – Drainage",
            "subtopic": "River Systems",
            "type": "factual",
            "difficulty": "medium",
            "question": "Which of the following rivers does NOT originate from the Amarkantak Hills?",
            "options": ["Narmada", "Son", "Mahanadi", "Johila"],
            "correct": "Mahanadi",
            "correct_index": 2,
            "explanation": "The Amarkantak Hills is the origin of Narmada, Son, and Johila rivers. The Mahanadi originates from the Siwari hills in Chhattisgarh, not Amarkantak.",
            "syllabus_pointer": "Indian Geography - River Systems",
            "pyq_pattern": "Similar to 2017 Q60, 2022 Q55",
        },
        {
            "q_id": 18,
            "subject": "Geography",
            "topic": "Indian Geography – Climate",
            "subtopic": "Climate Regions",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the statements about Koeppen's climate classification of India:\n1. Most peninsular India falls under Tropical Savanna climate (Aw).\n2. The western coast falls under Tropical Monsoon climate (Am).\n3. The Himalayan region falls under Highland climate (H).\nWhich of the statements given above is/are correct?",
            "options": ["1 and 2 only", "2 and 3 only", "1 and 3 only", "1, 2 and 3"],
            "correct": "2 and 3 only",
            "correct_index": 1,
            "explanation": "Statement 1 is incorrect: Most peninsular India falls under Tropical Wet and Dry climate. Statement 2 is correct: Western coast falls under Tropical Monsoon (Am). Statement 3 is correct: Himalayan region falls under Highland climate (H).",
            "syllabus_pointer": "Indian Geography - Climate Classification",
            "pyq_pattern": "Similar to 2019 Q65, 2024 Q62",
        },
        {
            "q_id": 19,
            "subject": "Geography",
            "topic": "Physical Geography – Geomorphology",
            "subtopic": "Earthquakes and Volcanoes",
            "type": "factual",
            "difficulty": "medium",
            "question": "The 'Ring of Fire' is associated with:",
            "options": ["Atlantic Ocean", "Pacific Ocean", "Indian Ocean", "Arctic Ocean"],
            "correct": "Pacific Ocean",
            "correct_index": 1,
            "explanation": "The 'Ring of Fire' is a major area in the Pacific Ocean where many earthquakes and volcanic eruptions occur. About 75% of the world's active volcanoes and 90% of earthquakes occur here.",
            "syllabus_pointer": "Physical Geography - Ring of Fire",
            "pyq_pattern": "Similar to 2016 Q70, 2020 Q68",
        },
        {
            "q_id": 20,
            "subject": "Geography",
            "topic": "Indian Geography – Agriculture",
            "subtopic": "Cropping Patterns",
            "type": "statement_based",
            "difficulty": "hard",
            "question": "Consider the statements about Indian agriculture:\n1. Rice is a kharif crop requiring high rainfall (>100 cm).\n2. Wheat is a rabi crop requiring cool growing season and bright sunshine at ripening.\n3. Cotton is a kharif crop requiring 21°C temperature and 50-75 cm rainfall.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "1, 2 and 3",
            "correct_index": 3,
            "explanation": "All three statements are correct. Rice is kharif needing >100 cm rainfall. Wheat is rabi needing cool season. Cotton is kharif needing 21-27°C and 50-75 cm rainfall.",
            "syllabus_pointer": "Indian Agriculture - Cropping Patterns",
            "pyq_pattern": "Similar to 2018 Q72, 2023 Q70",
        },
        {
            "q_id": 21,
            "subject": "Geography",
            "topic": "World Geography",
            "subtopic": "Natural Hazards",
            "type": "mapping",
            "difficulty": "hard",
            "question": "The 'Coral Triangle', known for the highest marine biodiversity, is located in:",
            "options": ["Caribbean Sea", "Mediterranean Sea", "Southeast Asia (Indo-Pacific)", "Red Sea"],
            "correct": "Southeast Asia (Indo-Pacific)",
            "correct_index": 2,
            "explanation": "The Coral Triangle is in the Western Pacific Ocean around Indonesia, Malaysia, Papua New Guinea, Philippines, Solomon Islands, and Timor-Leste. It contains 76% of the world's coral species.",
            "syllabus_pointer": "World Geography - Coral Triangle",
            "pyq_pattern": "Similar to 2021 Q75, 2024 Q78",
        },
        {
            "q_id": 22,
            "subject": "Geography",
            "topic": "Indian Geography – Soils",
            "subtopic": "Soil Types",
            "type": "comparison",
            "difficulty": "medium",
            "question": "Which of the following statements correctly differentiates between Alluvial and Black soil?",
            "options": [
                "Alluvial soil is found in Deccan region, Black soil in Indo-Gangetic plains",
                "Alluvial soil is rich in iron oxide, Black soil is rich in potash",
                "Alluvial soil is transported by rivers, Black soil is formed by weathering of volcanic rock",
                "Alluvial soil is suitable for cotton, Black soil is suitable for rice",
            ],
            "correct": "Alluvial soil is transported by rivers, Black soil is formed by weathering of volcanic rock",
            "correct_index": 2,
            "explanation": "Alluvial soil is transported and deposited by rivers (Indo-Gangetic plains). Black soil (Regur) is formed by weathering of volcanic basalt rock in the Deccan Trap region.",
            "syllabus_pointer": "Indian Geography - Soil Types",
            "pyq_pattern": "Similar to 2017 Q78, 2022 Q80",
        },
        {
            "q_id": 23,
            "subject": "Geography",
            "topic": "Physical Geography – Oceanography",
            "subtopic": "Ocean Currents",
            "type": "factual",
            "difficulty": "hard",
            "question": "The Humboldt Current, which influences the climate of coastal Peru, is a:",
            "options": ["Warm current in the Atlantic Ocean", "Cold current in the Pacific Ocean", "Warm current in the Indian Ocean", "Cold current in the Atlantic Ocean"],
            "correct": "Cold current in the Pacific Ocean",
            "correct_index": 1,
            "explanation": "The Humboldt Current (Peru Current) is a cold, low-salinity ocean current flowing northward along the western coast of South America.",
            "syllabus_pointer": "Oceanography - Ocean Currents",
            "pyq_pattern": "Similar to 2015 Q82, 2020 Q85",
        },
        # === ECONOMY (7 questions) ===
        {
            "q_id": 24,
            "subject": "Economy",
            "topic": "Banking & Monetary Policy",
            "subtopic": "RBI Tools",
            "type": "factual",
            "difficulty": "medium",
            "question": "Which of the following is NOT a quantitative tool of the Reserve Bank of India's monetary policy?",
            "options": ["Bank Rate", "Open Market Operations", "Statutory Liquidity Ratio", "Margin Requirements"],
            "correct": "Margin Requirements",
            "correct_index": 3,
            "explanation": "Quantitative tools include: Bank Rate, Open Market Operations, CRR, SLR, and Repo/Reverse Repo rates. Margin requirements are qualitative/Selective Credit Control tools.",
            "syllabus_pointer": "Economy - RBI Monetary Policy Tools",
            "pyq_pattern": "Similar to 2019 Q85, 2023 Q88",
        },
        {
            "q_id": 25,
            "subject": "Economy",
            "topic": "Budgeting & Fiscal Policy",
            "subtopic": "Deficit Types",
            "type": "statement_based",
            "difficulty": "hard",
            "question": "Consider the following statements about fiscal deficits:\n1. Fiscal Deficit = Total Expenditure - Total Receipts (excluding borrowing).\n2. Primary Deficit = Fiscal Deficit - Interest Payments.\n3. Effective Revenue Deficit excludes grants for capital asset creation.\nWhich of the statements given above is/are correct?",
            "options": ["1 and 2 only", "2 and 3 only", "1 and 3 only", "1, 2 and 3"],
            "correct": "1, 2 and 3",
            "correct_index": 3,
            "explanation": "All three statements are correct. Fiscal Deficit = Total Expenditure - (Revenue Receipts + Non-debt Capital Receipts). Primary Deficit = Fiscal Deficit - Interest Payments. Effective Revenue Deficit = Revenue Deficit - Grants for creation of capital assets.",
            "syllabus_pointer": "Economy - Fiscal Deficits",
            "pyq_pattern": "Similar to 2018 Q90, 2022 Q92",
        },
        {
            "q_id": 26,
            "subject": "Economy",
            "topic": "Taxation",
            "subtopic": "GST Structure",
            "type": "factual",
            "difficulty": "easy",
            "question": "Under the Goods and Services Tax (GST), the tax rate is decided by:",
            "options": ["Central Government alone", "State Government alone", "GST Council (Centre + States)", "Parliament by simple majority"],
            "correct": "GST Council (Centre + States)",
            "correct_index": 2,
            "explanation": "The GST Council, chaired by the Union Finance Minister and comprising State Finance Ministers, decides tax rates, exemptions, and other GST policies.",
            "syllabus_pointer": "Economy - GST Council",
            "pyq_pattern": "Similar to 2017 Q95, 2021 Q95",
        },
        {
            "q_id": 27,
            "subject": "Economy",
            "topic": "Financial Markets",
            "subtopic": "SEBI and Stock Exchanges",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the statements about SEBI:\n1. SEBI was established in 1992 through an Act of Parliament.\n2. SEBI regulates both primary and secondary markets.\n3. SEBI has the power to penalize insider trading.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "1, 2 and 3",
            "correct_index": 3,
            "explanation": "All three statements are correct. SEBI was given statutory powers through the SEBI Act, 1992. It regulates primary and secondary markets and can penalize insider trading.",
            "syllabus_pointer": "Economy - SEBI Functions",
            "pyq_pattern": "Similar to 2016 Q92, 2020 Q95",
        },
        {
            "q_id": 28,
            "subject": "Economy",
            "topic": "Government Schemes",
            "subtopic": "DBT and Financial Inclusion",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "The 'Direct Benefit Transfer' (DBT) scheme aims to transfer subsidies directly to beneficiaries using:",
            "options": ["Cash transfers only", "Aadhaar-linked bank accounts only", "Aadhaar-linked bank accounts and other digital modes", "Voucher-based system only"],
            "correct": "Aadhaar-linked bank accounts and other digital modes",
            "correct_index": 2,
            "explanation": "DBT transfers subsidies directly to beneficiaries using Aadhaar-linked bank accounts and other digital payment modes. As of 2024, DBT has saved over ₹3 lakh crore.",
            "syllabus_pointer": "Economy - Direct Benefit Transfer",
            "pyq_pattern": "Similar to 2019 Q98, 2023 Q95",
        },
        {
            "q_id": 29,
            "subject": "Economy",
            "topic": "External Sector",
            "subtopic": "Balance of Payments",
            "type": "factual",
            "difficulty": "hard",
            "question": "In India's Balance of Payments, which of the following is recorded in the Capital Account?",
            "options": ["Export of software services", "Foreign Direct Investment (FDI)", "Remittances from NRIs", "Tourism receipts"],
            "correct": "Foreign Direct Investment (FDI)",
            "correct_index": 1,
            "explanation": "The Capital Account records: FDI, FPI/FII, external assistance, NRI deposits, and other capital flows. The Current Account records: trade in goods/services, primary income, and secondary income (remittances).",
            "syllabus_pointer": "Economy - Balance of Payments",
            "pyq_pattern": "Similar to 2018 Q95, 2024 Q98",
        },
        {
            "q_id": 30,
            "subject": "Economy",
            "topic": "Poverty & Unemployment",
            "subtopic": "Measurement Methods",
            "type": "comparison",
            "difficulty": "medium",
            "question": "The poverty line in India was previously based on the Tendulkar Committee method. Which committee is currently responsible for determining poverty estimates?",
            "options": ["Rangarajan Committee", "NITI Aayog", "There is no official poverty estimation currently", "Planning Commission (still functional)"],
            "correct": "There is no official poverty estimation currently",
            "correct_index": 2,
            "explanation": "There is NO official poverty estimation currently being done by the Indian government. The last official estimates were based on Tendulkar Committee methodology (2011-12). The government currently uses the Multidimensional Poverty Index (MPI) by NITI Aayog.",
            "syllabus_pointer": "Economy - Poverty Estimation",
            "pyq_pattern": "Similar to 2020 Q100, 2023 Q98",
        },
        # === SCIENCE (6 questions) ===
        {
            "q_id": 31,
            "subject": "Science",
            "topic": "Physics – Modern Physics",
            "subtopic": "Nuclear Physics",
            "type": "factual",
            "difficulty": "easy",
            "question": "The process of splitting a heavy nucleus into two lighter nuclei is called:",
            "options": ["Nuclear fusion", "Nuclear fission", "Radioactive decay", "Nuclear transmutation"],
            "correct": "Nuclear fission",
            "correct_index": 1,
            "explanation": "Nuclear fission is the splitting of a heavy nucleus (like Uranium-235) into two lighter nuclei, releasing a large amount of energy. This is the principle behind nuclear reactors.",
            "syllabus_pointer": "Science - Nuclear Physics",
            "pyq_pattern": "Similar to 2017 Q102, 2022 Q105",
        },
        {
            "q_id": 32,
            "subject": "Science",
            "topic": "Biology – Biotechnology",
            "subtopic": "CRISPR-Cas9",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "CRISPR-Cas9 technology, which won the Nobel Prize in Chemistry 2020, is primarily used for:",
            "options": ["Cloning animals", "Gene editing", "DNA fingerprinting", "Stem cell therapy"],
            "correct": "Gene editing",
            "correct_index": 1,
            "explanation": "CRISPR-Cas9 is a revolutionary gene editing technology. Jennifer Doudna and Emmanuelle Charpentier won the 2020 Nobel Prize in Chemistry for this technology.",
            "syllabus_pointer": "Science - Gene Editing Technology",
            "pyq_pattern": "Similar to 2020 Q105, 2023 Q108",
        },
        {
            "q_id": 33,
            "subject": "Science",
            "topic": "Science & Technology – Space",
            "subtopic": "ISRO Missions",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "The Chandrayaan-3 mission's Vikram lander successfully soft-landed near which region of the Moon?",
            "options": ["Lunar equator", "Lunar North Pole", "Lunar South Pole", "Lunar far side (Mare Moscoviense)"],
            "correct": "Lunar South Pole",
            "correct_index": 2,
            "explanation": "Chandrayaan-3's Vikram lander successfully soft-landed near the Lunar South Pole on August 23, 2023. This made India the first country to land near the South Pole.",
            "syllabus_pointer": "Science - ISRO Moon Mission",
            "pyq_pattern": "New pattern (2023 current affairs)",
        },
        {
            "q_id": 34,
            "subject": "Science",
            "topic": "Biology – Human Physiology",
            "subtopic": "Immune System",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the statements about antibodies:\n1. Antibodies are produced by T-cells.\n2. Antibodies are proteins called immunoglobulins.\n3. Monoclonal antibodies were used in COVID-19 treatment.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "2 and 3 only",
            "correct_index": 2,
            "explanation": "Statement 1 is incorrect: Antibodies are produced by B-cells (B-lymphocytes), not T-cells. Statement 2 is correct: Antibodies are proteins called immunoglobulins. Statement 3 is correct: Monoclonal antibodies were used in COVID-19 treatment.",
            "syllabus_pointer": "Biology - Immune System",
            "pyq_pattern": "Similar to 2020 Q110, 2022 Q115",
        },
        {
            "q_id": 35,
            "subject": "Science",
            "topic": "Science & Technology – Defence",
            "subtopic": "Missile Systems",
            "type": "factual",
            "difficulty": "medium",
            "question": "The 'BrahMos' missile is a:",
            "options": [
                "Ballistic missile developed indigenously",
                "Supersonic cruise missile developed jointly with Russia",
                "Hypersonic missile developed with USA",
                "Anti-tank missile developed with Israel",
            ],
            "correct": "Supersonic cruise missile developed jointly with Russia",
            "correct_index": 1,
            "explanation": "BrahMos is a supersonic cruise missile (Mach 2.8-3.0) developed jointly by India (DRDO) and Russia (NPO Mashinostroyeniya).",
            "syllabus_pointer": "Science - Defence Technology",
            "pyq_pattern": "Similar to 2019 Q115, 2024 Q118",
        },
        {
            "q_id": 36,
            "subject": "Science",
            "topic": "Chemistry",
            "subtopic": "Green Chemistry",
            "type": "factual",
            "difficulty": "hard",
            "question": "The '12 Principles of Green Chemistry' were developed by:",
            "options": [
                "Paul Anastas and John Warner",
                "Marie Curie and Linus Pauling",
                "Friedrich Wöhler and Justus von Liebig",
                "Robert Bunsen and Gustav Kirchhoff",
            ],
            "correct": "Paul Anastas and John Warner",
            "correct_index": 0,
            "explanation": "The 12 Principles of Green Chemistry were developed by Paul Anastas and John Warner in their 1998 book 'Green Chemistry: Theory and Practice'.",
            "syllabus_pointer": "Chemistry - Green Chemistry",
            "pyq_pattern": "Similar to 2016 Q118, 2021 Q120",
        },
        # === ENVIRONMENT (6 questions) ===
        {
            "q_id": 37,
            "subject": "Environment",
            "topic": "Biodiversity",
            "subtopic": "Biodiversity Hotspots",
            "type": "mapping",
            "difficulty": "medium",
            "question": "Which of the following regions is NOT a biodiversity hotspot in India?",
            "options": ["Western Ghats", "Himalayas", "Sundarbans", "Indo-Burma region"],
            "correct": "Sundarbans",
            "correct_index": 2,
            "explanation": "India has 4 biodiversity hotspots: Western Ghats, Himalayas, Indo-Burma region, and Sundaland (Nicobar Islands). The Sundarbans is a specific ecosystem but NOT classified as a separate biodiversity hotspot.",
            "syllabus_pointer": "Environment - Biodiversity Hotspots",
            "pyq_pattern": "Similar to 2018 Q122, 2023 Q125",
        },
        {
            "q_id": 38,
            "subject": "Environment",
            "topic": "Climate Change",
            "subtopic": "International Agreements",
            "type": "statement_based",
            "difficulty": "hard",
            "question": "Consider the statements about the Paris Agreement:\n1. It aims to limit global warming to well below 2°C, preferably to 1.5°C.\n2. India's target under NDC is to reduce emissions intensity of GDP by 33-35% by 2030.\n3. The agreement is legally binding on all countries.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "1 and 2 only",
            "correct_index": 1,
            "explanation": "Statement 1 is correct: The Paris Agreement aims to limit warming to well below 2°C, preferably 1.5°C. Statement 2 is correct: India's NDC target was 33-35% reduction (now enhanced to 45%). Statement 3 is incorrect: The agreement itself is NOT legally binding on emission targets.",
            "syllabus_pointer": "Environment - Paris Agreement",
            "pyq_pattern": "Similar to 2019 Q125, 2024 Q128",
        },
        {
            "q_id": 39,
            "subject": "Environment",
            "topic": "Protected Areas",
            "subtopic": "Wildlife Conservation",
            "type": "factual",
            "difficulty": "medium",
            "question": "The 'Project Tiger' was launched in which year?",
            "options": ["1972", "1973", "1983", "1991"],
            "correct": "1973",
            "correct_index": 1,
            "explanation": "Project Tiger was launched in 1973 under the Wildlife (Protection) Act, 1972. As of 2024, India has 54 tiger reserves covering over 78,000 sq km.",
            "syllabus_pointer": "Environment - Project Tiger",
            "pyq_pattern": "Similar to 2017 Q128, 2022 Q130",
        },
        {
            "q_id": 40,
            "subject": "Environment",
            "topic": "Environmental Pollution",
            "subtopic": "Air Pollution",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "The 'National Clean Air Programme (NCAP)' aims to reduce PM2.5 and PM10 concentration by what percentage by 2025-26?",
            "options": ["10-20%", "20-30%", "30-40%", "40-50%"],
            "correct": "20-30%",
            "correct_index": 1,
            "explanation": "NCAP launched in 2019 aims to reduce PM2.5 and PM10 concentration by 20-30% by 2025-26 (later revised to 40% reduction by 2026).",
            "syllabus_pointer": "Environment - NCAP",
            "pyq_pattern": "Similar to 2021 Q132, 2024 Q135",
        },
        {
            "q_id": 41,
            "subject": "Environment",
            "topic": "International Agreements",
            "subtopic": "CBD and Nagoya Protocol",
            "type": "factual",
            "difficulty": "hard",
            "question": "The Nagoya Protocol on Access and Benefit Sharing is a supplementary agreement to:",
            "options": ["Paris Agreement", "Convention on Biological Diversity (CBD)", "CITES", "Ramsar Convention"],
            "correct": "Convention on Biological Diversity (CBD)",
            "correct_index": 1,
            "explanation": "The Nagoya Protocol is a supplementary agreement to the Convention on Biological Diversity (CBD). It provides a legal framework for fair sharing of benefits from genetic resources.",
            "syllabus_pointer": "Environment - Nagoya Protocol",
            "pyq_pattern": "Similar to 2019 Q135, 2023 Q138",
        },
        {
            "q_id": 42,
            "subject": "Environment",
            "topic": "Ecology",
            "subtopic": "Ecosystem Services",
            "type": "statement_based",
            "difficulty": "medium",
            "question": "Consider the statements about ecosystem services:\n1. Pollination by bees is a supporting service.\n2. Carbon sequestration is a regulating service.\n3. Ecotourism is a cultural service.\nWhich of the statements given above is/are correct?",
            "options": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"],
            "correct": "2 and 3 only",
            "correct_index": 2,
            "explanation": "Statement 1 is incorrect: Pollination is a REGULATING service, not a supporting service. Statement 2 is correct: Carbon sequestration is a regulating service. Statement 3 is correct: Ecotourism is a cultural service.",
            "syllabus_pointer": "Environment - Ecosystem Services",
            "pyq_pattern": "Similar to 2020 Q138, 2022 Q140",
        },
        # === CURRENT AFFAIRS (8 questions) ===
        {
            "q_id": 43,
            "subject": "Current Affairs",
            "topic": "Government Policies",
            "subtopic": "PM Gati Shakti",
            "type": "factual",
            "difficulty": "easy",
            "question": "The 'PM Gati Shakti National Master Plan' aims to:",
            "options": [
                "Provide universal healthcare",
                "Create integrated infrastructure and reduce logistics costs",
                "Promote digital payments",
                "Develop smart cities",
            ],
            "correct": "Create integrated infrastructure and reduce logistics costs",
            "correct_index": 1,
            "explanation": "PM Gati Shakti launched in October 2021 aims to create integrated infrastructure for seamless connectivity and reduce logistics costs from 13-14% to single digits.",
            "syllabus_pointer": "Current Affairs - PM Gati Shakti",
            "pyq_pattern": "Similar to 2022 Q145, 2024 Q142",
        },
        {
            "q_id": 44,
            "subject": "Current Affairs",
            "topic": "International Events",
            "subtopic": "India's Diplomacy",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "India hosted the G20 Summit in 2023 under the theme of:",
            "options": [
                "One Earth, One Family, One Future",
                "Vasudhaiva Kutumbakam",
                "Both A and B are correct",
                "Neither A nor B is correct",
            ],
            "correct": "Both A and B are correct",
            "correct_index": 2,
            "explanation": "India hosted the G20 Summit in New Delhi on September 9-10, 2023 under the theme 'One Earth, One Family, One Future' which is the English translation of 'Vasudhaiva Kutumbakam'.",
            "syllabus_pointer": "Current Affairs - India G20 Presidency",
            "pyq_pattern": "New pattern (2023 current affairs)",
        },
        {
            "q_id": 45,
            "subject": "Current Affairs",
            "topic": "Science & Tech – Recent",
            "subtopic": "Artificial Intelligence",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "India's 'AIRAWAT' platform, making headlines recently, is related to:",
            "options": ["AI computing infrastructure", "Cyber defense", "Satellite communication", "Drone technology"],
            "correct": "AI computing infrastructure",
            "correct_index": 0,
            "explanation": "AIRAWAT is India's AI computing infrastructure, developed by C-DAC under the National AI Mission. It is one of the largest supercomputing platforms for AI workloads in India.",
            "syllabus_pointer": "Current Affairs - India AI Infrastructure",
            "pyq_pattern": "New pattern (2024 current affairs)",
        },
        {
            "q_id": 46,
            "subject": "Current Affairs",
            "topic": "Reports & Indices",
            "subtopic": "Global Indices",
            "type": "factual",
            "difficulty": "easy",
            "question": "India's rank in the Global Innovation Index 2024 released by WIPO is:",
            "options": ["39th", "40th", "44th", "50th"],
            "correct": "39th",
            "correct_index": 0,
            "explanation": "India ranked 39th in the Global Innovation Index 2024. India improved from 81st (2015) to 39th (2024), making it the top innovator among lower-middle-income countries.",
            "syllabus_pointer": "Current Affairs - Global Innovation Index",
            "pyq_pattern": "Similar to 2023 Q148, 2024 Q145",
        },
        {
            "q_id": 47,
            "subject": "Current Affairs",
            "topic": "Defence & Security",
            "subtopic": "Indigenous Defence",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "The 'INS Vikrant', India's first indigenously built aircraft carrier, was commissioned in:",
            "options": ["2020", "2021", "2022", "2023"],
            "correct": "2022",
            "correct_index": 2,
            "explanation": "INS Vikrant (IAC-1) was commissioned on September 2, 2022. Built at Cochin Shipyard Limited, it is India's largest and most complex warship.",
            "syllabus_pointer": "Current Affairs - INS Vikrant",
            "pyq_pattern": "New pattern (2022 current affairs)",
        },
        {
            "q_id": 48,
            "subject": "Current Affairs",
            "topic": "Government Schemes",
            "subtopic": "Education Reforms",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "The 'PM SHRI Schools' scheme aims to upgrade how many schools across India?",
            "options": ["1,000 schools", "14,500 schools", "1,00,000 schools", "5,000 schools"],
            "correct": "14,500 schools",
            "correct_index": 1,
            "explanation": "PM SHRI scheme launched in 2022 aims to upgrade 14,500 schools across India to showcase the implementation of NEP 2020.",
            "syllabus_pointer": "Current Affairs - PM SHRI Schools",
            "pyq_pattern": "New pattern (2022 current affairs)",
        },
        {
            "q_id": 49,
            "subject": "Current Affairs",
            "topic": "International Events",
            "subtopic": "Climate Action",
            "type": "current_affairs",
            "difficulty": "medium",
            "question": "India's updated NDC under Paris Agreement includes reducing emissions intensity of GDP by what percentage by 2030?",
            "options": ["33-35%", "40-42%", "45%", "50%"],
            "correct": "45%",
            "correct_index": 2,
            "explanation": "India's updated NDC (August 2022) enhanced targets: reduce emissions intensity of GDP by 45% by 2030, achieve 50% non-fossil fuel capacity by 2030, and create additional carbon sink of 2.5-3 billion tonnes.",
            "syllabus_pointer": "Current Affairs - India Updated NDC",
            "pyq_pattern": "New pattern (2022 current affairs)",
        },
        {
            "q_id": 50,
            "subject": "Current Affairs",
            "topic": "Awards & Honours",
            "subtopic": "International Awards",
            "type": "current_affairs",
            "difficulty": "easy",
            "question": "The 2024 Nobel Prize in Economics was awarded to:",
            "options": [
                "Abhijit Banerjee, Esther Duflo, Michael Kremer",
                "Daron Acemoglu, Simon Johnson, James A. Robinson",
                "Paul Romer, William Nordhaus",
                "Amartya Sen",
            ],
            "correct": "Daron Acemoglu, Simon Johnson, James A. Robinson",
            "correct_index": 1,
            "explanation": "The 2024 Nobel Prize in Economics was awarded to Daron Acemoglu, Simon Johnson, and James A. Robinson for their studies of how institutions are formed and affect prosperity.",
            "syllabus_pointer": "Current Affairs - 2024 Nobel Economics",
            "pyq_pattern": "New pattern (2024 current affairs)",
        },
    ]

    return questions


def generate_mock_responses():
    """
    Generate mock student responses with realistic mistake patterns.
    Simulates a student who:
    - Is strong in History and Current Affairs
    - Is weak in Polity (especially Fundamental Rights and Centre-State relations)
    - Is weak in Economy (especially Banking and Fiscal Policy)
    - Makes common confusion errors (similar concepts, temporal errors)
    - Guesses on some hard questions
    """

    question_bank = create_question_bank()

    # Helper to find correct index
    def get_correct_idx(q_id):
        for q in question_bank:
            if q["q_id"] == q_id:
                return q["correct_index"]
        return None

    # Define mistake patterns for the mock student
    responses = {}

    # === POLITY (8 questions) - WEAK ===
    # Q1: Fundamental Rights - WRONG (partial knowledge)
    correct = get_correct_idx(1)
    wrong = 3 if correct != 3 else 2
    responses[1] = {"selected": wrong, "time_spent": 45, "confidence": 2, "mistake_type": "partial_knowledge", "explanation": "Confused statement 3 about Article 16"}

    # Q2: Money Bill - CORRECT
    correct = get_correct_idx(2)
    responses[2] = {"selected": correct, "time_spent": 20, "confidence": 3, "mistake_type": None}

    # Q3: President's Rule - WRONG (conceptual gap)
    correct = get_correct_idx(3)
    wrong = 0 if correct != 0 else 2
    responses[3] = {"selected": wrong, "time_spent": 60, "confidence": 2, "mistake_type": "conceptual_gap", "explanation": "Didn't know about Bommai case"}

    # Q4: Election Commission - CORRECT
    correct = get_correct_idx(4)
    responses[4] = {"selected": correct, "time_spent": 15, "confidence": 3, "mistake_type": None}

    # Q5: Right to Freedom of Religion - WRONG (confusion)
    correct = get_correct_idx(5)
    wrong = 2 if correct != 2 else 1
    responses[5] = {"selected": wrong, "time_spent": 50, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused Article 25 with Article 19 restrictions"}

    # Q6: Supreme Court Jurisdiction - WRONG (confusion)
    correct = get_correct_idx(6)
    wrong = 1 if correct != 1 else 3
    responses[6] = {"selected": wrong, "time_spent": 70, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused Appellate Jurisdiction articles"}

    # Q7: 73rd Amendment - CORRECT
    correct = get_correct_idx(7)
    responses[7] = {"selected": correct, "time_spent": 18, "confidence": 3, "mistake_type": None}

    # Q8: Fundamental Duties - WRONG (partial knowledge)
    correct = get_correct_idx(8)
    wrong = 1 if correct != 1 else 0
    responses[8] = {"selected": wrong, "time_spent": 30, "confidence": 2, "mistake_type": "partial_knowledge", "explanation": "Confused legal obligation with Fundamental Duty"}

    # === HISTORY (7 questions) - STRONG ===
    for q_id in [9, 10, 11, 13, 14, 15]:
        correct = get_correct_idx(q_id)
        responses[q_id] = {"selected": correct, "time_spent": 25, "confidence": 3, "mistake_type": None}

    # Q12: Social Reformers - WRONG (confusion)
    correct = get_correct_idx(12)
    wrong = 3 if correct != 3 else 2
    responses[12] = {"selected": wrong, "time_spent": 45, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused Vivenananda with Dayanand Saraswati"}

    # === GEOGRAPHY (8 questions) - AVERAGE ===
    for q_id in [16, 19, 20, 22]:
        correct = get_correct_idx(q_id)
        responses[q_id] = {"selected": correct, "time_spent": 35, "confidence": 3, "mistake_type": None}

    # Q17: Amarkantak Rivers - WRONG (confusion)
    correct = get_correct_idx(17)
    wrong = 1 if correct != 1 else 3
    responses[17] = {"selected": wrong, "time_spent": 40, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused Mahanadi origin"}

    # Q18: Koeppen Climate - WRONG (misinterpretation)
    correct = get_correct_idx(18)
    wrong = 0 if correct != 0 else 3
    responses[18] = {"selected": wrong, "time_spent": 55, "confidence": 2, "mistake_type": "misinterpretation", "explanation": "Misinterpreted Aw climate"}

    # Q21: Coral Triangle - WRONG (guesswork)
    correct = get_correct_idx(21)
    wrong = 0 if correct != 0 else 1
    responses[21] = {"selected": wrong, "time_spent": 25, "confidence": 1, "mistake_type": "guesswork", "explanation": "Guessed - confused with Caribbean"}

    # Q23: Humboldt Current - WRONG (confusion)
    correct = get_correct_idx(23)
    wrong = 2 if correct != 2 else 3
    responses[23] = {"selected": wrong, "time_spent": 40, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused with warm current"}

    # === ECONOMY (7 questions) - WEAK ===
    # Q24: RBI Monetary Policy - WRONG (confusion)
    correct = get_correct_idx(24)
    wrong = 0 if correct != 0 else 2
    responses[24] = {"selected": wrong, "time_spent": 50, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused Bank Rate with qualitative tool"}

    # Q25: Fiscal Deficits - WRONG (partial knowledge)
    correct = get_correct_idx(25)
    wrong = 0 if correct != 0 else 1
    responses[25] = {"selected": wrong, "time_spent": 65, "confidence": 2, "mistake_type": "partial_knowledge", "explanation": "Didn't know Effective Revenue Deficit"}

    # Q26: GST - CORRECT
    correct = get_correct_idx(26)
    responses[26] = {"selected": correct, "time_spent": 20, "confidence": 3, "mistake_type": None}

    # Q27: SEBI - CORRECT
    correct = get_correct_idx(27)
    responses[27] = {"selected": correct, "time_spent": 25, "confidence": 3, "mistake_type": None}

    # Q28: DBT - WRONG (partial knowledge)
    correct = get_correct_idx(28)
    wrong = 0 if correct != 0 else 1
    responses[28] = {"selected": wrong, "time_spent": 30, "confidence": 2, "mistake_type": "partial_knowledge", "explanation": "Thought DBT was only cash transfers"}

    # Q29: Balance of Payments - WRONG (confusion)
    correct = get_correct_idx(29)
    wrong = 0 if correct != 0 else 2
    responses[29] = {"selected": wrong, "time_spent": 45, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused FDI with current account item"}

    # Q30: Poverty Estimation - WRONG (factual error)
    correct = get_correct_idx(30)
    wrong = 1 if correct != 1 else 0
    responses[30] = {"selected": wrong, "time_spent": 35, "confidence": 2, "mistake_type": "factual_error", "explanation": "Didn't know official estimation stopped"}

    # === SCIENCE (6 questions) - AVERAGE ===
    for q_id in [31, 32, 33, 35]:
        correct = get_correct_idx(q_id)
        responses[q_id] = {"selected": correct, "time_spent": 20, "confidence": 3, "mistake_type": None}

    # Q34: Antibodies - WRONG (confusion)
    correct = get_correct_idx(34)
    wrong = 3 if correct != 3 else 1
    responses[34] = {"selected": wrong, "time_spent": 35, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused T-cells with B-cells"}

    # Q36: Green Chemistry - WRONG (guesswork)
    correct = get_correct_idx(36)
    wrong = 2 if correct != 2 else 3
    responses[36] = {"selected": wrong, "time_spent": 30, "confidence": 1, "mistake_type": "guesswork", "explanation": "Guessed - didn't know the names"}

    # === ENVIRONMENT (6 questions) - AVERAGE ===
    # Q38: Paris Agreement - CORRECT
    correct = get_correct_idx(38)
    responses[38] = {"selected": correct, "time_spent": 40, "confidence": 3, "mistake_type": None}

    # Q39: Project Tiger - CORRECT
    correct = get_correct_idx(39)
    responses[39] = {"selected": correct, "time_spent": 15, "confidence": 3, "mistake_type": None}

    # Q42: Ecosystem Services - CORRECT
    correct = get_correct_idx(42)
    responses[42] = {"selected": correct, "time_spent": 45, "confidence": 3, "mistake_type": None}

    # Q37: Biodiversity Hotspots - WRONG (confusion)
    correct = get_correct_idx(37)
    wrong = 2 if correct != 2 else 1
    responses[37] = {"selected": wrong, "time_spent": 35, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused Sundarbans with hotspot"}

    # Q40: NCAP - WRONG (partial knowledge)
    correct = get_correct_idx(40)
    wrong = 2 if correct != 2 else 1
    responses[40] = {"selected": wrong, "time_spent": 30, "confidence": 2, "mistake_type": "partial_knowledge", "explanation": "Didn't know exact NCAP target"}

    # Q41: Nagoya Protocol - WRONG (confusion)
    correct = get_correct_idx(41)
    wrong = 0 if correct != 0 else 2
    responses[41] = {"selected": wrong, "time_spent": 35, "confidence": 2, "mistake_type": "confusion_similar", "explanation": "Confused with Paris Agreement"}

    # === CURRENT AFFAIRS (8 questions) - STRONG ===
    for q_id in [43, 44, 46, 47, 49, 50]:
        correct = get_correct_idx(q_id)
        responses[q_id] = {"selected": correct, "time_spent": 20, "confidence": 3, "mistake_type": None}

    # Q45: AIRAWAT - WRONG (guesswork)
    correct = get_correct_idx(45)
    wrong = 1 if correct != 1 else 0
    responses[45] = {"selected": wrong, "time_spent": 25, "confidence": 1, "mistake_type": "guesswork", "explanation": "Guessed - confused with cyber defense"}

    # Q48: PM SHRI Schools - WRONG (partial knowledge)
    correct = get_correct_idx(48)
    wrong = 3 if correct != 3 else 0
    responses[48] = {"selected": wrong, "time_spent": 25, "confidence": 2, "mistake_type": "partial_knowledge", "explanation": "Didn't know exact number"}

    return responses


def create_student_profile():
    """Create a mock student profile."""
    return {
        "student_id": "STU001",
        "name": "Aishwarya Rao",
        "batch": "UPSC Prelims 2026 Test Series",
        "target_exam": "UPSC CSE Prelims 2026",
        "registration_date": "2026-01-15",
        "preparation_level": "intermediate",
        "previous_test_scores": [
            {"test_id": "T001", "score": 62, "max_score": 100, "date": "2026-09-15"},
            {"test_id": "T002", "score": 58, "max_score": 100, "date": "2026-09-22"},
            {"test_id": "T003", "score": 65, "max_score": 100, "date": "2026-09-29"},
        ],
        "background": "Engineering graduate, working professional",
        "study_hours_per_day": 4,
    }


def analyze_test_responses(question_bank, responses, student_profile):
    """Analyze test responses and generate mistake patterns."""

    analysis = {
        "student_id": student_profile["student_id"],
        "student_name": student_profile["name"],
        "test_id": "T004",
        "test_date": datetime.now().strftime("%Y-%m-%d"),
        "total_questions": len(question_bank),
        "total_correct": 0,
        "total_wrong": 0,
        "total_skipped": 0,
        "total_marks_obtained": 0,
        "total_marks_lost": 0,
        "overall_score": 0,
        "subject_wise_analysis": {},
        "mistake_cards": [],
        "pattern_summary": {},
        "focus_areas": [],
        "strength_areas": [],
        "recommendations": [],
    }

    # Subject-wise aggregation
    subject_stats = {}

    for q in question_bank:
        q_id = q["q_id"]
        subject = q["subject"]

        if subject not in subject_stats:
            subject_stats[subject] = {"total": 0, "correct": 0, "wrong": 0, "marks_lost": 0, "mistakes": []}

        subject_stats[subject]["total"] += 1

        resp = responses.get(q_id, {})
        is_correct = resp.get("selected") == q["correct_index"]

        if is_correct:
            subject_stats[subject]["correct"] += 1
            analysis["total_correct"] += 1
            analysis["total_marks_obtained"] += 2
        else:
            subject_stats[subject]["wrong"] += 1
            analysis["total_wrong"] += 1
            analysis["total_marks_lost"] += 2.67

            mistake_card = {
                "q_id": q_id,
                "subject": subject,
                "topic": q["topic"],
                "subtopic": q["subtopic"],
                "question_type": q["type"],
                "difficulty": q["difficulty"],
                "correct_answer": q["correct"],
                "student_answer": q["options"][resp.get("selected", 0)] if resp.get("selected") is not None else "Not answered",
                "explanation": q["explanation"],
                "student_mistake_reason": resp.get("explanation", "Not specified"),
                "mistake_type": resp.get("mistake_type", "unknown"),
                "confidence": resp.get("confidence", 0),
                "time_spent": resp.get("time_spent", 0),
                "severity": calculate_severity(q, resp),
                "syllabus_pointer": q["syllabus_pointer"],
                "pyq_pattern": q["pyq_pattern"],
            }
            analysis["mistake_cards"].append(mistake_card)
            subject_stats[subject]["mistakes"].append(mistake_card)

    analysis["overall_score"] = analysis["total_marks_obtained"]

    # Subject-wise analysis
    for subject, stats in subject_stats.items():
        accuracy = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        analysis["subject_wise_analysis"][subject] = {
            "total_questions": stats["total"],
            "correct": stats["correct"],
            "wrong": stats["wrong"],
            "accuracy": round(accuracy, 1),
            "marks_lost": round(stats["marks_lost"], 2),
            "mistake_count": len(stats["mistakes"]),
            "status": "strong" if accuracy >= 70 else "average" if accuracy >= 50 else "weak",
        }

    # Pattern summary
    mistake_type_counts = {}
    for card in analysis["mistake_cards"]:
        mtype = card["mistake_type"]
        mistake_type_counts[mtype] = mistake_type_counts.get(mtype, 0) + 1

    analysis["pattern_summary"] = {
        "total_mistakes": analysis["total_wrong"],
        "mistake_type_distribution": mistake_type_counts,
        "most_common_mistake_type": max(mistake_type_counts, key=mistake_type_counts.get) if mistake_type_counts else None,
        "average_time_per_mistake": (
            sum(c["time_spent"] for c in analysis["mistake_cards"]) / len(analysis["mistake_cards"])
            if analysis["mistake_cards"]
            else 0
        ),
    }

    # Focus areas
    for subject, stats in analysis["subject_wise_analysis"].items():
        if stats["accuracy"] < 60:
            analysis["focus_areas"].append(
                {
                    "subject": subject,
                    "accuracy": stats["accuracy"],
                    "priority": "HIGH" if stats["accuracy"] < 50 else "MEDIUM",
                    "topics_to_improve": get_weak_topics(subject_stats[subject]["mistakes"]),
                }
            )
        elif stats["accuracy"] >= 80:
            analysis["strength_areas"].append(
                {"subject": subject, "accuracy": stats["accuracy"], "recommendation": "Maintain consistency, focus on advanced questions"}
            )

    analysis["recommendations"] = generate_recommendations(analysis)
    return analysis


def calculate_severity(question, response):
    severity = "LOW"
    if question["difficulty"] == "hard":
        severity = "MEDIUM"
    if response.get("confidence", 0) >= 3:
        severity = "HIGH"
    if response.get("mistake_type") in ["conceptual_gap", "factual_error", "confusion_similar"]:
        severity = "HIGH"
    if response.get("time_spent", 0) < 20:
        severity = "LOW"
    return severity


def get_weak_topics(mistakes):
    topics = {}
    for m in mistakes:
        key = f"{m['topic']} - {m['subtopic']}"
        if key not in topics:
            topics[key] = {"count": 0, "questions": []}
        topics[key]["count"] += 1
        topics[key]["questions"].append(m["q_id"])
    sorted_topics = sorted(topics.items(), key=lambda x: x[1]["count"], reverse=True)
    return [{"topic": t[0], "mistake_count": t[1]["count"], "questions": t[1]["questions"]} for t in sorted_topics[:5]]


def generate_recommendations(analysis):
    recommendations = []

    for area in analysis["focus_areas"]:
        recommendations.append(
            {
                "priority": area["priority"],
                "category": "Subject Focus",
                "subject": area["subject"],
                "message": f"Focus on {area['subject']} - accuracy is {area['accuracy']}%. Recommended: Revise NCERT basics and solve 50+ PYQs on weak topics.",
                "action_items": [
                    f"Complete NCERT {area['subject']} fundamentals",
                    f"Solve 30 PYQs on {', '.join([t['topic'] for t in area['topics_to_improve'][:3]])}",
                    f"Take 2 sectional tests on {area['subject']}",
                ],
                "resources": get_subject_resources(area["subject"]),
            }
        )

    if analysis["pattern_summary"]["most_common_mistake_type"]:
        common_mistake = analysis["pattern_summary"]["most_common_mistake_type"]
        recommendations.append(
            {
                "priority": "HIGH",
                "category": "Mistake Pattern",
                "message": f"Your most common mistake type is '{common_mistake}'. This indicates a specific weakness that needs targeted intervention.",
                "action_items": get_mistake_type_remediation(common_mistake),
                "resources": [],
            }
        )

    avg_time = analysis["pattern_summary"]["average_time_per_mistake"]
    if avg_time > 45:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "category": "Time Management",
                "message": f"Average time spent on wrong answers: {avg_time:.0f} seconds. Practice timed tests to improve speed.",
                "action_items": [
                    "Take 5 sectional tests with strict 20-min time limit",
                    "Practice elimination techniques for faster decision making",
                    "Focus on high-weightage topics first",
                ],
                "resources": [],
            }
        )

    for area in analysis["strength_areas"]:
        recommendations.append(
            {
                "priority": "LOW",
                "category": "Strength Maintenance",
                "subject": area["subject"],
                "message": f"Maintain your strong performance in {area['subject']} ({area['accuracy']}% accuracy).",
                "action_items": [
                    f"Solve advanced PYQs on {area['subject']}",
                    f"Link static topics with current affairs",
                    f"Take 1 sectional test per week on {area['subject']}",
                ],
                "resources": [],
            }
        )

    return recommendations


def get_subject_resources(subject):
    resources = {
        "Polity": ["NCERT Class 11: Indian Constitution at Work", "M. Laxmikanth - Indian Polity", "Previous Year Questions (2013-2025)"],
        "History": ["NCERT Class 12: Themes in Indian History", "Spectrum - A Brief History of Modern India", "Nitin Singhania - Indian Art & Culture"],
        "Geography": ["NCERT Class 11 & 12: Physical Geography, India: Physical Environment", "GC Leong - Certificate Physical and Human Geography", "Majid Hussain - Physical Geography"],
        "Economy": ["NCERT Class 11 & 12: Indian Economic Development, Macroeconomics", "Ramesh Singh - Indian Economy", "Budget and Economic Survey summaries"],
        "Science": ["NCERT Class 6-10: Science textbooks", "Science Reporter magazine", "Current affairs on science and technology"],
        "Environment": ["NCERT Class 12: Biology (Chapters on Ecology)", "Shankar IAS Environment", "Down to Earth magazine"],
        "Current Affairs": ["The Hindu/Indian Express daily news", "PIB daily updates", "Monthly current affairs compilation"],
    }
    return resources.get(subject, ["NCERT textbooks", "Previous Year Questions"])


def get_mistake_type_remediation(mistake_type):
    remediation = {
        "conceptual_gap": ["Revise NCERT fundamentals", "Read standard textbook chapters", "Watch explanatory videos", "Solve 10 PYQs with explanations", "Create concept maps"],
        "confusion_similar": ["Create comparison tables for similar concepts", "Practice 20 questions on distinguishing similar concepts", "Use mnemonics to remember differences"],
        "partial_knowledge": ["Complete full chapter reading", "Take notes while studying", "Revise after 1 week", "Solve topic-wise PYQs"],
        "factual_error": ["Create flashcards for important facts", "Use spaced repetition", "Practice factual recall questions"],
        "misinterpretation": ["Practice reading questions carefully", "Underline key words", "Eliminate wrong options first"],
        "guesswork": ["Improve elimination techniques", "Study more to reduce guessing", "Practice 'intelligent elimination' method"],
        "time_pressure": ["Take timed sectional tests", "Practice with a timer daily", "Learn to skip difficult questions initially"],
    }
    return remediation.get(mistake_type, ["Review the topic", "Practice more questions"])


def generate_json_report(analysis, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    return output_path


def generate_latex_pdf(analysis, question_bank, student_profile, output_path):
    """Generate a professional PDF analysis report using LaTeX."""
    
    # Color names
    brandblue = "brandblue"
    wrongred = "wrongred"
    correctgreen = "correctgreen"
    brandgold = "brandgold"

    def acolor(acc):
        if acc >= 70:
            return correctgreen
        elif acc < 50:
            return wrongred
        else:
            return brandgold

    def esc(s):
        return str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

    # Build document as list of lines
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
    L.append(r"\definecolor{darktext}{RGB}{33,33,33}")
    L.append(r"\hypersetup{colorlinks=true,linkcolor=brandblue,urlcolor=brandblue}")
    L.append(r"\pagestyle{fancy}")
    L.append(r"\fancyhf{}")
    L.append(r"\fancyhead[L]{\textcolor{brandblue}{\textbf{Approach KAS}}}")
    L.append(r"\fancyhead[R]{\textcolor{brandblue}{\textbf{UPSC Prelims Test Analysis}}}")
    L.append(r"\fancyfoot[L]{\textcolor{gray}{\small kas.approachestoias.com}}")
    L.append(r"\fancyfoot[R]{\textcolor{gray}{\small @ApproachKAS}}")
    L.append(r"\titleformat{\section}{\Large\bfseries\color{brandblue}}{}{0em}{}[\titlerule]")
    L.append(r"\titleformat{\subsection}{\large\bfseries\color{darktext}}{}{0em}{}")
    L.append(r"\begin{document}")
    L.append(r"\begin{center}")
    L.append(r"\vspace*{1cm}")
    L.append(r"{\Huge\bfseries\color{brandblue} UPSC PRELIMS TEST ANALYSIS}\\[0.5cm]")
    L.append(r"{\Large\color{darktext} Personalized Performance Report}\\[1cm]")
    L.append(r"\end{center}")
    L.append(r"\vspace{1cm}")
    L.append(r"\begin{center}")
    L.append(r"\fbox{\begin{minipage}{0.9\textwidth}")
    L.append(r"\centering")
    L.append(r"\textbf{Student:} " + esc(student_profile["name"]) + r" \\")
    L.append(r"\textbf{Test ID:} " + analysis["test_id"] + r" \\")
    L.append(r"\textbf{Date:} " + analysis["test_date"] + r" \\")
    L.append(r"\textbf{Target Exam:} " + esc(student_profile["target_exam"]))
    L.append(r"\end{minipage}}")
    L.append(r"\end{center}")
    L.append(r"\vspace{1cm}")
    L.append(r"\section{Executive Summary}")
    L.append(r"\begin{center}")
    L.append(r"\begin{tabular}{|c|c|c|c|}")
    L.append(r"\hline")
    L.append(r"\textbf{Total Questions} & \textbf{Correct} & \textbf{Wrong} & \textbf{Score} \\")
    L.append(r"\hline")
    L.append(str(analysis["total_questions"]) + " & " + str(analysis["total_correct"]) + " & " + str(analysis["total_wrong"]) + r" & \textcolor{brandblue}{\textbf{" + str(analysis["overall_score"]) + r"}} \\")
    L.append(r"\hline")
    L.append(r"\end{tabular}")
    L.append(r"\end{center}")
    L.append(r"\vspace{0.5cm}")
    L.append(r"\section{Subject-wise Performance}")
    L.append(r"\begin{longtable}{|l|c|c|c|c|}")
    L.append(r"\hline")
    L.append(r"\textbf{Subject} & \textbf{Total} & \textbf{Correct} & \textbf{Wrong} & \textbf{Accuracy} \\")
    L.append(r"\hline")
    L.append(r"\endfirsthead")
    L.append(r"\hline")
    L.append(r"\textbf{Subject} & \textbf{Total} & \textbf{Correct} & \textbf{Wrong} & \textbf{Accuracy} \\")
    L.append(r"\hline")
    L.append(r"\endhead")

    for subject, stats in analysis["subject_wise_analysis"].items():
        color = acolor(stats["accuracy"])
        L.append(esc(subject) + " & " + str(stats["total_questions"]) + " & " + str(stats["correct"]) + " & " + str(stats["wrong"]) + r" & \textcolor{" + color + "}{" + str(stats["accuracy"]) + r"\%} \\")
        L.append(r"\hline")

    L.append(r"\end{longtable}")
    L.append(r"\vspace{0.5cm}")
    L.append(r"\section{Mistake Pattern Analysis}")
    L.append(r"\begin{center}")
    L.append(r"\begin{tabular}{|l|c|}")
    L.append(r"\hline")
    L.append(r"\textbf{Mistake Type} & \textbf{Count} \\")
    L.append(r"\hline")

    for mtype, count in analysis["pattern_summary"]["mistake_type_distribution"].items():
        L.append(esc(mtype.replace("_", " ").title()) + " & " + str(count) + r" \\")
        L.append(r"\hline")

    L.append(r"\end{tabular}")
    L.append(r"\end{center}")
    L.append(r"\section{Focus Areas (Weak Subjects)}")

    for area in analysis["focus_areas"]:
        L.append(r"\textbf{" + esc(area["subject"]) + " (Accuracy: " + str(area["accuracy"]) + r"\%):}\\newline")
        L.append(r"\textbf{Priority:} \textcolor{" + acolor(area["accuracy"]) + "}{" + area["priority"] + r"}\\newline")
        L.append(r"\textbf{Topics to Improve:}\newline")
        L.append(r"\begin{itemize}")
        for topic in area["topics_to_improve"][:3]:
            L.append(r"\item " + esc(topic["topic"]) + " (" + str(topic["mistake_count"]) + " mistakes)")
        L.append(r"\end{itemize}")

    if analysis["strength_areas"]:
        L.append(r"\section{Strength Areas}")
        for area in analysis["strength_areas"]:
            L.append(r"\textbf{" + esc(area["subject"]) + "}: " + str(area["accuracy"]) + r"\% accuracy - " + esc(area["recommendation"]) + r"\\newline")

    L.append(r"\section{Personalized Recommendations}")

    for i, rec in enumerate(analysis["recommendations"], 1):
        rcolor = acolor(50) if rec["priority"] == "HIGH" else acolor(65) if rec["priority"] == "MEDIUM" else acolor(80)
        L.append(r"\subsection{Recommendation " + str(i) + ": " + esc(rec["category"]) + "}")
        L.append(r"\textbf{Priority:} \textcolor{" + rcolor + "}{" + rec["priority"] + r"}\\newline")
        L.append(esc(rec["message"]) + r"\\newline")
        L.append(r"\textbf{Action Items:}\newline")
        L.append(r"\begin{enumerate}")
        for item in rec["action_items"]:
            L.append(r"\item " + esc(item))
        L.append(r"\end{enumerate}")

    L.append(r"\section{Detailed Mistake Analysis}")

    for card in analysis["mistake_cards"]:
        L.append(r"\subsubsection{Question " + str(card["q_id"]) + ": " + esc(card["subject"]) + "}")
        L.append(r"\textbf{Topic:} " + esc(card["topic"]) + " - " + esc(card["subtopic"]) + r"\\newline")
        L.append(r"\textbf{Correct Answer:} " + esc(card["correct_answer"]) + r"\\newline")
        L.append(r"\textbf{Your Answer:} \textcolor{wrongred}{" + esc(card["student_answer"]) + r"}\\newline")
        L.append(r"\textbf{Mistake Type:} " + esc(card["mistake_type"]) + r"\\newline")
        L.append(r"\textbf{Explanation:} " + esc(card["explanation"]) + r"\\newline")
        L.append(r"\vspace{0.5cm}")

    L.append(r"\end{document}")

    tex_path = output_path.replace(".pdf", ".tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    return tex_path


def main():
    print("=" * 60)
    print("UPSC PRELIMS TEST ANALYSIS ENGINE (Laya-Adapted)")
    print("=" * 60)

    print("\n[1/5] Creating question bank...")
    question_bank = create_question_bank()
    print(f"  Created {len(question_bank)} questions across 7 subjects")

    print("\n[2/5] Generating mock student responses...")
    responses = generate_mock_responses()
    print(f"  Generated {len(responses)} responses with realistic mistake patterns")

    print("\n[3/5] Creating student profile...")
    student_profile = create_student_profile()
    print(f"  Student: {student_profile['name']} ({student_profile['student_id']})")

    print("\n[4/5] Analyzing test responses...")
    analysis = analyze_test_responses(question_bank, responses, student_profile)
    print(f"  Analysis complete!")
    print(f"  Score: {analysis['overall_score']}/200")
    print(f"  Correct: {analysis['total_correct']}, Wrong: {analysis['total_wrong']}")

    print("\n[5/5] Generating reports...")

    qb_path = DATA_DIR / "question_bank.json"
    with open(qb_path, "w", encoding="utf-8") as f:
        json.dump(question_bank, f, indent=2, ensure_ascii=False)
    print(f"  Question bank saved: {qb_path}")

    resp_path = DATA_DIR / "student_responses.json"
    with open(resp_path, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    print(f"  Responses saved: {resp_path}")

    json_path = OUTPUT_DIR / "analysis_report.json"
    generate_json_report(analysis, json_path)
    print(f"  JSON report saved: {json_path}")

    tex_path = OUTPUT_DIR / "analysis_report.tex"
    generate_latex_pdf(analysis, question_bank, student_profile, str(tex_path))
    print(f"  LaTeX report saved: {tex_path}")

    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nStudent: {student_profile['name']}")
    print(f"Test Score: {analysis['overall_score']}/200")
    print(f"Accuracy: {(analysis['total_correct']/analysis['total_questions'])*100:.1f}%")

    print("\nSubject Performance:")
    for subject, stats in analysis["subject_wise_analysis"].items():
        status_icon = "✓" if stats["status"] == "strong" else "✗" if stats["status"] == "weak" else "~"
        print(f"  {status_icon} {subject}: {stats['accuracy']}% ({stats['status']})")

    print("\nTop Mistake Patterns:")
    for mtype, count in sorted(analysis["pattern_summary"]["mistake_type_distribution"].items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"  • {mtype.replace('_', ' ').title()}: {count} times")

    print("\nFocus Areas:")
    for area in analysis["focus_areas"]:
        print(f"  🔴 {area['subject']}: {area['accuracy']}% accuracy - Priority: {area['priority']}")

    print("\n" + "=" * 60)
    print(f"All outputs saved to: {OUTPUT_DIR}")
    print("=" * 60)

    return analysis


if __name__ == "__main__":
    analysis = main()
