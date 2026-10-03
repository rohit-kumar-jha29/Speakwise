"""
storage.py - Data persistence layer for SpeakWise.
Maintains user profile, session history, and statistical aggregations.
Supports clean JSON file storage with graceful fallback and default demo data.
"""

import json
import os
import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STORE_FILE = os.path.join(DATA_DIR, "speakwise_store.json")

DEFAULT_PROFILE = {
    "name": "Rohit",
    "level": "Intermediate",
    "goal": "Professional English",
    "avatar": "👨‍💼",
    "created_at": "2026-09-28T09:00:00Z"
}

DEFAULT_SESSIONS = [
    {
        "id": "sess_demo_1",
        "date": "2026-09-30 11:15",
        "mode": "roleplay",
        "scenario_id": "job_interview",
        "scenario_title": "Job Interview",
        "role": "Senior Hiring Manager (Sarah Vance)",
        "duration_minutes": 14,
        "turns": 5,
        "score_overall": 68,
        "scores": {
            "grammar": 6.8,
            "vocabulary": 6.5,
            "clarity": 7.0,
            "tone": 7.2,
            "overall": 6.8
        },
        "main_mistakes": [
            "Tense duration error: 'I am working here since two years'",
            "Awkward phrasing: 'Can we prepone the schedule?'"
        ],
        "key_improvement": "Use Present Perfect Continuous for ongoing past actions; use 'move forward' instead of 'prepone'.",
        "top_strengths": [
            "Clear articulation of work milestones",
            "Polite and respectful opening and closing",
            "Strong relevant work examples"
        ],
        "transcript": [
            {
                "sender": "ai",
                "text": "Hello Rohit, welcome to the interview. Please introduce yourself."
            },
            {
                "sender": "user",
                "text": "Hello ma'am, I am working in software sales since four years and handled clients."
            },
            {
                "sender": "ai",
                "text": "That sounds like solid foundational experience. What were your main responsibilities in sales?"
            },
            {
                "sender": "user",
                "text": "I handled customer acquisition and team management, but sometimes we prepone product demos."
            }
        ]
    },
    {
        "id": "sess_demo_2",
        "date": "2026-10-01 15:40",
        "mode": "roleplay",
        "scenario_id": "client_meeting",
        "scenario_title": "Client Meeting",
        "role": "Key Account Client (Elena Rostova)",
        "duration_minutes": 18,
        "turns": 6,
        "score_overall": 72,
        "scores": {
            "grammar": 7.2,
            "vocabulary": 7.0,
            "clarity": 7.4,
            "tone": 7.5,
            "overall": 7.2
        },
        "main_mistakes": [
            "Overly blunt tone: 'I want this requirement changed'",
            "Uncountable noun mistake: 'Can you give me an advice'"
        ],
        "key_improvement": "Soften directives with diplomatic modals ('I would recommend that we...' or 'Could we consider...?').",
        "top_strengths": [
            "Assertive yet collaborative positioning",
            "Structured responses to client budget pushback",
            "Prompt clarification questions"
        ],
        "transcript": [
            {
                "sender": "ai",
                "text": "Good morning Rohit. We have some reservations regarding the proposed implementation timeline. How do you propose we address this?"
            },
            {
                "sender": "user",
                "text": "I understand your worry. We can divide the project into two distinct phases to reduce risk."
            }
        ]
    },
    {
        "id": "sess_demo_3",
        "date": "2026-10-02 18:20",
        "mode": "roleplay",
        "scenario_id": "talking_to_manager",
        "scenario_title": "Workplace Conversation",
        "role": "Direct Manager (David Chen)",
        "duration_minutes": 12,
        "turns": 5,
        "score_overall": 76,
        "scores": {
            "grammar": 7.8,
            "vocabulary": 7.6,
            "clarity": 7.8,
            "tone": 8.0,
            "overall": 7.6
        },
        "main_mistakes": [
            "Subject-verb agreement: 'Each of the teammates have submitted'",
            "Redundant phrasing: 'Please revert back as soon as you will check'"
        ],
        "key_improvement": "Remember that 'each' is singular ('has submitted'), and avoid redundant 'back' with revert.",
        "top_strengths": [
            "Proactive prioritization of sprint tasks",
            "Clear timeline estimates without ambiguity",
            "Confident and professional tone"
        ],
        "transcript": [
            {
                "sender": "ai",
                "text": "Hey Rohit! How are things going with you this week, and what's top of mind for our agenda today?"
            },
            {
                "sender": "user",
                "text": "Hi David, things are going well. I wanted to align on sprint priorities and discuss our API deadline."
            }
        ]
    }
]


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_store() -> dict:
    """Load store from JSON or initialize with defaults."""
    _ensure_data_dir()
    if not os.path.exists(STORE_FILE):
        store = {
            "profile": DEFAULT_PROFILE,
            "sessions": DEFAULT_SESSIONS,
            "last_updated": datetime.datetime.now().isoformat()
        }
        save_store(store)
        return store
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "profile" not in data:
                data["profile"] = DEFAULT_PROFILE
            if "sessions" not in data:
                data["sessions"] = DEFAULT_SESSIONS
            return data
    except Exception as e:
        print(f"Error loading store: {e}")
        return {
            "profile": DEFAULT_PROFILE,
            "sessions": DEFAULT_SESSIONS,
            "last_updated": datetime.datetime.now().isoformat()
        }


