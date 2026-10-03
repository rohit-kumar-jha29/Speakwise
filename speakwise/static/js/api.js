/**
 * api.js - SpeakWise AI Client API Service Layer
 */

const API = {
  async getEngineStatus() {
    try {
      const res = await fetch("/api/engine/status");
      return await res.json();
    } catch (e) {
      return { mode: "Demo Mode (Simulated AI)", is_simulated: true, status: "offline" };
    }
  },

  async setEngineKey(apiKey, provider = "gemini") {
    const res = await fetch("/api/engine/key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey, provider })
    });
    return await res.json();
  },

  async getProfile() {
    const res = await fetch("/api/profile");
    return await res.json();
  },

  async updateProfile(profile) {
    const res = await fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile)
    });
    return await res.json();
  },

  async getDashboard() {
    const res = await fetch("/api/dashboard");
    return await res.json();
  },

  async getScenarios() {
    const res = await fetch("/api/scenarios");
    return await res.json();
  },

  async sendMessage(scenarioId, message, history, turnCount) {
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario_id: scenarioId,
          message: message,
          history: history,
          turn_count: turnCount
        })
      });
      return await res.json();
    } catch (e) {
      console.error("Chat error:", e);
      return {
        ai_reply: "I'm having trouble connecting right now. Please try again.",
        feedback: null,
        error_occurred: true,
        retry_available: true
      };
    }
  },

  async getFeedback(text) {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    return await res.json();
  },

  async completeSession(sessionData) {
    const res = await fetch("/api/sessions/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sessionData)
    });
    return await res.json();
  },

  async getSessions() {
    const res = await fetch("/api/sessions");
    return await res.json();
  },

  async getSessionById(sessionId) {
    const res = await fetch(`/api/sessions/${sessionId}`);
    return await res.json();
  },

  async getGrammarQuiz(level = "Intermediate") {
    const res = await fetch(`/api/grammar/quiz?level=${encodeURIComponent(level)}`);
    return await res.json();
  },

  async evaluateVocab(word, sentence) {
    const res = await fetch("/api/vocab/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ word, sentence })
    });
    return await res.json();
  },

  async resetData() {
    const res = await fetch("/api/reset", { method: "POST" });
    return await res.json();
  }
};
