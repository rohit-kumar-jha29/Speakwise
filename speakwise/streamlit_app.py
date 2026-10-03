"""
streamlit_app.py — SpeakWise AI
A Streamlit-based AI-powered Language & Soft-Skills Practice Chatbot.
Run with:  streamlit run streamlit_app.py
"""

import streamlit as st
import os
import datetime
import json
import uuid

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SpeakWise AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load .env if present (Streamlit Cloud uses st.secrets instead) ──────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from ai_service import AIService
from database import (
    get_user_profile, update_user_profile,
    get_all_sessions, get_session_by_id,
    get_dashboard_stats, save_session,
)
from scenarios import get_all_scenarios, get_scenario, get_scenarios_by_category
from challenges import GRAMMAR_CHALLENGES, VOCABULARY_CHALLENGES, SITUATION_CHALLENGES

# ── Resolve API key: Streamlit secrets > env var ────────────────────────────
def _resolve_api_key() -> str:
    # Streamlit Cloud secrets
    try:
        k = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("AI_API_KEY") or ""
        if k:
            return k
    except Exception:
        pass
    return (
        os.getenv("AI_API_KEY", "") or
        os.getenv("GEMINI_API_KEY", "") or
        os.getenv("OPENAI_API_KEY", "")
    ).strip()

# ── Singleton AI service stored in session state ─────────────────────────────
if "ai_service" not in st.session_state:
    svc = AIService()
    key = _resolve_api_key()
    if key:
        svc.set_api_key(key)
    st.session_state["ai_service"] = svc

ai: AIService = st.session_state["ai_service"]

# ── Session-state defaults ───────────────────────────────────────────────────
DEFAULTS = {
    "page": "dashboard",
    "chat_history": [],
    "chat_scenario": "free_conversation",
    "chat_turn": 0,
    "roleplay_scenario": None,
    "roleplay_history": [],
    "roleplay_turn": 0,
    "roleplay_active": False,
    "interview_type": None,
    "interview_history": [],
    "interview_turn": 0,
    "interview_active": False,
    "grammar_challenge_idx": 0,
    "grammar_attempts": {},
    "vocab_challenge_idx": 0,
    "session_start_time": None,
    "profile": None,
    "last_feedback": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Load user profile once ───────────────────────────────────────────────────
if st.session_state["profile"] is None:
    st.session_state["profile"] = get_user_profile()

profile = st.session_state["profile"]

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global font */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar nav buttons */
div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-size: 0.95rem;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    margin-bottom: 2px;
    transition: background 0.2s;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12);
}

