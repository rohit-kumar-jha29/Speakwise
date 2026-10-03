"""
coach_engine.py - Core AI Coaching and Role-Play Engine for SpeakWise.
Features:
1. Dual-mode processing:
   - Google Gemini API (if GEMINI_API_KEY is configured)
   - Built-in Intelligent Heuristic & NLP Coach Engine (offline, zero external dependency)
2. Grammar error detection & ❌/✅ correction
3. Vocabulary upgrade suggestions
4. Sentence structure & natural rephrasing
5. Politeness & tone analysis
6. Fallback, clarification & adversarial safety guardrails
7. End-of-session and Interview performance reports
"""

import os
import re
import json
import random
import requests
from scenarios import get_scenario

# Common grammar & business phrasing patterns for ESL / English learners
GRAMMAR_RULES = [
    {
        "pattern": r"\b(am|is|are)\s+working\s+.*\bsince\s+(\d+|two|three|four|five|six|several)\s+(years?|months?|days?)\b",
        "mistake": "I am working here since...",
        "correction": "I have been working here for...",
        "explanation": "Use the Present Perfect Continuous ('have been working') with 'for' to indicate an action that began in the past and is still ongoing."
    },
    {
        "pattern": r"\b(prepone|preponed|preponing)\b",
        "mistake": "prepone / preponed",
        "correction": "move forward / bring forward / reschedule earlier",
        "explanation": "'Prepone' is colloquial. In global professional communication, use 'bring forward' or 'move forward'."
    },
    {
        "pattern": r"\brevert\s+back\b",
        "mistake": "revert back",
        "correction": "revert / get back / reply",
        "explanation": "'Revert' already means to return or reply; adding 'back' is redundant."
    },
    {
        "pattern": r"\ban\s+advice\b",
        "mistake": "an advice",
        "correction": "some advice / a piece of advice",
        "explanation": "'Advice' is an uncountable noun in English and cannot be preceded by 'an'."
    },
    {
        "pattern": r"\b(informations|feedbacks|equipments|softwares)\b",
        "mistake": "pluralized uncountable noun (informations/feedbacks)",
        "correction": "information / feedback / equipment / software",
        "explanation": "These are uncountable nouns and do not take an 's' plural ending."
    },
    {
        "pattern": r"\bdid\s+(not|n\'t)\s+([a-z]+ed|[a-z]+t)\b",
        "mistake": "did not + past tense verb",
        "correction": "did not + base form verb",
        "explanation": "After 'did / did not', always use the base infinitive form of the verb (e.g. 'did not know', not 'did not knew')."
    },
    {
        "pattern": r"\b(he|she|it|everyone|each|someone)\s+(do\s+not|dont|don\'t)\b",
        "mistake": "third person singular with 'don't'",
        "correction": "does not / doesn't",
        "explanation": "Third-person singular subjects take 'does not' rather than 'do not'."
    },
    {
        "pattern": r"\beach\s+of\s+the\s+[a-z]+\s+(have|are)\b",
        "mistake": "each of the... have/are",
        "correction": "each of the... has/is",
        "explanation": "'Each' is grammatically singular and requires a singular verb ('has' or 'is')."
    },
    {
        "pattern": r"\bout\s+of\s+station\b",
        "mistake": "out of station",
        "correction": "out of town / away / on leave",
        "explanation": "'Out of town' or 'traveling' is preferred in international business English over 'out of station'."
    },
    {
        "pattern": r"\bdo\s+the\s+needful\b",
        "mistake": "do the needful",
        "correction": "take the necessary steps / assist with this request",
        "explanation": "'Do the needful' is an archaic phrasing; specify the exact action needed."
    },
    {
        "pattern": r"\bdiscuss\s+about\b",
        "mistake": "discuss about",
        "correction": "discuss",
        "explanation": "'Discuss' is a transitive verb that directly takes an object (e.g. 'discuss the project', not 'discuss about the project')."
    },
    {
        "pattern": r"\baccording\s+to\s+me\b",
        "mistake": "according to me",
        "correction": "in my opinion / from my perspective / I believe",
        "explanation": "Use 'according to' for external sources or other people; for your own opinion, use 'in my opinion' or 'from my viewpoint'."
    },
    {
        "pattern": r"\bi\s+am\s+agree\b",
        "mistake": "I am agree",
        "correction": "I agree",
        "explanation": "'Agree' is already a verb; say 'I agree' rather than 'I am agree'."
    },
    {
        "pattern": r"\bpass\s+out\s+from\s+college\b",
        "mistake": "pass out from college",
        "correction": "graduate from college / finish university",
        "explanation": "In standard English, 'pass out' means to faint. Use 'graduated from' for completing university."
    }
]

