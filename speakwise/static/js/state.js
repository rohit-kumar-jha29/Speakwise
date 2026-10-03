/**
 * state.js - SpeakWise AI Application State with Multi-Turn Session Restore
 */

const State = {
  activeView: "dashboard",
  profile: {
    name: "Rohit",
    level: "Intermediate",
    goal: "Professional English",
    avatar: "👨‍💼"
  },
  activeScenario: null,
  activeMode: "chat", // 'chat', 'roleplay', 'interview', 'demo_2min'
  history: [],
  turnCount: 0,
  
  // 2-Minute Demo Practice state
  demoMode: {
    active: false,
    maxTurns: 4,
    currentTurn: 0,
    startTime: null
  },

  // Audio / Speech
  speech: {
    recognition: null,
    isRecording: false,
    synth: window.speechSynthesis || null
  },

  lastUserMessage: "",

  init() {
    // 1. Theme
    try {
      const savedTheme = localStorage.getItem("speakwise_theme") || "dark";
      document.documentElement.setAttribute("data-theme", savedTheme);
    } catch (e) {}

    // 2. Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.speech.recognition = new SpeechRecognition();
      this.speech.recognition.continuous = false;
      this.speech.recognition.interimResults = false;
      this.speech.recognition.lang = "en-US";
    }

    // 3. Restore Active Session on page refresh
    this.restoreActiveSession();
  },

  saveActiveSession() {
    if (this.history.length === 0) return;
    try {
      const payload = {
        activeView: this.activeView,
        activeScenario: this.activeScenario,
        activeMode: this.activeMode,
        history: this.history,
        turnCount: this.turnCount,
        demoMode: this.demoMode,
        timestamp: Date.now()
      };
      localStorage.setItem("speakwise_active_session", JSON.stringify(payload));
    } catch (e) {}
  },

  restoreActiveSession() {
    try {
      const raw = localStorage.getItem("speakwise_active_session");
      if (!raw) return false;
      const data = JSON.parse(raw);
      // Only restore if within past 4 hours
      if (Date.now() - (data.timestamp || 0) < 4 * 60 * 60 * 1000) {
        this.activeScenario = data.activeScenario;
        this.activeMode = data.activeMode || "chat";
        this.history = data.history || [];
        this.turnCount = data.turnCount || 0;
        this.demoMode = data.demoMode || { active: false, maxTurns: 4, currentTurn: 0 };
        return true;
      }
    } catch (e) {}
    return false;
  },

  clearActiveSession() {
    this.history = [];
    this.turnCount = 0;
    this.demoMode.active = false;
    try {
      localStorage.removeItem("speakwise_active_session");
    } catch (e) {}
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem("speakwise_theme", next);
    } catch (e) {}
    return next;
  }
};