/* Metric card */
.sw-metric {
    background: linear-gradient(135deg,#1e293b,#0f172a);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
}
.sw-metric h1 { font-size:2.2rem; margin:0; color:#38bdf8; }
.sw-metric p  { margin:0; color:#94a3b8; font-size:0.85rem; }

/* Chat bubbles */
.chat-bubble-ai {
    background:#1e293b; border:1px solid #334155;
    border-radius:14px 14px 14px 0;
    padding:0.9rem 1.1rem; margin-bottom:0.6rem;
    color:#e2e8f0; max-width:78%;
}
.chat-bubble-user {
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    border-radius:14px 14px 0 14px;
    padding:0.9rem 1.1rem; margin-bottom:0.6rem;
    color:#fff; max-width:78%; margin-left:auto;
}
.chat-label { font-size:0.72rem; color:#64748b; margin-bottom:0.2rem; }

/* Feedback card */
.feedback-card {
    background:#0f172a; border:1px solid #1e3a5f;
    border-radius:12px; padding:1rem 1.2rem;
    margin-top:0.6rem; color:#e2e8f0;
}
.feedback-card h4 { color:#38bdf8; margin:0 0 0.4rem; }

/* Score badge */
.score-badge {
    display:inline-block;
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    color:#fff; border-radius:20px;
    padding:2px 12px; font-size:0.82rem;
    font-weight:600;
}

/* Section header */
.sw-section-title {
    font-size:1.6rem; font-weight:700;
    color:#f1f5f9; margin-bottom:0.2rem;
}
.sw-section-sub { color:#64748b; margin-bottom:1.2rem; }

/* Progress skill bar */
.skill-bar-wrap { margin-bottom:0.5rem; }
.skill-bar-label { display:flex; justify-content:space-between; color:#94a3b8; font-size:0.82rem; margin-bottom:3px; }
.skill-bar-bg { background:#1e293b; border-radius:20px; height:10px; }
.skill-bar-fill { height:10px; border-radius:20px;
    background:linear-gradient(90deg,#2563eb,#7c3aed); }

/* Scenario card */
.scenario-card {
    background:#1e293b; border:1px solid #334155;
    border-radius:12px; padding:1rem; margin-bottom:0.5rem;
    cursor:pointer; transition:border-color 0.2s;
}
.scenario-card:hover { border-color:#2563eb; }

/* Warning / success */
.sw-success { color:#22c55e; font-weight:600; }
.sw-warning { color:#f59e0b; font-weight:600; }
.sw-error   { color:#ef4444; font-weight:600; }

/* Session history card */
.history-card {
    background:#1e293b; border:1px solid #334155;
    border-radius:12px; padding:1rem 1.2rem;
    margin-bottom:0.5rem; color:#e2e8f0;
}
.history-card h4 { margin:0 0 0.3rem; color:#f1f5f9; }
.history-card p  { margin:0; color:#94a3b8; font-size:0.82rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 SpeakWise AI")
    st.markdown(f"**{profile.get('name','Rohit')}** · {profile.get('level','Intermediate')}")
    st.markdown("---")

    nav_items = [
        ("🏠", "Dashboard",          "dashboard"),
        ("💬", "AI Practice",        "chat"),
        ("🎭", "Role Play",          "roleplay"),
        ("🎤", "Interview Practice", "interview"),
        ("✍️", "Grammar Practice",   "grammar"),
        ("📚", "Vocabulary",         "vocab"),
        ("📊", "Progress",           "progress"),
        ("🕘", "Session History",    "history"),
    ]
    for icon, label, page_key in nav_items:
        if st.button(f"{icon}  {label}", key=f"nav_{page_key}"):
            st.session_state["page"] = page_key
            st.rerun()

    st.markdown("---")
    # Engine status
    status = ai.get_status()
    if status["is_simulated"]:
        st.markdown("🟡 **Demo Mode** (Simulated AI)")
    else:
        st.markdown("🟢 **Real AI Mode** (Live LLM)")

    with st.expander("⚙️ API Settings"):
        new_key = st.text_input("Gemini / OpenAI API Key", type="password",
                                placeholder="AIzaSy... or sk-...",
                                value=ai.api_key or "")
        provider_opt = st.selectbox("Provider", ["gemini", "openai"],
                                    index=0 if ai.provider == "gemini" else 1)
        if st.button("💾 Save Key"):
            ai.set_api_key(new_key, provider_opt)
            st.success("Key saved!")
            st.rerun()

    with st.expander("👤 Edit Profile"):
        new_name  = st.text_input("Name",  value=profile.get("name", "Rohit"))
        new_level = st.selectbox("Level",
                                 ["Beginner", "Intermediate", "Advanced"],
                                 index=["Beginner","Intermediate","Advanced"].index(
                                     profile.get("level","Intermediate")))
        new_goal  = st.selectbox("Goal",
                                 ["General Conversation","Grammar",
                                  "Professional English","Interview Preparation",
                                  "Presentation Skills","Confidence Building"],
                                 index=0)
        if st.button("💾 Save Profile"):
            updated = update_user_profile(new_name, new_level, new_goal)
            st.session_state["profile"] = updated
            profile = updated
            st.success("Profile updated!")
            st.rerun()

page = st.session_state["page"]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_chat_bubble(sender: str, text: str):
    if sender == "ai":
        st.markdown(f"""
        <div class="chat-label">🤖 AI Coach</div>
        <div class="chat-bubble-ai">{text}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-label" style="text-align:right">👤 You</div>
        <div class="chat-bubble-user">{text}</div>
        """, unsafe_allow_html=True)


def render_feedback(fb: dict):
    if not fb:
        return
    with st.expander("📋 Feedback & Analysis", expanded=False):
        cols = st.columns(5)
        score_labels = [
            ("Grammar",    fb["grammar"]["score"]),
            ("Vocabulary", fb["vocabulary"]["score"]),
            ("Clarity",    fb["clarity"]["score"]),
            ("Tone",       fb["tone"]["score"]),
            ("Confidence", fb.get("confidence", 7.5)),
        ]
        for col, (lbl, val) in zip(cols, score_labels):
            col.metric(lbl, f"{val:.1f}/10")

        if fb["grammar"]["errors"]:
            st.markdown("**✏️ Grammar**")
            for err in fb["grammar"]["errors"]:
                st.markdown(f"- ❌ *{err['original']}* → ✅ **{err['improved']}**  \n  _{err['explanation']}_")

        if fb["vocabulary"]["suggestions"]:
            st.markdown("**💡 Vocabulary Upgrades**")
            for sug in fb["vocabulary"]["suggestions"]:
                st.markdown(f"- {sug['formatted']}")

        tone = fb["tone"]
        st.markdown(f"**🎭 Tone:** `{tone['label']}` — {tone['suggestion']}")

        nv = fb.get("natural_version","")
        pv = fb.get("professional_version","")
        if nv:
            st.markdown("**🗣️ More Natural Version**")
            st.info(nv)
        if pv and pv != nv:
            st.markdown("**💼 Professional Version**")
            st.success(pv)


def skill_bar_html(label: str, value: int, color="#2563eb") -> str:
    return f"""
    <div class="skill-bar-wrap">
      <div class="skill-bar-label"><span>{label}</span><span>{value}%</span></div>
      <div class="skill-bar-bg">
        <div class="skill-bar-fill" style="width:{value}%;background:linear-gradient(90deg,{color},{color}aa)"></div>
      </div>
    </div>"""


def end_and_save_session(mode, scenario_id, scenario_title, role, history):
    """Generate a session report, save to DB, and display summary."""
    user_texts = [m["text"] for m in history if m["sender"] == "user"]
    combined  = " ".join(user_texts)
    report    = ai.generateSessionReport(scenario_title, history, profile)
    duration  = max(1, len(history) // 2)

    sess_id = f"sess_{uuid.uuid4().hex[:8]}"
    save_session({
        "id":             sess_id,
        "user_id":        "user_default",
        "date":           datetime.datetime.now().strftime("%d %b %Y %H:%M"),
        "mode":           mode,
        "scenario_id":    scenario_id,
        "scenario_title": scenario_title,
        "role":           role,
        "duration_minutes": duration,
        "turns":          len(user_texts),
        "score_overall":  report["overall_score"],
        "scores":         report["scores"],
        "main_mistakes":  report["areas_to_improve"],
        "key_improvement": report["areas_to_improve"][0] if report["areas_to_improve"] else "",
        "top_strengths":  report["strengths"],
        "transcript":     history,
    })

    st.success("✅ Session saved!")
    st.markdown(f"### 📊 Communication Report — *{scenario_title}*")
    st.markdown(f"**Overall Score: {report['overall_score']}/100**")
    cols = st.columns(5)
    for col, (lbl, val) in zip(cols, [
        ("Grammar",    report["scores"]["grammar"]),
        ("Vocabulary", report["scores"]["vocabulary"]),
        ("Clarity",    report["scores"]["clarity"]),
        ("Tone",       report["scores"]["tone"]),
        ("Confidence", report["scores"]["confidence"]),
    ]):
        col.metric(lbl, f"{val:.1f}/10")

    st.markdown("**💪 Strengths**")
    for s in report["strengths"]:
        st.markdown(f"- ✅ {s}")
    st.markdown("**📈 Areas to Improve**")
    for a in report["areas_to_improve"]:
        st.markdown(f"- 🔧 {a}")
    st.markdown("**💡 Better Answers**")
    for ba in report["suggested_better_answers"]:
        st.markdown(f"- **{ba['context']}:** _{ba['better_answer']}_")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "dashboard":
    stats = get_dashboard_stats()

    st.markdown('<p class="sw-section-title">🏠 Dashboard</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sw-section-sub">Welcome back, <b>{stats["name"]}</b>! Keep up the great work. 🚀</p>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="sw-metric"><h1>{stats['sessions_completed']}</h1>
        <p>Sessions Completed</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="sw-metric"><h1>{stats['practice_time_str']}</h1>
        <p>Total Practice Time</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="sw-metric"><h1>{stats['average_score']}</h1>
        <p>Average Score / 100</p></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="sw-metric"><h1>{stats['current_streak']}🔥</h1>
        <p>Day Streak</p></div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_skills, col_trend = st.columns([1, 2])

    with col_skills:
        st.markdown("### 📊 Skill Breakdown")
        skills = stats.get("skills", {})
        color_map = {
            "grammar":    "#2563eb",
            "vocabulary": "#7c3aed",
            "clarity":    "#0891b2",
            "tone":       "#059669",
            "confidence": "#d97706",
        }
        for skill_key, color in color_map.items():
            val = skills.get(skill_key, 70)
            label = skill_key.capitalize()
            st.markdown(skill_bar_html(label, val, color), unsafe_allow_html=True)

    with col_trend:
        st.markdown("### 📈 Score Trend")
        trend = stats.get("trend", [])
        if trend:
            import pandas as pd
            df = pd.DataFrame(trend)[["session_num", "score"]].rename(
                columns={"session_num": "Session", "score": "Score"})
            st.line_chart(df.set_index("Session"), height=260)
        else:
            st.info("Complete your first session to see your progress trend!")

    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("💬 Start AI Practice", use_container_width=True):
            st.session_state["page"] = "chat"
            st.rerun()
    with qc2:
        if st.button("🎭 Role Play", use_container_width=True):
            st.session_state["page"] = "roleplay"
            st.rerun()
    with qc3:
        if st.button("🎤 Interview Prep", use_container_width=True):
            st.session_state["page"] = "interview"
            st.rerun()
    with qc4:
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state["page"] = "progress"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AI PRACTICE (Free Chat)
# ─────────────────────────────────────────────────────────────────────────────
elif page == "chat":
    st.markdown('<p class="sw-section-title">💬 AI Practice</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Chat freely with your AI coach. Practice any topic.</p>',
                unsafe_allow_html=True)

    # Scenario selector in sidebar-style expander
    with st.expander("⚙️ Scenario", expanded=False):
        scenarios = get_all_scenarios()
        scenario_titles = {s["id"]: f"{s['badge']} {s['title']}" for s in scenarios}
        sel = st.selectbox("Practice Scenario",
                           list(scenario_titles.keys()),
                           format_func=lambda x: scenario_titles[x],
                           index=list(scenario_titles.keys()).index(
                               st.session_state["chat_scenario"]))
        if sel != st.session_state["chat_scenario"]:
            st.session_state["chat_scenario"] = sel
            st.session_state["chat_history"] = []
            st.session_state["chat_turn"]    = 0

        if st.button("🔄 Reset Conversation"):
            st.session_state["chat_history"] = []
            st.session_state["chat_turn"]    = 0
            st.rerun()

    # Initial greeting
    scenario = get_scenario(st.session_state["chat_scenario"])
    if not st.session_state["chat_history"]:
        starter = scenario.get("starter_message", "Hi! What would you like to practice?")
        st.session_state["chat_history"].append({"sender": "ai", "text": starter})

    # Render chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            render_chat_bubble(msg["sender"], msg["text"])

    # Render last feedback
    if st.session_state.get("last_feedback"):
        render_feedback(st.session_state["last_feedback"])

    # Input
    st.markdown("---")
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input("Your message", placeholder="Type your message here...",
                                   label_visibility="collapsed", key="chat_input_box")
    with col_send:
        send_clicked = st.button("Send ➤", use_container_width=True)

    if send_clicked and user_input.strip():
        st.session_state["chat_history"].append({"sender": "user", "text": user_input})
        st.session_state["chat_turn"] += 1

        with st.spinner("AI is thinking..."):
            result = ai.sendMessage(
                user_message=user_input,
                scenario_id=st.session_state["chat_scenario"],
                history=st.session_state["chat_history"],
                profile=profile,
                turn_count=st.session_state["chat_turn"],
            )

        st.session_state["chat_history"].append({"sender": "ai", "text": result["ai_reply"]})
        st.session_state["last_feedback"] = result.get("feedback")
        st.rerun()

    # End session button
    if len([m for m in st.session_state["chat_history"] if m["sender"] == "user"]) >= 2:
        if st.button("🏁 End Session & Get Report"):
            end_and_save_session(
                mode="free_conversation",
                scenario_id=st.session_state["chat_scenario"],
                scenario_title=scenario.get("title","Free Conversation"),
                role=scenario.get("role","AI Coach"),
                history=st.session_state["chat_history"],
            )
            st.session_state["chat_history"] = []
            st.session_state["chat_turn"]    = 0

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ROLE PLAY
# ─────────────────────────────────────────────────────────────────────────────
elif page == "roleplay":
    st.markdown('<p class="sw-section-title">🎭 Role Play</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Step into a real-world scenario and practice your communication.</p>',
                unsafe_allow_html=True)

    if not st.session_state["roleplay_active"]:
        # Scenario selector
        by_cat = get_scenarios_by_category()
        # Exclude Interview Track from Role Play
        categories = [c for c in by_cat.keys() if c != "Interview Track"]

        for cat in categories:
            st.markdown(f"### {cat}")
            scenarios_in_cat = by_cat[cat]
            cols = st.columns(3)
            for i, sc in enumerate(scenarios_in_cat):
                with cols[i % 3]:
                    st.markdown(f"""<div class="scenario-card">
                    <b>{sc['badge']} {sc['title']}</b><br>
                    <small style="color:#94a3b8">{sc['description']}</small>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Start →", key=f"rp_{sc['id']}"):
                        st.session_state["roleplay_scenario"] = sc["id"]
                        st.session_state["roleplay_history"]  = []
                        st.session_state["roleplay_turn"]     = 0
                        st.session_state["roleplay_active"]   = True
                        st.session_state["session_start_time"] = datetime.datetime.now()
                        st.rerun()
    else:
        sc_id  = st.session_state["roleplay_scenario"]
        sc     = get_scenario(sc_id)
        title  = sc.get("title", "Role Play")
        role   = sc.get("role",  "AI Coach")
        tip    = sc.get("coach_tip", "")

        st.markdown(f"#### 🎭 {sc['badge']} {title}")
        st.markdown(f"*Playing as: **{role}***")
        if tip:
            st.info(f"💡 Coach Tip: {tip}")

        # Inject starter if empty
        if not st.session_state["roleplay_history"]:
            st.session_state["roleplay_history"].append({
                "sender": "ai",
                "text": sc.get("starter_message", "Let's begin the scenario.")
            })

        for msg in st.session_state["roleplay_history"]:
            render_chat_bubble(msg["sender"], msg["text"])

        st.markdown("---")
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            rp_input = st.text_input("Your response", placeholder="Respond naturally...",
                                     label_visibility="collapsed", key="rp_input_box")
        with col_btn:
            rp_send = st.button("Send ➤", key="rp_send", use_container_width=True)

        if rp_send and rp_input.strip():
            st.session_state["roleplay_history"].append({"sender": "user", "text": rp_input})
            st.session_state["roleplay_turn"] += 1

            with st.spinner("..."):
                result = ai.sendMessage(
                    user_message=rp_input,
                    scenario_id=sc_id,
                    history=st.session_state["roleplay_history"],
                    profile=profile,
                    turn_count=st.session_state["roleplay_turn"],
                )
            st.session_state["roleplay_history"].append({"sender": "ai", "text": result["ai_reply"]})
            st.session_state["last_feedback"] = result.get("feedback")
            st.rerun()

        # Show feedback every few turns
        turns_done = len([m for m in st.session_state["roleplay_history"] if m["sender"] == "user"])
        if turns_done > 0 and turns_done % 3 == 0 and st.session_state.get("last_feedback"):
            render_feedback(st.session_state["last_feedback"])

        col_fb, col_end = st.columns([1, 1])
        with col_fb:
            if st.button("📋 Get Feedback Now"):
                if st.session_state.get("last_feedback"):
                    render_feedback(st.session_state["last_feedback"])
        with col_end:
            if st.button("🏁 End Role Play"):
                end_and_save_session(
                    mode="roleplay", scenario_id=sc_id,
                    scenario_title=title, role=role,
                    history=st.session_state["roleplay_history"],
                )
                st.session_state["roleplay_active"]  = False
                st.session_state["roleplay_history"] = []
                st.session_state["roleplay_turn"]    = 0

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: INTERVIEW PRACTICE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "interview":
    st.markdown('<p class="sw-section-title">🎤 Interview Practice</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Simulate real interview rounds for different job roles.</p>',
                unsafe_allow_html=True)

    INTERVIEW_TYPES = [
        "HR", "Business Analyst", "Marketing",
        "Sales", "Data Analytics", "General Management"
    ]

    if not st.session_state["interview_active"]:
        st.markdown("### Choose your Interview Track")
        cols = st.columns(3)
        icons = ["👥","📊","📣","🎯","📉","🏛️"]
        for i, itype in enumerate(INTERVIEW_TYPES):
            with cols[i % 3]:
                if st.button(f"{icons[i]} {itype} Interview", use_container_width=True, key=f"iv_{i}"):
                    st.session_state["interview_type"]    = itype
                    st.session_state["interview_history"] = []
                    st.session_state["interview_turn"]    = 0
                    st.session_state["interview_active"]  = True
                    # Map to scenario and get starter
                    scen_map = {
                        "HR": "interview_hr",
                        "Business Analyst": "interview_ba",
                        "Marketing": "interview_marketing",
                        "Sales": "interview_sales",
                        "Data Analytics": "interview_data",
                        "General Management": "interview_management"
                    }
                    scen_id = scen_map.get(itype, "interview_hr")
                    sc = get_scenario(scen_id)
                    starter = sc.get("starter_message","Let's begin the interview.")
                    tip     = sc.get("coach_tip","")
                    st.session_state["interview_history"].append({"sender":"ai","text":starter})
                    st.session_state["interview_coach_tip"] = tip
                    st.session_state["interview_scen_id"]   = scen_id
                    st.rerun()
    else:
        itype = st.session_state["interview_type"]
        scen_id = st.session_state.get("interview_scen_id","interview_hr")
        sc = get_scenario(scen_id)
        tip   = st.session_state.get("interview_coach_tip","")

        st.markdown(f"#### 🎤 {itype} Interview")
        if tip:
            st.info(f"💡 {tip}")

        for msg in st.session_state["interview_history"]:
            render_chat_bubble(msg["sender"], msg["text"])

        st.markdown("---")
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            iv_input = st.text_input("Your answer", placeholder="Answer the question...",
                                     label_visibility="collapsed", key="iv_input_box")
        with col_btn:
            iv_send = st.button("Send ➤", key="iv_send", use_container_width=True)

        if iv_send and iv_input.strip():
            st.session_state["interview_history"].append({"sender":"user","text":iv_input})
            st.session_state["interview_turn"] += 1

            with st.spinner("Preparing next question..."):
                result = ai.sendMessage(
                    user_message=iv_input,
                    scenario_id=scen_id,
                    history=st.session_state["interview_history"],
                    profile=profile,
                    turn_count=st.session_state["interview_turn"],
                )
            st.session_state["interview_history"].append({"sender":"ai","text":result["ai_reply"]})
            st.session_state["last_feedback"] = result.get("feedback")
            st.rerun()

        col_fb, col_end = st.columns([1,1])
        with col_fb:
            if st.button("📋 Get Feedback"):
                if st.session_state.get("last_feedback"):
                    render_feedback(st.session_state["last_feedback"])
        with col_end:
            if st.button("🏁 End Interview"):
                end_and_save_session(
                    mode="interview", scenario_id=scen_id,
                    scenario_title=f"{itype} Interview",
                    role=sc.get("role","Interviewer"),
                    history=st.session_state["interview_history"],
                )
                st.session_state["interview_active"]  = False
                st.session_state["interview_history"] = []
                st.session_state["interview_turn"]    = 0

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GRAMMAR PRACTICE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "grammar":
    st.markdown('<p class="sw-section-title">✍️ Grammar Practice</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Fix real grammar mistakes with explanations.</p>',
                unsafe_allow_html=True)

    tab_challenge, tab_quiz = st.tabs(["🔧 Correction Challenges", "📝 Quick Quiz"])

    with tab_challenge:
        idx = st.session_state["grammar_challenge_idx"]
        challenges = GRAMMAR_CHALLENGES

        if idx >= len(challenges):
            st.success("🎉 You've completed all grammar challenges!")
            if st.button("🔄 Start Over"):
                st.session_state["grammar_challenge_idx"] = 0
                st.session_state["grammar_attempts"]      = {}
                st.rerun()
        else:
            ch = challenges[idx]
            st.markdown(f"**Challenge {idx + 1} / {len(challenges)}**  ·  `{ch['category']}`")
            st.markdown(f"##### {ch['prompt']}")
            st.error(f"❌ *{ch['sentence']}*")
            st.markdown(f"**Rule:** {ch['rule_summary']}")

            key = f"gram_ans_{idx}"
            user_ans = st.text_input("Your corrected sentence:", key=key)

            attempt_key = f"attempt_{idx}"
            if st.button("✅ Check Answer", key=f"check_{idx}"):
                if not user_ans.strip():
                    st.warning("Please enter your corrected sentence.")
                else:
                    accepted = [ch["correct_answer"].lower()] + [v.lower() for v in ch.get("accepted_variants",[])]
                    correct  = user_ans.strip().lower() in accepted

                    st.session_state["grammar_attempts"][attempt_key] = {
                        "answer": user_ans, "correct": correct
                    }

            if attempt_key in st.session_state["grammar_attempts"]:
                result_data = st.session_state["grammar_attempts"][attempt_key]
                if result_data["correct"]:
                    st.success("✅ Correct! Well done.")
                else:
                    st.error(f"❌ Not quite. Model answer: **{ch['correct_answer']}**")
                    st.info(f"📖 Explanation: {ch['explanation']}")

                if st.button("Next Challenge →", key=f"next_{idx}"):
                    st.session_state["grammar_challenge_idx"] += 1
                    st.rerun()

    with tab_quiz:
        quizzes = ai.generateGrammarQuiz(profile.get("level","Intermediate"))
        for i, q in enumerate(quizzes):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            sel = st.radio("", q["options"], key=f"quiz_q{i}", label_visibility="collapsed")
            if st.button("Check", key=f"quiz_check{i}"):
                chosen_letter = sel[0]
                if chosen_letter == q["correct_option"]:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Correct answer: **{q['correct_option']}**")
                st.info(f"📖 {q['explanation']}")
            st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: VOCABULARY
# ─────────────────────────────────────────────────────────────────────────────
elif page == "vocab":
    st.markdown('<p class="sw-section-title">📚 Vocabulary</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Build a professional and rich vocabulary.</p>',
                unsafe_allow_html=True)

    tab_word, tab_situation = st.tabs(["📖 Word Practice", "🎬 Situation Writing"])

    with tab_word:
        idx = st.session_state["vocab_challenge_idx"]
        vocab_list = VOCABULARY_CHALLENGES

        if idx >= len(vocab_list):
            st.success("🎉 You've practised all vocabulary words!")
            if st.button("🔄 Start Over", key="vocab_restart"):
                st.session_state["vocab_challenge_idx"] = 0
                st.rerun()
        else:
            vc = vocab_list[idx]
            st.markdown(f"### Word: **{vc['word']}** `{vc['part_of_speech']}`")
            st.markdown(f"**Definition:** {vc['definition']}")
            st.markdown(f"**Synonyms:** {', '.join(vc['synonyms'])}")
            st.info(f"📝 Example: *{vc['example']}*")
            st.markdown(f"**Your task:** {vc['prompt']}")
            st.markdown(f"💡 *Hint: {vc['ideal_usage_hint']}*")

            user_sentence = st.text_area("Write your sentence:", key=f"vocab_ans_{idx}", height=80)
            if st.button("✅ Submit & Get Feedback", key=f"vocab_submit_{idx}"):
                if user_sentence.strip():
                    with st.spinner("Analyzing..."):
                        fb = ai.generateFeedback(user_sentence, profile)
                    render_feedback(fb)
                    if st.button("Next Word →", key=f"vocab_next_{idx}"):
                        st.session_state["vocab_challenge_idx"] += 1
                        st.rerun()
                else:
                    st.warning("Please write a sentence first.")

    with tab_situation:
        for sc in SITUATION_CHALLENGES:
            with st.expander(f"🎬 {sc['title']} [{sc['difficulty']}]"):
                st.markdown(f"**Context:** {sc['context']}")
                st.markdown(f"**Task:** {sc['task']}")
                st.markdown(f"**Key Competencies:** {', '.join(sc['key_competencies'])}")
                user_resp = st.text_area("Your response:", key=f"sit_{sc['id']}", height=120)
                if st.button("✅ Get Feedback", key=f"sit_fb_{sc['id']}"):
                    if user_resp.strip():
                        with st.spinner("Analyzing..."):
                            fb = ai.generateFeedback(user_resp, profile)
                        render_feedback(fb)
                        st.markdown("**📋 Model Answer:**")
                        st.success(sc["model_answer"])

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PROGRESS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "progress":
    st.markdown('<p class="sw-section-title">📊 Progress</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Track your improvement across all practice sessions.</p>',
                unsafe_allow_html=True)

    sessions = get_all_sessions()
    stats    = get_dashboard_stats()

    if not sessions:
        st.info("Complete your first session to see progress charts!")
    else:
        import pandas as pd

        df = pd.DataFrame(sessions)

        # Score trend
        st.markdown("### 📈 Overall Score Trend")
        df_trend = df[["scenario_title","score_overall"]].reset_index()
        df_trend.columns = ["Session","Scenario","Score"]
        df_trend["Session"] += 1
        st.line_chart(df_trend.set_index("Session")[["Score"]], height=260)

        st.markdown("### 📊 Skill Scores Over Sessions")
        skill_cols = {
            "grammar_score": "Grammar",
            "vocab_score":   "Vocabulary",
            "clarity_score": "Clarity",
            "tone_score":    "Tone",
            "confidence_score": "Confidence"
        }
        existing_cols = [c for c in skill_cols if c in df.columns]
        if existing_cols:
            df_skills = df[existing_cols].copy()
            df_skills.columns = [skill_cols[c] for c in existing_cols]
            df_skills.index   = range(1, len(df_skills) + 1)
            df_skills.index.name = "Session"
            st.line_chart(df_skills, height=280)

        # Skill breakdown bars
        st.markdown("### 🏅 Current Skill Levels")
        skills = stats.get("skills", {})
        c1, c2 = st.columns(2)
        with c1:
            for sk in ["grammar","vocabulary","clarity"]:
                val = skills.get(sk, 70)
                st.markdown(skill_bar_html(sk.capitalize(), val), unsafe_allow_html=True)
        with c2:
            for sk in ["tone","confidence"]:
                val = skills.get(sk, 70)
                st.markdown(skill_bar_html(sk.capitalize(), val), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SESSION HISTORY
# ─────────────────────────────────────────────────────────────────────────────
elif page == "history":
    st.markdown('<p class="sw-section-title">🕘 Session History</p>', unsafe_allow_html=True)
    st.markdown('<p class="sw-section-sub">Review all your past practice sessions.</p>',
                unsafe_allow_html=True)

    sessions = get_all_sessions()
    if not sessions:
        st.info("No sessions yet. Complete a practice session to see it here!")
    else:
        sessions_rev = list(reversed(sessions))
        for s in sessions_rev:
            score_color = "#22c55e" if s["score_overall"] >= 75 else ("#f59e0b" if s["score_overall"] >= 60 else "#ef4444")
            mode_badge  = {"roleplay":"🎭","interview":"🎤","grammar":"✍️","vocab":"📚","free_conversation":"💬"}.get(s["mode"],"💬")

            with st.expander(
                f"{mode_badge} {s['scenario_title']} · "
                f"Score: {s['score_overall']}/100 · {s['date']}"
            ):
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Grammar",    f"{s['grammar_score']:.1f}")
                c2.metric("Vocabulary", f"{s['vocab_score']:.1f}")
                c3.metric("Clarity",    f"{s['clarity_score']:.1f}")
                c4.metric("Tone",       f"{s['tone_score']:.1f}")
                c5.metric("Confidence", f"{s['confidence_score']:.1f}")

                st.markdown(f"**🕐 Duration:** {s['duration_minutes']} min  |  "
                            f"**💬 Turns:** {s['turns']}  |  "
                            f"**🎭 Role:** {s['role']}")

                if s.get("main_mistakes"):
                    st.markdown("**📈 Key Improvements:**")
                    for m in s["main_mistakes"][:2]:
                        st.markdown(f"- 🔧 {m}")

                if s.get("top_strengths"):
                    st.markdown("**💪 Strengths:**")
                    for st_ in s["top_strengths"][:2]:
                        st.markdown(f"- ✅ {st_}")

                # Full transcript
                full = get_session_by_id(s["id"])
                if full and full.get("transcript"):
                    st.markdown("**📜 Session Transcript:**")
                    for msg in full["transcript"]:
                        render_chat_bubble(msg["sender"], msg["text"])
