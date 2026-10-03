# SpeakWise AI – Language & Soft-Skills Practice Chatbot 🎙️

**SpeakWise AI** is an end-to-end, fully functional, production-grade AI conversational practice platform and personal English communication coach. It is built to simulate realistic workplace, everyday, and academic conversations, analyze grammar, tone, vocabulary, and sentence formation in real-time, and track long-term progress with persistent multi-session storage.

> **Tagline**: *Practice. Speak. Improve.*  
> **Description**: *An AI-powered communication coach for improving English, grammar, professional communication and interview skills through realistic conversations.*

---

## 🌟 Key Highlights & Architectural Features

### 1. Dual AI Engine Architecture
- **Real AI Mode (Live LLM API)**: Configurable through environment variables (`AI_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY`) or in-app via the top header modal. Seamlessly connects with Google Gemini 1.5 Flash or OpenAI endpoints.
- **Demo Mode (Simulated AI)**: When no API key is provided, the application runs on a high-fidelity dynamic conversational engine with multi-turn context memory, intelligent keyword bridging, and ESL/business heuristic feedback. It is transparently labeled in the UI as `🟡 Demo Mode (Simulated AI)`.

### 2. Multi-Turn Conversation Memory & Session Restore
- Maintains full conversation context across turns (e.g., following up on previous mentions of EdTech, sales, or team management).
- **Session State Persistence**: If the user refreshes during an active session, the chat history, turns, and scenario state are restored without resetting.

### 3. Role-Play Module (13 Scenarios)
- **Scenarios**: Job Interview, HR Interview, Client Meeting, Manager Conversation, Team Meeting, Sales Call, Customer Complaint, Networking, Presentation, Asking for Leave, Salary Negotiation, College Viva, Group Discussion.
- **Difficulty Selection**: Beginner, Intermediate, Advanced.
- **In-Character Execution**: AI stays 100% in character and does not interrupt the conversation with corrections during the simulation.
- **End Session Report**: Generates a comprehensive Communication Report (Overall Score /100, Grammar /10, Vocabulary /10, Clarity /10, Professional Tone /10, Confidence /10).

### 4. 3-Tier Natural English Improvement & Tone Analysis
- **Your Response**: The original user input.
- **More Natural**: How a fluent native speaker would naturally say it.
- **Professional Version**: How the same thought can be elevated for an executive workplace or interview setting.
- **Tone Analysis**: Labels communication tone (*Professional & Measured, Confident, Polite, Too Direct, Informal*) and provides actionable diplomatic alternatives.

### 5. Dedicated Practice Tracks
- **AI Practice (Free Conversation)**: AI initiates with natural conversational openers and adapts to user replies.
- **Interview Practice**: 6 tracks (*HR, Business Analyst, Marketing, Sales, Data Analytics, General Management*), asking one question at a time and evaluating responses.
- **Grammar Practice**: Interactive multiple-choice sentence correction exercises with detailed grammatical rule explanations.
- **Vocabulary Practice**: Word challenges (e.g. *Persuade*) where users construct sentences and receive context, grammar, and naturalness evaluations.
- **⚡ Start 2-Minute Practice**: Instant 4-turn express job interview simulation with a live progress bar (`Turn 1/4` → `Turn 4/4`), automated final scoring, and dashboard update.

### 6. SQLite Database & Live Dashboard
- **Backend Persistence**: Uses SQLite (`speakwise.db`) for storing users, practice sessions, transcripts, and feedback history.
- **Pre-Seeded Demo History**: Pre-loaded with 12 completed sessions for user **Rohit** showing an upward score trajectory (62 → 82), 76% average score, 3h 42m speaking time, and 5-day streak.
- **Interactive Visualizations**: Real Chart.js line charts tracking score trends and competency breakdowns (Grammar 72%, Vocabulary 81%, Clarity 78%, Tone 85%, Confidence 74%).
- **Session History Table**: Review past sessions, complete with full transcript dialogs and recommendations.

### 7. Voice Input (STT) & Speech Playback (TTS)
- **Speech-to-Text (STT)**: Microphone button using the browser's Web Speech API.
- **Text-to-Speech (TTS)**: Listen to any AI response or natural phrasing with natural vocal inflection.

---

## 📁 Project Directory Structure

```text
speakwise/
├── app.py                  # Main Flask application and REST API endpoints
├── database.py             # SQLite persistence layer and data seed routines
├── ai_service.py           # Modular AI Service Layer (Live LLM & Demo Mode engines)
├── scenarios.py            # Definitions for 13 role-play scenarios & interview tracks
├── challenges.py           # Practice datasets for Grammar, Vocab, and Situations
├── test_app.py             # Automated unit test suite (15 test cases)
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── README.md               # Documentation
└── static/
    ├── index.html          # Semantic HTML5 layout with sidebar, hub, chat, and modals
    ├── css/
    │   └── styles.css      # Premium dark/light design system with glassmorphism
    └── js/
        ├── api.js          # REST API client
        ├── state.js        # State manager with multi-turn session restore
        ├── charts.js       # Chart.js renderers (Line trend & Skill radar)
        ├── ui.js           # DOM manipulation, TTS/STT, and modal helpers
        └── app.js          # Master controller wiring all modes and events
```

---

## 🚀 Quickstart & Setup

### 1. Requirements
- Python 3.10+
- Modern Web Browser (Google Chrome, Microsoft Edge, Firefox, Safari)

### 2. Installation & Server Start
Navigate to the project directory:
```bash
cd C:\Users\asus\.gemini\antigravity\scratch\speakwise

# Install dependencies
python -m pip install -r requirements.txt

# Start the SpeakWise AI server
python app.py
```

### 3. Open in Browser
Visit:
```
http://127.0.0.1:5000
```

---

## 🧪 Automated Test Verification

SpeakWise AI includes an automated test suite verifying all 38 requirements:
```bash
python test_app.py
```
Output:
```text
...............
----------------------------------------------------------------------
Ran 15 tests in 0.514s

OK
```

### Test Cases Covered:
1. SQLite seed and dashboard statistics (12 sessions, 76% avg, Rohit profile)
2. Demo Mode status and simulated AI indicators
3. Real AI Mode automatic switching with API key
4. Scenarios catalog (13 Section 4 scenarios + 6 interview tracks)
5. Normal conversation flow (User → Chat → AI)
6. Multi-turn memory and context retention
7. In-character role-play without mid-dialogue interruptions
8. Grammar analysis (Original, Improved, Explanation)
9. 3-Tier phrasing improvement (Your Response, More Natural, Professional Version)
10. Tone analysis and diplomatic suggestions
11. Vague answer clarification handling
12. Off-topic redirection handling
13. Prompt injection and adversarial input protection
14. Empty message validation
15. Session completion and SQLite persistence
