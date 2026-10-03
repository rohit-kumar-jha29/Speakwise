"""
app.py - Main Flask Application Server for SpeakWise AI.
Bridges SQLite persistence, Modular AI Service Layer, and REST API endpoints.
"""

import os
import datetime
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

from database import (
    get_user_profile, update_user_profile, get_all_sessions,
    get_session_by_id, save_session, get_dashboard_stats, reset_database
)
from scenarios import get_all_scenarios, get_scenarios_by_category, get_scenario
from ai_service import ai_service
from challenges import VOCABULARY_CHALLENGES, SITUATION_CHALLENGES

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "speakwise_ai_secure_token_2026")


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")


# ----------------- ENGINE STATUS & CONFIG -----------------
@app.route("/api/engine/status", methods=["GET"])
def get_engine_status():
    status = ai_service.get_status()
    return jsonify({
        "status": status["status"],
        "mode": status["mode"],
        "is_simulated": status["is_simulated"],
        "provider": status["provider"],
        "has_key": status["has_key"],
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/api/engine/key", methods=["POST"])
def set_engine_key():
    data = request.get_json() or {}
    key = data.get("api_key", "").strip()
    provider = data.get("provider", "gemini")
    ai_service.set_api_key(key, provider)
    status = ai_service.get_status()
    return jsonify({
        "success": True,
        "message": "Switched to Real AI Mode with configured LLM API." if key else "Switched to Demo Mode (Simulated AI).",
        "mode": status["mode"],
        "is_simulated": status["is_simulated"]
    })


# ----------------- USER PROFILE -----------------
@app.route("/api/profile", methods=["GET"])
def profile_get():
    return jsonify(get_user_profile())


@app.route("/api/profile", methods=["POST"])
def profile_update():
    data = request.get_json() or {}
    name = data.get("name", "Rohit")
    level = data.get("level", "Intermediate")
    goal = data.get("goal", "Professional English")
    avatar = data.get("avatar", "👨‍💼")
    updated = update_user_profile(name, level, goal, avatar)
    return jsonify({"success": True, "profile": updated})


# ----------------- DASHBOARD STATS -----------------
@app.route("/api/dashboard", methods=["GET"])
def dashboard_stats():
    return jsonify(get_dashboard_stats())


# ----------------- SCENARIOS -----------------
@app.route("/api/scenarios", methods=["GET"])
def scenarios_list():
    return jsonify({
        "all": get_all_scenarios(),
        "categories": get_scenarios_by_category()
    })


@app.route("/api/scenarios/<scenario_id>", methods=["GET"])
def scenarios_single(scenario_id):
    return jsonify(get_scenario(scenario_id))


# ----------------- CHAT / ROLE PLAY TURN -----------------
@app.route("/api/chat", methods=["POST"])
def chat_turn():
    try:
        data = request.get_json() or {}
        message = data.get("message", "")
        scenario_id = data.get("scenario_id", "job_interview")
        history = data.get("history", [])
        turn_count = data.get("turn_count", 1)

        # Length validation
        if len(message) > 2000:
            return jsonify({
                "error": "Message is too long. Please keep your response under 2000 characters."
            }), 400

        profile = get_user_profile()
        result = ai_service.sendMessage(
            user_message=message,
            scenario_id=scenario_id,
            history=history,
            profile=profile,
            turn_count=turn_count
        )
        return jsonify(result)
    except Exception as e:
        print(f"Chat error: {e}")
        # Return graceful friendly message with Retry option, never 500 error
        return jsonify({
            "ai_reply": "I'm having trouble connecting right now. Please try again.",
            "feedback": None,
            "error_occurred": True,
            "retry_available": True
        }), 200


# ----------------- ON-DEMAND FEEDBACK ("GET FEEDBACK") -----------------
@app.route("/api/feedback", methods=["POST"])
def get_feedback():
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Please provide text to analyze."}), 400

    profile = get_user_profile()
    feedback = ai_service.generateFeedback(text, profile)
    return jsonify(feedback)


# ----------------- SESSION COMPLETION & HISTORY -----------------
@app.route("/api/sessions/complete", methods=["POST"])
def session_complete():
    data = request.get_json() or {}
    scenario_id = data.get("scenario_id", "job_interview")
    scenario_title = data.get("scenario_title", "Communication Practice")
    role = data.get("role", "AI Communication Coach")
    mode = data.get("mode", "roleplay")
    history = data.get("history", [])
    duration_minutes = data.get("duration_minutes", 5)

    profile = get_user_profile()
    report = ai_service.generateSessionReport(scenario_title, history, profile)

    session_record = {
        "id": f"sess_{int(datetime.datetime.now().timestamp())}",
        "user_id": profile.get("id", "user_default"),
        "date": datetime.datetime.now().strftime("%d %b %Y %H:%M"),
        "mode": mode,
        "scenario_id": scenario_id,
        "scenario_title": scenario_title,
        "role": role,
        "duration_minutes": duration_minutes,
        "turns": len([m for m in history if m.get("sender") == "user"]),
        "score_overall": report["overall_score"],
        "scores": report["scores"],
        "main_mistakes": report["areas_to_improve"][:2],
        "key_improvement": report["areas_to_improve"][0] if report["areas_to_improve"] else "Continue speaking regularly.",
        "top_strengths": report["strengths"],
        "transcript": history
    }

    saved = save_session(session_record)
    return jsonify({
        "success": True,
        "report": report,
        "session": saved
    })


@app.route("/api/sessions", methods=["GET"])
def sessions_list():
    return jsonify(get_all_sessions())


@app.route("/api/sessions/<session_id>", methods=["GET"])
def sessions_single(session_id):
    sess = get_session_by_id(session_id)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(sess)


# ----------------- PRACTICE MODES: GRAMMAR -----------------
@app.route("/api/grammar/quiz", methods=["GET"])
def grammar_quiz():
    level = request.args.get("level", "Intermediate")
    quizzes = ai_service.generateGrammarQuiz(level)
    return jsonify(quizzes)


# ----------------- PRACTICE MODES: VOCABULARY -----------------
@app.route("/api/vocab/challenges", methods=["GET"])
def vocab_challenges():
    return jsonify(VOCABULARY_CHALLENGES)


@app.route("/api/vocab/evaluate", methods=["POST"])
def vocab_evaluate():
    data = request.get_json() or {}
    word = data.get("word", "").strip().lower()
    sentence = data.get("sentence", "").strip()

    if not sentence:
        return jsonify({"error": "Please enter a sentence."}), 400

    contains_word = word in sentence.lower()
    profile = get_user_profile()
    feedback = ai_service.generateFeedback(sentence, profile)

    words = sentence.split()
    score = 7.0
    if contains_word:
        score += 2.0
    if len(words) >= 8:
        score += 1.0
    score = min(10.0, score)

    return jsonify({
        "contains_target_word": contains_word,
        "score": score,
        "feedback_comment": "Superb context and elevated sentence structure!" if contains_word and score >= 8.5 else (
            f"Please ensure you include the target word '{word}' naturally in your sentence." if not contains_word else "Good effort! Try incorporating specific business context."
        ),
        "natural_version": feedback["natural_version"],
        "professional_version": feedback["professional_version"],
        "tone": feedback["tone"]["label"]
    })


# ----------------- PRACTICE MODES: SITUATION -----------------
@app.route("/api/situation/challenges", methods=["GET"])
def situation_challenges():
    return jsonify(SITUATION_CHALLENGES)


@app.route("/api/situation/evaluate", methods=["POST"])
def situation_evaluate():
    data = request.get_json() or {}
    situation_id = data.get("id")
    response_text = data.get("response", "").strip()

    target = next((s for s in SITUATION_CHALLENGES if s["id"] == situation_id), None)
    if not target:
        return jsonify({"error": "Situation not found"}), 404

    profile = get_user_profile()
    feedback = ai_service.generateFeedback(response_text, profile)

    return jsonify({
        "overall_score": feedback["overall_100"],
        "tone_label": feedback["tone"]["label"],
        "tone_suggestion": feedback["tone"]["suggestion"],
        "natural_version": feedback["natural_version"],
        "professional_version": feedback["professional_version"],
        "model_answer": target["model_answer"],
        "feedback_comment": "Excellent diplomatic composure! Your response sets boundaries and solves the issue collaboratively."
    })


# ----------------- RESET DATABASE -----------------
@app.route("/api/reset", methods=["POST"])
def reset_all():
    reset_database()
    return jsonify({"success": True, "message": "SpeakWise reset to default demo state."})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"SpeakWise AI server running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