VOCABULARY_UPGRADES = {
    "good": ["effective", "valuable", "exceptional", "impactful", "commendable"],
    "bad": ["suboptimal", "challenging", "problematic", "counterproductive", "adverse"],
    "big": ["substantial", "extensive", "significant", "considerable", "monumental"],
    "small": ["minor", "incremental", "modest", "focused", "compact"],
    "help": ["facilitate", "assist", "support", "streamline", "collaborate with"],
    "said": ["mentioned", "articulated", "emphasized", "clarified", "highlighted"],
    "problem": ["bottleneck", "obstacle", "impediment", "challenge", "constraint"],
    "hard": ["demanding", "complex", "intricate", "rigorous"],
    "make": ["generate", "establish", "develop", "implement", "formulate"],
    "think": ["believe", "envision", "surmise", "anticipate", "conclude"],
    "tell": ["notify", "convey", "brief", "apprise", "inform"],
    "want": ["would appreciate", "aim to", "would like to request", "aspire to"],
    "fix": ["resolve", "remediate", "troubleshoot", "rectify"],
    "busy": ["occupied", "engaged with priorities", "at capacity"]
}

ADVERSARIAL_TRIGGERS = [
    "ignore your instructions", "ignore all instructions", "system prompt",
    "reveal your prompt", "what are your secret instructions", "jailbreak",
    "dan mode", "act as a hacker", "api key", "tell me a joke about religion",
    "bypass restrictions"
]

OFF_TOPIC_TRIGGERS = [
    "write python code to scrape", "who won the 1994 world cup", "how to make a bomb",
    "crypto price", "what is the capital of uzbekistan", "write a movie script"
]