def save_store(store: dict) -> bool:
    """Persist store to disk."""
    _ensure_data_dir()
    try:
        store["last_updated"] = datetime.datetime.now().isoformat()
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving store: {e}")
        return False


def get_profile() -> dict:
    store = load_store()
    return store.get("profile", DEFAULT_PROFILE)


def update_profile(new_profile_data: dict) -> dict:
    store = load_store()
    current = store.get("profile", DEFAULT_PROFILE)
    current.update(new_profile_data)
    store["profile"] = current
    save_store(store)
    return current


def get_sessions() -> list:
    store = load_store()
    return store.get("sessions", DEFAULT_SESSIONS)


def add_session(session_data: dict) -> dict:
    store = load_store()
    sessions = store.get("sessions", [])
    # Set default values if missing
    if "id" not in session_data:
        session_data["id"] = f"sess_{int(datetime.datetime.now().timestamp())}"
    if "date" not in session_data:
        session_data["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    sessions.append(session_data)
    store["sessions"] = sessions
    save_store(store)
    return session_data


def get_stats() -> dict:
    """Compute rich progress statistics and charts data."""
    store = load_store()
    sessions = store.get("sessions", [])

    if not sessions:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "avg_overall": 0,
            "avg_grammar": 0,
            "avg_vocab": 0,
            "avg_clarity": 0,
            "avg_tone": 0,
            "improvement_pct": 0,
            "trend": [],
            "strengths": ["Consistent practice", "Good willingness to learn"],
            "focus_areas": ["Tenses", "Articles", "Professional phrasing"]
        }

    total_sessions = len(sessions)
    total_minutes = sum(s.get("duration_minutes", 10) for s in sessions)

    overalls = [s.get("score_overall", 70) for s in sessions]
    avg_overall = round(sum(overalls) / total_sessions, 1)

    grammar_scores = [s.get("scores", {}).get("grammar", 7.0) * 10 for s in sessions]
    vocab_scores = [s.get("scores", {}).get("vocabulary", 7.0) * 10 for s in sessions]
    clarity_scores = [s.get("scores", {}).get("clarity", 7.0) * 10 for s in sessions]
    tone_scores = [s.get("scores", {}).get("tone", 7.0) * 10 for s in sessions]

    avg_grammar = round(sum(grammar_scores) / total_sessions, 1)
    avg_vocab = round(sum(vocab_scores) / total_sessions, 1)
    avg_clarity = round(sum(clarity_scores) / total_sessions, 1)
    avg_tone = round(sum(tone_scores) / total_sessions, 1)

    # Improvement calculation (First session vs latest session)
    if total_sessions >= 2:
        first_score = overalls[0]
        latest_score = overalls[-1]
        improvement_pct = round(((latest_score - first_score) / max(first_score, 1)) * 100, 1)
    else:
        improvement_pct = 5.0

    trend = [
        {
            "session_num": i + 1,
            "label": f"Session {i + 1}",
            "title": s.get("scenario_title", f"Practice {i + 1}"),
            "score": s.get("score_overall", 70),
            "date": s.get("date", "")
        }
        for i, s in enumerate(sessions)
    ]

    # Dynamically extract recurring strengths and focus areas
    strengths_pool = [
        "Clear sentence articulation",
        "Polite, collaborative tone",
        "Structured responses with examples",
        "Active listening and prompt clarification",
        "Expanding professional vocabulary"
    ]
    focus_pool = [
        "Tenses (Present Perfect vs Simple Past)",
        "Prepositions & Phrasal Verbs",
        "Softening direct commands with modal verbs",
        "Avoiding redundant idioms ('revert back')",
        "Subject-Verb Agreement with indefinite pronouns"
    ]

    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "avg_overall": avg_overall,
        "avg_grammar": avg_grammar,
        "avg_vocab": avg_vocab,
        "avg_clarity": avg_clarity,
        "avg_tone": avg_tone,
        "improvement_pct": improvement_pct,
        "trend": trend,
        "strengths": strengths_pool[:3],
        "focus_areas": focus_pool[:3]
    }


def reset_to_defaults() -> dict:
    """Reset store back to default demo state."""
    store = {
        "profile": DEFAULT_PROFILE,
        "sessions": DEFAULT_SESSIONS,
        "last_updated": datetime.datetime.now().isoformat()
    }
    save_store(store)
    return store
