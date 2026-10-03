"""
database.py - SQLite Database Layer for SpeakWise AI.
Maintains persistent tables for users, sessions, messages, feedback, and skill metrics.
Initializes with 12 rich historical sessions matching the user's specification.
"""

import sqlite3
import json
import os
import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "speakwise.db")


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # User Profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        level TEXT NOT NULL,
        goal TEXT NOT NULL,
        avatar TEXT,
        streak_days INTEGER DEFAULT 5,
        total_practice_minutes INTEGER DEFAULT 222,
        created_at TEXT
    )
    """)

    # Practice Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        date TEXT,
        mode TEXT,
        scenario_id TEXT,
        scenario_title TEXT,
        role TEXT,
        duration_minutes INTEGER,
        turns INTEGER,
        score_overall INTEGER,
        grammar_score REAL,
        vocab_score REAL,
        clarity_score REAL,
        tone_score REAL,
        confidence_score REAL,
        main_mistakes TEXT,
        key_improvement TEXT,
        top_strengths TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Messages table (multi-turn history)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        sender TEXT,
        text TEXT,
        timestamp TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions (id)
    )
    """)

    # Feedback cache table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        message_id INTEGER,
        feedback_json TEXT,
        created_at TEXT
    )
    """)

    conn.commit()

    # Seed default user and demo sessions if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_demo_data(cursor)
        conn.commit()

    conn.close()


def seed_demo_data(cursor):
    """Seed initial user Rohit with 12 completed sessions showing steady progress."""
    now = datetime.datetime.now()
    user_id = "user_default"
    cursor.execute("""
    INSERT INTO users (id, name, level, goal, avatar, streak_days, total_practice_minutes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, "Rohit", "Intermediate", "Professional English", "👨‍💼", 5, 222, (now - datetime.timedelta(days=14)).isoformat()))

    # 12 historical sessions spanning past 2 weeks
    # Progress: 62 -> 65 -> 67 -> 69 -> 71 -> 72 -> 74 -> 76 -> 77 -> 78 -> 80 -> 82
    historical_sessions = [
        {"day": 13, "mode": "roleplay", "scen_id": "job_interview", "title": "Job Interview", "role": "Hiring Manager", "dur": 15, "turns": 6, "score": 62, "g": 6.0, "v": 6.2, "c": 6.5, "t": 6.5, "conf": 6.0, "mistake": "Tenses duration ('working since 2 years')", "imp": "Use Present Perfect Continuous ('have been working for')."},
        {"day": 12, "mode": "free_conversation", "scen_id": "free_conversation", "title": "Casual Intro", "role": "AI Coach", "dur": 12, "turns": 5, "score": 65, "g": 6.4, "v": 6.5, "c": 6.8, "t": 6.8, "conf": 6.3, "mistake": "Subject-verb agreement ('he do not')", "imp": "Remember third-person singular 'does not'."},
        {"day": 11, "mode": "roleplay", "scen_id": "client_meeting", "title": "Client Meeting", "role": "Client Director", "dur": 18, "turns": 7, "score": 67, "g": 6.5, "v": 6.8, "c": 7.0, "t": 6.8, "conf": 6.6, "mistake": "Overly direct command ('I want this done')", "imp": "Soften requests with diplomatic modals ('I would appreciate...')."},
        {"day": 10, "mode": "grammar", "scen_id": "grammar_challenge", "title": "Grammar Workout", "role": "AI Coach", "dur": 10, "turns": 8, "score": 69, "g": 7.2, "v": 6.8, "c": 7.0, "t": 7.0, "conf": 6.8, "mistake": "Preposition errors ('discuss about')", "imp": "Use 'discuss' directly without 'about'."},
        {"day": 9, "mode": "roleplay", "scen_id": "manager_conversation", "title": "Manager Conversation", "role": "Team Lead", "dur": 16, "turns": 6, "score": 71, "g": 7.0, "v": 7.2, "c": 7.4, "t": 7.5, "conf": 7.0, "mistake": "Colloquialism ('prepone the meeting')", "imp": "Use 'move forward' or 'reschedule earlier'."},
        {"day": 8, "mode": "roleplay", "scen_id": "team_meeting", "title": "Team Standup", "role": "Scrum Master", "dur": 14, "turns": 5, "score": 72, "g": 7.2, "v": 7.2, "c": 7.5, "t": 7.8, "conf": 7.2, "mistake": "Redundant idiom ('revert back')", "imp": "Say 'revert' or 'get back to you' without 'back'."},
        {"day": 7, "mode": "interview", "scen_id": "interview_hr", "title": "HR Interview", "role": "HR Director", "dur": 22, "turns": 8, "score": 74, "g": 7.4, "v": 7.5, "c": 7.6, "t": 7.8, "conf": 7.4, "mistake": "Uncountable noun ('an advice')", "imp": "Say 'some advice' or 'a piece of advice'."},
        {"day": 6, "mode": "roleplay", "scen_id": "customer_complaint", "title": "Customer Complaint", "role": "Upset Customer", "dur": 20, "turns": 7, "score": 76, "g": 7.5, "v": 7.8, "c": 7.8, "t": 8.2, "conf": 7.5, "mistake": "Defensive tone during escalation", "imp": "Acknowledge feelings first with empathetic phrasing."},
        {"day": 5, "mode": "vocab", "scen_id": "vocab_drill", "title": "Vocabulary Mastery", "role": "AI Coach", "dur": 12, "turns": 6, "score": 77, "g": 7.6, "v": 8.2, "c": 7.9, "t": 8.0, "conf": 7.6, "mistake": "Basic adjectives ('good/bad')", "imp": "Incorporate elevated descriptors ('impactful', 'suboptimal')."},
        {"day": 4, "mode": "roleplay", "scen_id": "sales_call", "title": "Sales Call", "role": "Prospective Buyer", "dur": 18, "turns": 6, "score": 78, "g": 7.6, "v": 8.0, "c": 8.0, "t": 8.4, "conf": 7.8, "mistake": "Run-on explanation", "imp": "Keep value proposition answers to 2 concise sentences."},
        {"day": 2, "mode": "interview", "scen_id": "interview_ba", "title": "Business Analyst Interview", "role": "Lead Architect", "dur": 24, "turns": 8, "score": 80, "g": 7.8, "v": 8.2, "c": 8.2, "t": 8.6, "conf": 8.0, "mistake": "Missing quantified results in STAR response", "imp": "Cite percentage improvements or measurable team outcomes."},
        {"day": 1, "mode": "roleplay", "scen_id": "salary_negotiation", "title": "Salary Negotiation", "role": "Hiring Partner", "dur": 20, "turns": 6, "score": 82, "g": 8.0, "v": 8.4, "c": 8.4, "t": 8.8, "conf": 8.2, "mistake": "Slight hesitation when articulating market value", "imp": "Lead with industry benchmarks and key recent contributions."}
    ]

    for item in historical_sessions:
        sess_id = f"sess_hist_{item['day']}"
        s_date = (now - datetime.timedelta(days=item['day'])).strftime("%d %b %Y %H:%M")
        strengths = json.dumps([
            "Strong contextual ownership",
            "Polite and professional demeanor",
            "Clear articulation of business milestones"
        ])
        mistakes = json.dumps([item["mistake"]])

        cursor.execute("""
        INSERT INTO sessions (
            id, user_id, date, mode, scenario_id, scenario_title, role,
            duration_minutes, turns, score_overall, grammar_score, vocab_score,
            clarity_score, tone_score, confidence_score, main_mistakes,
            key_improvement, top_strengths, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sess_id, user_id, s_date, item["mode"], item["scen_id"], item["title"],
            item["role"], item["dur"], item["turns"], item["score"], item["g"],
            item["v"], item["c"], item["t"], item["conf"], mistakes, item["imp"],
            strengths, (now - datetime.timedelta(days=item['day'])).isoformat()
        ))

        # Sample conversation messages for inspection
        cursor.execute("""
        INSERT INTO messages (session_id, sender, text, timestamp)
        VALUES (?, 'ai', 'Welcome to this session. Let us begin our communication practice.', ?)
        """, (sess_id, s_date))
        cursor.execute("""
        INSERT INTO messages (session_id, sender, text, timestamp)
        VALUES (?, 'user', 'Thank you. I am glad to be here and ready to discuss the topic.', ?)
        """, (sess_id, s_date))


def get_user_profile():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
    conn.close()
    if user:
        return dict(user)
    return {
        "id": "user_default",
        "name": "Rohit",
        "level": "Intermediate",
        "goal": "Professional English",
        "avatar": "👨‍💼",
        "streak_days": 5,
        "total_practice_minutes": 222
    }


def update_user_profile(name, level, goal, avatar="👨‍💼"):
    conn = get_db_connection()
    conn.execute("""
    UPDATE users SET name = ?, level = ?, goal = ?, avatar = ? WHERE id = 'user_default'
    """, (name, level, goal, avatar))
    conn.commit()
    conn.close()
    return get_user_profile()


def save_session(session_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sessions (
        id, user_id, date, mode, scenario_id, scenario_title, role,
        duration_minutes, turns, score_overall, grammar_score, vocab_score,
        clarity_score, tone_score, confidence_score, main_mistakes,
        key_improvement, top_strengths, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_data["id"],
        session_data.get("user_id", "user_default"),
        session_data["date"],
        session_data["mode"],
        session_data["scenario_id"],
        session_data["scenario_title"],
        session_data["role"],
        session_data.get("duration_minutes", 5),
        session_data.get("turns", 1),
        session_data["score_overall"],
        session_data["scores"]["grammar"],
        session_data["scores"]["vocabulary"],
        session_data["scores"]["clarity"],
        session_data["scores"]["tone"],
        session_data["scores"].get("confidence", 7.5),
        json.dumps(session_data.get("main_mistakes", [])),
        session_data.get("key_improvement", "Continue regular practice."),
        json.dumps(session_data.get("top_strengths", [])),
        datetime.datetime.now().isoformat()
    ))

    # Save messages
    for msg in session_data.get("transcript", []):
        cursor.execute("""
        INSERT INTO messages (session_id, sender, text, timestamp)
        VALUES (?, ?, ?, ?)
        """, (session_data["id"], msg["sender"], msg["text"], msg.get("timestamp", datetime.datetime.now().isoformat())))

    # Update user practice minutes & streak
    cursor.execute("""
    UPDATE users SET 
        total_practice_minutes = total_practice_minutes + ?,
        streak_days = streak_days + 1
    WHERE id = 'user_default'
    """, (session_data.get("duration_minutes", 5),))

    conn.commit()
    conn.close()
    return session_data


def get_all_sessions():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM sessions ORDER BY created_at ASC").fetchall()
    conn.close()

    sessions = []
    for r in rows:
        d = dict(r)
        d["main_mistakes"] = json.loads(d["main_mistakes"]) if d["main_mistakes"] else []
        d["top_strengths"] = json.loads(d["top_strengths"]) if d["top_strengths"] else []
        d["scores"] = {
            "grammar": d["grammar_score"],
            "vocabulary": d["vocab_score"],
            "clarity": d["clarity_score"],
            "tone": d["tone_score"],
            "confidence": d["confidence_score"]
        }
        sessions.append(d)
    return sessions


def get_session_by_id(session_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not row:
        conn.close()
        return None
    d = dict(row)
    d["main_mistakes"] = json.loads(d["main_mistakes"]) if d["main_mistakes"] else []
    d["top_strengths"] = json.loads(d["top_strengths"]) if d["top_strengths"] else []
    d["scores"] = {
        "grammar": d["grammar_score"],
        "vocabulary": d["vocab_score"],
        "clarity": d["clarity_score"],
        "tone": d["tone_score"],
        "confidence": d["confidence_score"]
    }

    # Fetch transcript
    msg_rows = conn.execute("SELECT sender, text, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,)).fetchall()
    d["transcript"] = [dict(m) for m in msg_rows]
    conn.close()
    return d


def get_dashboard_stats():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
    sessions = conn.execute("SELECT * FROM sessions ORDER BY created_at ASC").fetchall()
    conn.close()

    total_sessions = len(sessions)
    if total_sessions == 0:
        return {
            "name": user["name"] if user else "Rohit",
            "sessions_completed": 0,
            "practice_time_str": "0m",
            "average_score": 0,
            "current_streak": 1,
            "skills": {"grammar": 70, "vocab": 70, "clarity": 70, "tone": 70, "confidence": 70},
            "trend": []
        }

    overalls = [s["score_overall"] for s in sessions]
    avg_score = round(sum(overalls) / total_sessions)
    
    total_minutes = sum(s["duration_minutes"] for s in sessions)
    hours = total_minutes // 60
    mins = total_minutes % 60
    time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"

    # Skill breakdown mapped to percentages (avg score / 10 * 100)
    avg_g = round(sum(s["grammar_score"] for s in sessions) / total_sessions * 10)
    avg_v = round(sum(s["vocab_score"] for s in sessions) / total_sessions * 10)
    avg_c = round(sum(s["clarity_score"] for s in sessions) / total_sessions * 10)
    avg_t = round(sum(s["tone_score"] for s in sessions) / total_sessions * 10)
    avg_conf = round(sum(s["confidence_score"] for s in sessions) / total_sessions * 10)

    # Trend for chart (Session 1 -> Session 12...)
    trend = [
        {
            "session_num": i + 1,
            "label": f"Session {i + 1}",
            "title": s["scenario_title"],
            "score": s["score_overall"],
            "date": s["date"]
        }
        for i, s in enumerate(sessions)
    ]

    return {
        "name": user["name"] if user else "Rohit",
        "sessions_completed": total_sessions,
        "practice_time_str": time_str,
        "average_score": avg_score,
        "current_streak": user["streak_days"] if user else 5,
        "skills": {
            "grammar": avg_g,
            "vocabulary": avg_v,
            "clarity": avg_c,
            "tone": avg_t,
            "confidence": avg_conf
        },
        "trend": trend
    }


def reset_database():
    """Reset the database to default demo state."""
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass
    init_db()


# Initialize database on module import
init_db()