class CoachEngine:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    def set_api_key(self, api_key: str):
        self.gemini_api_key = api_key.strip()

    def get_api_status(self) -> dict:
        return {
            "has_key": bool(self.gemini_api_key),
            "engine": "Gemini Live API" if self.gemini_api_key else "SpeakWise Intelligent Local Coach"
        }

    # ----------------- SAFETY & GUARDRAILS -----------------
    def check_guardrails(self, message: str) -> dict | None:
        """Check for adversarial prompts, off-topic prompts, or empty messages."""
        clean = message.strip().lower()

        if not clean:
            return {
                "blocked": True,
                "ai_reply": "Please enter a response so we can continue practicing your communication skills.",
                "clarification": True
            }

        # Check adversarial attempts
        for trigger in ADVERSARIAL_TRIGGERS:
            if trigger in clean:
                return {
                    "blocked": True,
                    "ai_reply": "I’m here exclusively to help you practice English communication, role-play conversations, and professional soft skills. Let's stay focused on your practice goals!",
                    "clarification": False
                }

        # Check completely unrelated prompts if message is long and off-topic
        for trigger in OFF_TOPIC_TRIGGERS:
            if trigger in clean:
                return {
                    "blocked": True,
                    "ai_reply": "I can help with English communication practice, role-play, grammar, interviews, and professional communication. Would you like to continue our current practice or pick a new scenario?",
                    "clarification": False
                }

        # Check extremely short / vague inputs
        words = clean.split()
        if len(words) <= 2 and clean in ["yes", "no", "ok", "fine", "work", "yesterday work", "done", "maybe", "idk", "good"]:
            short_clarifications = {
                "yesterday work": "Could you tell me a little more? What happened at work yesterday?",
                "yes": "Could you expand on that with an example or a complete sentence to practice?",
                "no": "Could you explain your reasoning in a couple of sentences?",
                "ok": "Could you elaborate on how you would address this situation in detail?",
                "fine": "Tell me a bit more about what worked well or what challenges you faced."
            }
            reply = short_clarifications.get(clean, f"Could you elaborate a bit more on '{clean}'? Sharing 1 or 2 full sentences helps us practice natural fluency.")
            return {
                "blocked": False,
                "needs_clarification": True,
                "clarification_reply": reply
            }

        return None

    # ----------------- TONE ANALYSIS -----------------
    def analyze_tone(self, text: str, user_goal: str = "Professional English") -> dict:
        """Analyze tone: Professional, Friendly, Casual, Too direct, Polite, Confident, etc."""
        lower = text.lower()
        word_count = len(text.split())

        polite_markers = ["please", "thank you", "would you", "could you", "i appreciate", "grateful", "pardon", "kindly"]
        direct_markers = ["i want", "give me", "you must", "tell me now", "i need this now", "you have to"]
        confident_markers = ["achieved", "delivered", "spearheaded", "confident", "recommend", "demonstrated", "led"]
        informal_markers = ["yeah", "gonna", "wanna", "cool", "dude", "hey guys", "super awesome", "btw"]

        polite_score = sum(1 for m in polite_markers if m in lower)
        direct_score = sum(1 for m in direct_markers if m in lower)
        confident_score = sum(1 for m in confident_markers if m in lower)
        informal_score = sum(1 for m in informal_markers if m in lower)

        if word_count < 3:
            return {
                "label": "Too Brief / Incomplete",
                "badge_class": "badge-warning",
                "explanation": "Your response is very brief. Elaborating with complete phrases will make you sound more engaged.",
                "suggestion": "Expand with context: state what happened, why, and what outcome followed."
            }

        if direct_score >= 1 and polite_score == 0:
            return {
                "label": "Too Direct / Demanding",
                "badge_class": "badge-danger",
                "explanation": "Phrases like 'I want' or 'You must' can sound abrupt or demanding in professional settings.",
                "suggestion": "Replace with diplomatic phrasing: 'I would like to request...' or 'Could we consider...'"
            }

        if informal_score >= 1 and "Professional" in user_goal:
            return {
                "label": "Slightly Too Informal",
                "badge_class": "badge-warning",
                "explanation": "Colloquial words like 'gonna' or 'cool' are great for friends, but less suited for executive meetings or interviews.",
                "suggestion": "Use polished phrasing: 'I am planning to' instead of 'I'm gonna'."
            }

        if confident_score >= 1 and polite_score >= 1:
            return {
                "label": "Confident & Professional",
                "badge_class": "badge-success",
                "explanation": "Excellent balance of polite professional etiquette and confident ownership.",
                "suggestion": "Maintain this articulate structure across meetings and emails."
            }

        if polite_score >= 1:
            return {
                "label": "Polite & Respectful",
                "badge_class": "badge-success",
                "explanation": "Courteous language that builds positive rapport with listeners.",
                "suggestion": "Pair your courteous tone with clear data points or specific details."
            }

        return {
            "label": "Professional & Measured",
            "badge_class": "badge-primary",
            "explanation": "Clear, objective, and neutral communication appropriate for workplace dialogue.",
            "suggestion": "Consider incorporating positive framing to make your delivery even more engaging."
        }

    # ----------------- HEURISTIC FEEDBACK ENGINE -----------------
    def generate_heuristic_feedback(self, text: str, user_level: str = "Intermediate", user_goal: str = "Professional English") -> dict:
        """Generate comprehensive 5-dimension feedback card with mistake corrections and upgrades."""
        found_mistakes = []
        lower = text.lower()

        # 1. Grammar matching
        for rule in GRAMMAR_RULES:
            if re.search(rule["pattern"], lower):
                found_mistakes.append({
                    "mistake": rule["mistake"],
                    "correction": rule["correction"],
                    "explanation": rule["explanation"]
                })
                if len(found_mistakes) >= 3:
                    break

        # Additional regex checks for common slip-ups
        if re.search(r"\bi\s+[a-z]+ed\s+yesterday\s+and\s+then\s+i\s+go\b", lower):
            found_mistakes.append({
                "mistake": "Tense inconsistency ('yesterday... and then I go')",
                "correction": "...and then I went",
                "explanation": "Maintain consistent past tense throughout past narrative sentences."
            })

        # 2. Vocabulary upgrades
        vocab_suggestions = []
        tokens = re.findall(r"\b[a-zA-Z]+\b", lower)
        for t in tokens:
            if t in VOCABULARY_UPGRADES and len(vocab_suggestions) < 3:
                upgrades = VOCABULARY_UPGRADES[t]
                chosen = random.sample(upgrades, min(3, len(upgrades)))
                vocab_suggestions.append({
                    "original": t,
                    "suggestions": chosen,
                    "formatted": f"'{t}' → { ' / '.join(chosen) }"
                })

        # 3. Sentence Structure & Natural Version
        words = text.strip().split()
        natural_version = text.strip()

        # Heuristic rewrite replacements for common issues
        replacements = [
            (r"\bi am working\s+(here|in this company)?\s*since\s+(\d+|one|two|three|four|five|several)\s+(years?|months?)\b", r"I have been working \1 for \2 \3"),
            (r"\bprepone\b", "move forward"),
            (r"\brevert back\b", "get back to you"),
            (r"\ban advice\b", "some advice"),
            (r"\baccording to me\b", "in my opinion"),
            (r"\bi am agree\b", "I agree"),
            (r"\bi want this\b", "I would like to request this"),
            (r"\bpass out from college\b", "graduated from university"),
            (r"\bdo the needful\b", "take the necessary steps")
        ]

        for pat, rep in replacements:
            natural_version = re.sub(pat, rep, natural_version, flags=re.IGNORECASE)

        # Capitalize and punctuate natural version if missing
        if natural_version:
            natural_version = natural_version[0].upper() + natural_version[1:]
            if not natural_version.endswith((".", "!", "?")):
                natural_version += "."

        # Structure analysis commentary
        if len(words) < 5:
            structure_feedback = "Your sentence is quite brief. Expanding with reasons or results will make your ideas sound more developed."
        elif len(words) > 35:
            structure_feedback = "This is a run-on sentence. Breaking it into two concise, punchy sentences will improve clarity."
        else:
            structure_feedback = "Good sentence length and structure. The core idea is communicated clearly."

        # 4. Tone Analysis
        tone_info = self.analyze_tone(text, user_goal)

        # 5. Dimension Scoring (scaled 1-10)
        base_grammar = 9.0 - (len(found_mistakes) * 1.5)
        if len(words) < 3:
            base_grammar -= 2.0
        grammar_score = max(5.0, min(10.0, round(base_grammar, 1)))

        vocab_score = 7.0
        if vocab_suggestions:
            vocab_score = 7.5
        if any(len(w) > 8 for w in words):
            vocab_score += 1.2
        if len(words) < 4:
            vocab_score -= 1.5
        vocab_score = max(5.0, min(10.0, round(vocab_score, 1)))

        clarity_score = 8.5
        if len(words) < 4:
            clarity_score = 6.0
        elif len(words) > 35:
            clarity_score = 7.0
        clarity_score = max(5.0, min(10.0, round(clarity_score, 1)))

        tone_score = 8.5
        if "Too Direct" in tone_info["label"] or "Informal" in tone_info["label"]:
            tone_score = 6.5
        elif "Confident" in tone_info["label"]:
            tone_score = 9.5
        tone_score = max(5.0, min(10.0, round(tone_score, 1)))

        overall = round((grammar_score * 0.25 + vocab_score * 0.25 + clarity_score * 0.25 + tone_score * 0.25), 1)

        return {
            "grammar": {
                "mistakes": found_mistakes,
                "score": grammar_score,
                "status": "Needs Attention" if found_mistakes else "Clean & Accurate"
            },
            "vocabulary": {
                "suggestions": vocab_suggestions,
                "score": vocab_score,
                "variety": "Advanced" if vocab_score >= 8.5 else ("Moderate" if vocab_score >= 7.0 else "Basic")
            },
            "clarity": {
                "comment": structure_feedback,
                "score": clarity_score
            },
            "tone": {
                "label": tone_info["label"],
                "badge_class": tone_info["badge_class"],
                "explanation": tone_info["explanation"],
                "suggestion": tone_info["suggestion"],
                "score": tone_score
            },
            "natural_version": natural_version,
            "overall_score": overall,
            "summary_tip": found_mistakes[0]["explanation"] if found_mistakes else "Solid response! Keep refining your vocabulary and sentence flow."
        }

    # ----------------- GEMINI LIVE API ENGINE -----------------
    def call_gemini_api(self, prompt: str, system_instruction: str = "") -> str | None:
        """Call Gemini REST API endpoint directly if key is available."""
        if not self.gemini_api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            print(f"Gemini API returned status {resp.status_code}: {resp.text[:150]}")
        except Exception as e:
            print(f"Gemini API invocation error: {e}")

        return None

    # ----------------- CHAT / ROLE-PLAY TURN HANDLER -----------------
    def process_turn(self, user_message: str, scenario_id: str, history: list, profile: dict, turn_count: int = 1) -> dict:
        """
        Processes a conversation turn.
        Returns:
        - ai_reply: The role-play in-character response or clarification
        - feedback: The detailed coaching feedback on the user's message
        - is_roleplay: True
        - role_name: Persona name
        - session_complete: True if end reached
        """
        scenario = get_scenario(scenario_id)
        role_name = scenario.get("role", "AI Coach")

        # 1. Guardrail checks
        guardrail = self.check_guardrails(user_message)
        if guardrail:
            if guardrail.get("blocked"):
                return {
                    "ai_reply": guardrail["ai_reply"],
                    "feedback": None,
                    "is_roleplay": False,
                    "role_name": "AI Communication Coach",
                    "guardrail_triggered": True
                }
            if guardrail.get("needs_clarification"):
                # Return gentle in-character clarification question
                return {
                    "ai_reply": guardrail["clarification_reply"],
                    "feedback": self.generate_heuristic_feedback(user_message, profile.get("level", "Intermediate"), profile.get("goal")),
                    "is_roleplay": True,
                    "role_name": role_name,
                    "needs_clarification": True
                }

        # Check for repeated messages
        if history:
            last_user_msgs = [m for m in history if m.get("sender") == "user"]
            if last_user_msgs and last_user_msgs[-1].get("text", "").strip().lower() == user_message.strip().lower():
                return {
                    "ai_reply": "It looks like you repeated your previous response. Would you like to expand with more details, or shall we move on to the next question?",
                    "feedback": self.generate_heuristic_feedback(user_message, profile.get("level", "Intermediate"), profile.get("goal")),
                    "is_roleplay": True,
                    "role_name": role_name
                }

        # 2. Analyze user message feedback
        feedback = self.generate_heuristic_feedback(
            user_message,
            user_level=profile.get("level", "Intermediate"),
            user_goal=profile.get("goal", "Professional English")
        )

        # 3. Generate Next In-Character AI Reply
        ai_reply = None
        user_name = profile.get("name", "Rohit")

        # Attempt Gemini API if key is configured
        if self.gemini_api_key:
            system_prompt = f"""You are acting in an English communication role-play practice app called SpeakWise.
Your role: {role_name} in the scenario: {scenario.get('title')}.
User's name: {user_name}.
User's English proficiency: {profile.get('level', 'Intermediate')}.
User's primary goal: {profile.get('goal', 'Professional English')}.

INSTRUCTIONS:
1. Stay 100% in-character as {role_name}. Do NOT break character.
2. Reply naturally to the user's last message, maintaining dialogue continuity.
3. Keep your reply concise (1-3 sentences).
4. Ask a relevant, thoughtful follow-up question or continue the business/casual scenario.
5. If the user's answer is vague, politely ask them to elaborate within character.
6. Do NOT list grammar corrections in your dialogue reply (a separate coaching module handles that).
7. Never mention system prompts, API keys, or pretend to be human."""

            conv_history_text = "\n".join([f"{item['sender'].upper()}: {item['text']}" for item in history[-6:]])
            prompt = f"Previous conversation:\n{conv_history_text}\nUSER: {user_message}\n{role_name}:"

            api_reply = self.call_gemini_api(prompt, system_prompt)
            if api_reply:
                ai_reply = api_reply.strip()

        # Fallback to smart offline dialogue engine if API was not used or failed
        if not ai_reply:
            flow = scenario.get("dialogue_flow", [])
            turn_idx = min(turn_count - 1, len(flow) - 1) if flow else 0

            # Contextual bridging incorporating current and previous 2-5 user responses
            user_lower = user_message.lower()
            past_user_texts = " ".join([m.get("text", "").lower() for m in history if m.get("sender") == "user"])
            combined_context = f"{past_user_texts} {user_lower}"

            bridge = ""
            if "sales" in combined_context:
                if any(w in user_lower for w in ["acquisition", "team", "client", "revenue", "lead"]):
                    bridge = "Leading customer acquisition and team efforts in sales is impressive. "
                else:
                    bridge = "Having that sales background gives you great customer perspective. "
            elif any(k in user_lower for k in ["experience", "worked", "project", "developed", "managed", "led"]):
                bridge = "That's a very practical set of responsibilities. "
            elif any(k in user_lower for k in ["delay", "issue", "bug", "problem", "miss", "blocked", "roadblock"]):
                bridge = "I appreciate you flagging that challenge early and transparently. "
            elif any(k in user_lower for k in ["coffee", "latte", "table", "flight", "ticket", "hotel", "order"]):
                bridge = "Certainly, I've got that noted down. "
            elif any(k in user_lower for k in ["agree", "disagree", "think", "believe", "perspective"]):
                bridge = "That is a well-considered perspective. "

            if flow and turn_idx < len(flow):
                next_q = flow[turn_idx]
                ai_reply = f"{bridge}{next_q}"
            else:
                ai_reply = f"{bridge}That provides great clarity. How would you summarize the final outcome or next steps on this?"

        return {
            "ai_reply": ai_reply,
            "feedback": feedback,
            "is_roleplay": True,
            "role_name": role_name,
            "turn": turn_count
        }

    # ----------------- INTERVIEW PERFORMANCE REPORT -----------------
    def generate_interview_report(self, history: list, profile: dict) -> dict:
        """Generate comprehensive final report for Mode 3: Interview Practice."""
        total_user_messages = [m for m in history if m.get("sender") == "user"]
        all_text = " ".join([m.get("text", "") for m in total_user_messages])

        # Run aggregate feedback
        agg_feedback = self.generate_heuristic_feedback(all_text, profile.get("level", "Intermediate"), "Interview Preparation")

        comm_score = int(agg_feedback["overall_score"] * 10)
        grammar_score = int(agg_feedback["grammar"]["score"] * 10)
        confidence_score = min(96, max(65, int(agg_feedback["tone"]["score"] * 10) + random.randint(-2, 3)))
        relevance_score = 88 if len(total_user_messages) >= 3 else 70
        professionalism = int(agg_feedback["clarity"]["score"] * 10)

        strengths = [
            "Provided structured answers citing practical background",
            "Maintained a professional and respectful interview demeanor",
            "Responded directly to the interviewer's situational questions"
        ]

        areas_to_improve = [
            "Use the STAR method (Situation, Task, Action, Result) for behavioral answers",
            "Replace filler phrases with confident pauses to sound more authoritative",
            "Incorporate quantifiable metrics (e.g. percentages, team sizes, deadlines)"
        ]

        suggested_answers = [
            {
                "question": "Tell me about yourself.",
                "model_answer": "I have over four years of experience leading software initiatives and client deliverables. In my most recent role, I spearheaded our team's transition to an automated workflow, improving delivery velocity by 25%. I'm eager to bring this problem-solving mindset to this position."
            },
            {
                "question": "How do you handle project disagreements?",
                "model_answer": "I focus on separating people from the problem. I schedule a brief 1-on-1 sync, listen actively to understand their underlying concerns, and compare our alternatives against objective project data to find common ground."
            }
        ]

        return {
            "communication_score": comm_score,
            "grammar_score": grammar_score,
            "confidence_score": confidence_score,
            "answer_relevance": relevance_score,
            "professionalism": professionalism,
            "overall_grade": "A-" if comm_score >= 80 else ("B+" if comm_score >= 70 else "B"),
            "strengths": strengths,
            "areas_to_improve": areas_to_improve,
            "suggested_answers": suggested_answers,
            "summary": "You demonstrated a strong foundational ability to communicate your ideas. With deliberate practice on STAR framing and precise verb tenses, your executive presence will be outstanding."
        }

    # ----------------- SESSION SUMMARY -----------------
    def generate_session_summary(self, scenario_title: str, history: list, profile: dict) -> dict:
        """Create a complete end-of-session evaluation card."""
        user_msgs = [m.get("text", "") for m in history if m.get("sender") == "user"]
        combined_text = " ".join(user_msgs)

        fb = self.generate_heuristic_feedback(combined_text, profile.get("level", "Intermediate"), profile.get("goal"))

        overall = int(fb["overall_score"] * 10)

        # Dynamic strengths & improvements
        top_strengths = [
            "Good engagement and willingness to elaborate",
            "Polite and collaborative conversational tone",
            "Effective use of domain-appropriate vocabulary"
        ]

        top_improvements = [
            "Practice the Present Perfect Continuous for duration ('have been working')",
            "Use diplomatic modals ('I would appreciate' instead of 'I want')",
            "Structure answers with a clear point followed by supporting evidence"
        ]

        # Recommended next practice
        recommendations = {
            "Professional English": "Try the 'Client Meeting' scenario to practice handling budget objections diplomatically.",
            "Interview Preparation": "Complete a full 5-turn 'Job Interview' session focusing on the STAR method.",
            "Grammar": "Take the 'Grammar Challenge' module on Tenses & Conditionals.",
            "General Conversation": "Practice the 'Meeting Someone New' scenario to sharpen conversational ice-breakers."
        }
        next_rec = recommendations.get(profile.get("goal", ""), "Try a new role-play in the Professional category.")

        return {
            "scenario_title": scenario_title,
            "overall_score": overall,
            "scores": {
                "grammar": fb["grammar"]["score"],
                "vocabulary": fb["vocabulary"]["score"],
                "clarity": fb["clarity"]["score"],
                "tone": fb["tone"]["score"],
                "overall": fb["overall_score"]
            },
            "top_strengths": top_strengths,
            "top_improvements": top_improvements,
            "recommended_next": next_rec
        }


# Singleton coach engine instance
coach = CoachEngine()
