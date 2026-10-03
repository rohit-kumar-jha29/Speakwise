/**
 * app.js - Master Application Controller for SpeakWise AI.
 */

const App = {
  scenarios: [],
  grammarQuizzes: [],
  currentQuizIdx: 0,

  async init() {
    State.init();
    this.bindEvents();

    // Load initial states
    await this.loadEngineStatus();
    await this.loadProfile();
    await this.loadDashboard();
    await this.loadScenarios();
    await this.loadGrammarQuiz();

    // Check if an active session was restored from page refresh
    if (State.history && State.history.length > 0) {
      this.restoreChatUI();
    } else {
      UI.switchView("dashboard");
    }
  },

  // ----------------- EVENT BINDINGS -----------------
  bindEvents() {
    // Sidebar Navigation
    document.querySelectorAll(".nav-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const view = btn.dataset.view;
        if (view === "dashboard") {
          UI.switchView("dashboard");
          this.loadDashboard();
        } else if (view === "chat") {
          this.startFreeConversation();
        } else if (view === "roleplay") {
          UI.switchView("roleplay");
        } else if (view === "interview") {
          UI.switchView("interview");
        } else if (view === "grammar") {
          UI.switchView("grammar");
          this.renderGrammarQuizItem();
        } else if (view === "vocab") {
          UI.switchView("vocab");
        } else if (view === "progress") {
          UI.switchView("progress");
          this.loadProgressCharts();
        } else if (view === "history") {
          UI.switchView("history");
          this.loadSessionHistory();
        }
      });
    });

    // Mobile menu toggle
    document.getElementById("btn-menu-toggle")?.addEventListener("click", () => {
      document.getElementById("sidebar")?.classList.toggle("mobile-open");
    });

    // Dark/Light Theme Toggle
    document.getElementById("btn-theme-toggle")?.addEventListener("click", () => {
      State.toggleTheme();
      this.loadDashboard();
    });

    // 2-Minute Practice Quick Demo Buttons
    document.querySelectorAll(".btn-quick-demo, #btn-dash-2min, #btn-top-2min").forEach(btn => {
      btn.addEventListener("click", () => this.startTwoMinutePractice());
    });

    // Dashboard Hero Buttons
    document.getElementById("btn-dash-start")?.addEventListener("click", () => this.startFreeConversation());
    document.getElementById("btn-dash-roleplay")?.addEventListener("click", () => UI.switchView("roleplay"));
    document.getElementById("btn-dash-interview")?.addEventListener("click", () => UI.switchView("interview"));

    // Chat Input & Send
    const chatInput = document.getElementById("chat-textarea");
    const sendBtn = document.getElementById("btn-send-message");

    chatInput?.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handleUserSend();
      }
    });

    sendBtn?.addEventListener("click", () => this.handleUserSend());

    // Speech-to-Text Microphone
    const micBtn = document.getElementById("btn-mic");
    if (micBtn && State.speech.recognition) {
      micBtn.addEventListener("click", () => this.toggleSpeechRecognition());
    }

    // Chat Quick Actions
    document.getElementById("btn-chat-feedback")?.addEventListener("click", () => this.requestManualFeedback());
    document.getElementById("btn-end-session")?.addEventListener("click", () => this.finishActiveSession());

    // Profile Settings Modal
    document.getElementById("user-profile-trigger")?.addEventListener("click", () => {
      this.openProfileModal();
    });
    document.getElementById("btn-save-profile")?.addEventListener("click", () => {
      this.saveProfileModal();
    });

    // API Key & Engine Config Modal
    document.getElementById("engine-status-pill")?.addEventListener("click", () => {
      UI.openModal("modal-api-settings");
    });
    document.getElementById("btn-save-api-key")?.addEventListener("click", async () => {
      const key = document.getElementById("input-api-key")?.value || "";
      const provider = document.getElementById("select-api-provider")?.value || "gemini";
      const res = await API.setEngineKey(key, provider);
      UI.showToast(res.message, "success");
      UI.closeModal("modal-api-settings");
      this.loadEngineStatus();
    });

    // Close Modal buttons
    document.querySelectorAll(".modal-close-btn, .modal-cancel-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        btn.closest(".modal-overlay")?.classList.remove("active");
      });
    });

    // Natural Version Actions
    document.getElementById("btn-listen-natural")?.addEventListener("click", () => {
      const text = document.getElementById("natural-version-text")?.textContent;
      if (text) UI.speakText(text.replace(/^"|"$/g, ''));
    });
    document.getElementById("btn-copy-natural")?.addEventListener("click", () => {
      const text = document.getElementById("natural-version-text")?.textContent;
      if (text) {
        navigator.clipboard.writeText(text.replace(/^"|"$/g, ''));
        UI.showToast("Copied to clipboard!", "success");
      }
    });

    // Reset Demo Data
    document.getElementById("btn-reset-demo")?.addEventListener("click", async () => {
      if (confirm("Reset SpeakWise AI to original demo data (12 historical sessions)?")) {
        await API.resetData();
        State.clearActiveSession();
        window.location.reload();
      }
    });

    // Vocabulary Evaluation
    document.getElementById("btn-eval-vocab")?.addEventListener("click", async () => {
      const input = document.getElementById("vocab-user-sentence")?.value.trim();
      const resBox = document.getElementById("vocab-result-box");
      if (!input) return;

      const evalRes = await API.evaluateVocab("persuade", input);
      if (resBox) {
        resBox.style.display = "block";
        resBox.innerHTML = `
          <div style="font-weight:700;font-size:1.05rem;color:var(--primary);margin-bottom:6px;">Score: ${evalRes.score}/10</div>
          <div style="font-size:0.9rem;margin-bottom:8px;">${escapeHTML(evalRes.feedback_comment)}</div>
          <div style="background:var(--bg-tertiary);padding:10px;border-radius:6px;font-size:0.85rem;line-height:1.4;">
            <strong>Professional Phrasing:</strong> "${escapeHTML(evalRes.professional_version)}"
          </div>
        `;
      }
    });

    // Interview Tracks Click Handling
    document.querySelectorAll("#interview-tracks-grid .hub-card").forEach(card => {
      card.addEventListener("click", () => {
        const track = card.dataset.track;
        this.startInterviewTrack(track);
      });
    });
  },

  // ----------------- LOAD ENGINE STATUS -----------------
  async loadEngineStatus() {
    const status = await API.getEngineStatus();
    const ind = document.getElementById("engine-status-indicator");
    const pill = document.getElementById("engine-status-text");
    const dot = document.getElementById("status-dot");

    if (status.is_simulated) {
      if (ind) {
        ind.className = "engine-demo-badge";
        ind.innerHTML = "🟡 Demo Mode (Simulated AI)";
        ind.title = "Simulated AI responses active. Add API key to switch to Real AI.";
      }
      if (pill) pill.textContent = "Demo Mode";
      if (dot) dot.style.background = "var(--warning)";
    } else {
      if (ind) {
        ind.className = "engine-online-badge";
        ind.innerHTML = "🟢 AI Coach Online";
      }
      if (pill) pill.textContent = "Real AI Mode";
      if (dot) dot.style.background = "var(--success)";
    }
  },

  // ----------------- USER PROFILE -----------------
  async loadProfile() {
    try {
      const prof = await API.getProfile();
      State.profile = prof;
      this.updateProfileUI();
    } catch (e) {
      this.updateProfileUI();
    }
  },

  updateProfileUI() {
    document.querySelectorAll(".user-name-display").forEach(el => el.textContent = State.profile.name);
    document.querySelectorAll(".user-meta-display").forEach(el => el.textContent = `${State.profile.level} • ${State.profile.goal}`);
    document.querySelectorAll(".user-avatar-display").forEach(el => el.textContent = State.profile.avatar || "👨‍💼");
  },

  openProfileModal() {
    const nameIn = document.getElementById("input-profile-name");
    const levelIn = document.getElementById("select-profile-level");
    const goalIn = document.getElementById("select-profile-goal");

    if (nameIn) nameIn.value = State.profile.name;
    if (levelIn) levelIn.value = State.profile.level;
    if (goalIn) goalIn.value = State.profile.goal;

    UI.openModal("modal-profile");
  },

  async saveProfileModal() {
    const name = document.getElementById("input-profile-name")?.value.trim() || "Rohit";
    const level = document.getElementById("select-profile-level")?.value || "Intermediate";
    const goal = document.getElementById("select-profile-goal")?.value || "Professional English";

    State.profile.name = name;
    State.profile.level = level;
    State.profile.goal = goal;

    await API.updateProfile(State.profile);
    this.updateProfileUI();
    UI.closeModal("modal-profile");
    UI.showToast("Profile updated successfully!", "success");
  },

  // ----------------- DASHBOARD -----------------
  async loadDashboard() {
    const data = await API.getDashboard();
    const fill = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    fill("dash-sessions-completed", data.sessions_completed || 12);
    fill("dash-average-score", `${data.average_score || 76}%`);
    fill("dash-practice-time", data.practice_time_str || "3h 42m");
    fill("dash-streak", `${data.current_streak || 5} days 🔥`);

    // Skill breakdown
    const skills = data.skills || { grammar: 72, vocabulary: 81, clarity: 78, tone: 85, confidence: 74 };
    const updateSkill = (name, val) => {
      const txt = document.getElementById(`skill-${name}-val`);
      const bar = document.getElementById(`skill-${name}-bar`);
      if (txt) txt.textContent = `${val}%`;
      if (bar) bar.style.width = `${val}%`;
    };
    updateSkill("grammar", skills.grammar);
    updateSkill("vocab", skills.vocabulary);
    updateSkill("clarity", skills.clarity);
    updateSkill("tone", skills.tone);
    updateSkill("conf", skills.confidence);

    // Chart trend
    if (data.trend && data.trend.length) {
      Charts.renderTrendChart("chart-trend", data.trend);
    }
  },

  async loadProgressCharts() {
    const data = await API.getDashboard();
    if (data.trend && data.trend.length) {
      Charts.renderTrendChart("chart-progress-trend", data.trend);
    }
    Charts.renderRadarChart("chart-progress-radar", {
      avg_grammar: data.skills?.grammar,
      avg_vocab: data.skills?.vocabulary,
      avg_clarity: data.skills?.clarity,
      avg_tone: data.skills?.tone,
      avg_overall: data.average_score
    });
  },

  // ----------------- SCENARIOS & ROLE PLAY -----------------
  async loadScenarios() {
    const data = await API.getScenarios();
    this.scenarios = data.all || [];
    this.renderRolePlayCards(this.scenarios);
  },

  renderRolePlayCards(list) {
    const container = document.getElementById("roleplay-scenarios-grid");
    if (!container) return;

    // Filter to Section 4 scenarios
    const required13 = [
      "job_interview", "hr_interview", "client_meeting", "manager_conversation",
      "team_meeting", "sales_call", "customer_complaint", "networking",
      "presentation", "asking_for_leave", "salary_negotiation", "college_viva", "group_discussion"
    ];

    const cards = list.filter(s => required13.includes(s.id));

    container.innerHTML = cards.map(s => `
      <div class="scenario-select-card" data-id="${s.id}">
        <div class="card-top-row">
          <span style="font-size:1.4rem;">${s.badge || "💼"}</span>
          <span class="difficulty-tag diff-intermediate">Interactive</span>
        </div>
        <h3 style="font-size:1.05rem;font-weight:700;">${escapeHTML(s.title)}</h3>
        <div style="font-size:0.75rem;color:var(--secondary);font-weight:600;">Role: ${escapeHTML(s.role)}</div>
        <p class="hub-card-desc">${escapeHTML(s.description)}</p>
        <div class="hub-card-footer">
          <span>Start Role Play</span>
          <span>→</span>
        </div>
      </div>
    `).join("");

    container.querySelectorAll(".scenario-select-card").forEach(card => {
      card.addEventListener("click", () => {
        const id = card.dataset.id;
        const scen = this.scenarios.find(s => s.id === id);
        if (scen) this.startRolePlay(scen);
      });
    });
  },

  // ----------------- START MODES -----------------
  startFreeConversation() {
    const scen = {
      id: "free_conversation",
      title: "AI Practice",
      role: "AI Communication Coach",
      coach_tip: "Speak naturally. Share thoughts, plans, or questions.",
      starter_message: "Hi! I'm your AI communication coach. What would you like to practice today?"
    };
    State.activeScenario = scen;
    State.activeMode = "chat";
    State.history = [];
    State.turnCount = 1;
    State.demoMode.active = false;

    this.setupChatUI(scen.title, scen.role, scen.coach_tip);
    UI.switchView("chat");
    UI.clearChat();

    State.history.push({ sender: "ai", text: scen.starter_message });
    UI.appendMessage("ai", scen.starter_message, scen.role);
    State.saveActiveSession();
  },

  startRolePlay(scenario) {
    const diff = document.getElementById("roleplay-difficulty-select")?.value || "Intermediate";
    State.activeScenario = scenario;
    State.activeMode = "roleplay";
    State.history = [];
    State.turnCount = 1;
    State.demoMode.active = false;

    this.setupChatUI(scenario.title, scenario.role, `Role-play mode (${diff}). AI remains in character.`);
    UI.switchView("chat");
    UI.clearChat();

    const starter = scenario.starter_message.replace(/Rohit/g, State.profile.name);
    State.history.push({ sender: "ai", text: starter });
    UI.appendMessage("ai", starter, scenario.role);
    State.saveActiveSession();
  },

  startInterviewTrack(track) {
    const trackMap = {
      "HR": "interview_hr",
      "Business Analyst": "interview_ba",
      "Marketing": "interview_marketing",
      "Sales": "interview_sales",
      "Data Analytics": "interview_data",
      "General Management": "interview_management"
    };
    const scenId = trackMap[track] || "interview_hr";
    const scen = this.scenarios.find(s => s.id === scenId) || this.scenarios[0];

    State.activeScenario = scen;
    State.activeMode = "interview";
    State.history = [];
    State.turnCount = 1;
    State.demoMode.active = false;

    this.setupChatUI(`${track} Interview`, scen.role, scen.coach_tip);
    UI.switchView("chat");
    UI.clearChat();

    const starter = scen.starter_message.replace(/Rohit/g, State.profile.name);
    State.history.push({ sender: "ai", text: starter });
    UI.appendMessage("ai", starter, scen.role);
    State.saveActiveSession();
  },

  startTwoMinutePractice() {
    const demoScenario = {
      id: "job_interview",
      title: "2-Minute Practice (Job Interview)",
      role: "Executive Recruiter (Sarah Vance)",
      coach_tip: "Fast 4-turn interview demonstration. Deliver crisp answers to receive live evaluation!",
      starter_message: `Good morning ${State.profile.name}. Welcome to your 2-minute interview practice session. Tell me about your background and core strength.`
    };

    State.activeScenario = demoScenario;
    State.activeMode = "demo_2min";
    State.history = [];
    State.turnCount = 1;
    State.demoMode = {
      active: true,
      maxTurns: 4,
      currentTurn: 0,
      startTime: Date.now()
    };

    this.setupChatUI("⚡ 2-Minute Practice Challenge", demoScenario.role, demoScenario.coach_tip, true);
    UI.switchView("chat");
    UI.clearChat();
    this.updateDemoProgressBar(0);

    State.history.push({ sender: "ai", text: demoScenario.starter_message });
    UI.appendMessage("ai", demoScenario.starter_message, demoScenario.role);
    State.saveActiveSession();

    UI.showToast("2-Minute Practice started! 4 turns to final evaluation.", "info");
  },

  updateDemoProgressBar(turn) {
    const fill = document.getElementById("demo-progress-fill");
    const label = document.getElementById("demo-turn-label");
    const max = State.demoMode.maxTurns || 4;
    const pct = Math.min(100, Math.round((turn / max) * 100));

    if (fill) fill.style.width = `${Math.max(10, pct)}%`;
    if (label) label.textContent = `Turn ${turn}/${max}`;
  },

  setupChatUI(title, role, tip, isDemo = false) {
    const titleEl = document.getElementById("chat-scenario-title");
    const roleEl = document.getElementById("chat-scenario-role");
    const tipEl = document.getElementById("chat-scenario-tip");
    const demoBar = document.getElementById("demo-progress-container");

    if (titleEl) titleEl.textContent = title;
    if (roleEl) roleEl.textContent = role;
    if (tipEl) tipEl.textContent = tip;
    if (demoBar) demoBar.style.display = isDemo ? "flex" : "none";
  },

  restoreChatUI() {
    if (!State.activeScenario) return;
    this.setupChatUI(
      State.activeScenario.title,
      State.activeScenario.role,
      State.activeScenario.coach_tip,
      State.demoMode?.active
    );
    UI.switchView("chat");
    UI.clearChat();

    State.history.forEach(m => {
      UI.appendMessage(m.sender, m.text, State.activeScenario.role);
    });

    if (State.demoMode?.active) {
      this.updateDemoProgressBar(State.demoMode.currentTurn);
    }
  },

  // ----------------- USER MESSAGE HANDLING -----------------
  async handleUserSend() {
    const input = document.getElementById("chat-textarea");
    if (!input) return;
    const message = input.value.trim();

    if (!message) {
      UI.showToast("Please enter a message so we can continue practicing.", "warning");
      input.focus();
      return;
    }

    input.value = "";
    input.style.height = "auto";
    State.lastUserMessage = message;

    // Append to UI
    UI.appendMessage("user", message);
    State.history.push({
      sender: "user",
      text: message,
      timestamp: new Date().toISOString()
    });
    State.saveActiveSession();

    if (State.demoMode.active) {
      State.demoMode.currentTurn += 1;
      this.updateDemoProgressBar(State.demoMode.currentTurn);
    }

    UI.showTyping(true);

    try {
      const response = await API.sendMessage(
        State.activeScenario?.id || "free_conversation",
        message,
        State.history,
        State.turnCount
      );

      UI.showTyping(false);

      if (response.feedback) {
        UI.updateFeedbackPanel(response.feedback);
      }

      const roleName = response.role_name || State.activeScenario?.role || "AI Coach";
      UI.appendMessage("ai", response.ai_reply, roleName);
      State.history.push({
        sender: "ai",
        text: response.ai_reply,
        timestamp: new Date().toISOString()
      });

      State.turnCount += 1;
      State.saveActiveSession();

      // Check if 2-Minute practice reached maximum turns
      if (State.demoMode.active && State.demoMode.currentTurn >= State.demoMode.maxTurns) {
        setTimeout(() => {
          this.finishActiveSession();
        }, 1200);
      }
    } catch (e) {
      UI.showTyping(false);
      UI.appendMessage("ai", "I'm having trouble connecting right now. Please try again.", "AI Coach");
    }
  },

  async requestManualFeedback() {
    if (!State.lastUserMessage) {
      UI.showToast("Please type a response first to receive feedback.", "warning");
      return;
    }
    const fb = await API.getFeedback(State.lastUserMessage);
    UI.updateFeedbackPanel(fb);
    UI.showToast("Live Performance updated!", "success");
  },

  async finishActiveSession() {
    if (State.history.length <= 1) {
      UI.showToast("Practice at least 1 turn before completing the session.", "warning");
      return;
    }

    const durationMins = State.demoMode.active ? 2 : Math.max(2, Math.round(State.history.length * 1.5));

    const result = await API.completeSession({
      scenario_id: State.activeScenario?.id || "free_conversation",
      scenario_title: State.activeScenario?.title || "AI Practice",
      role: State.activeScenario?.role || "AI Coach",
      mode: State.activeMode,
      history: State.history,
      duration_minutes: durationMins
    });

    if (result.success) {
      State.clearActiveSession();
      UI.renderSessionSummaryModal(result.report, result.session);
      await this.loadDashboard();
    }
  },

  // ----------------- SPEECH-TO-TEXT -----------------
  toggleSpeechRecognition() {
    const micBtn = document.getElementById("btn-mic");
    const chatInput = document.getElementById("chat-textarea");

    if (State.speech.isRecording) {
      State.speech.recognition.stop();
      State.speech.isRecording = false;
      micBtn?.classList.remove("recording");
    } else {
      try {
        State.speech.recognition.start();
        State.speech.isRecording = true;
        micBtn?.classList.add("recording");
        UI.showToast("Listening... Speak clearly into your mic.", "info");

        State.speech.recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          if (chatInput) {
            chatInput.value = transcript;
            chatInput.focus();
          }
          State.speech.recognition.stop();
          State.speech.isRecording = false;
          micBtn?.classList.remove("recording");
        };

        State.speech.recognition.onerror = () => {
          State.speech.isRecording = false;
          micBtn?.classList.remove("recording");
        };

        State.speech.recognition.onend = () => {
          State.speech.isRecording = false;
          micBtn?.classList.remove("recording");
        };
      } catch (e) {
        State.speech.isRecording = false;
        micBtn?.classList.remove("recording");
      }
    }
  },

  // ----------------- GRAMMAR PRACTICE QUIZ -----------------
  async loadGrammarQuiz() {
    this.grammarQuizzes = await API.getGrammarQuiz(State.profile.level);
    this.currentQuizIdx = 0;
  },

  renderGrammarQuizItem() {
    if (!this.grammarQuizzes.length) return;
    const q = this.grammarQuizzes[this.currentQuizIdx];

    const countEl = document.getElementById("grammar-quiz-count");
    const qEl = document.getElementById("grammar-quiz-question");
    const optContainer = document.getElementById("grammar-options-container");
    const resBox = document.getElementById("grammar-quiz-result");

    if (countEl) countEl.textContent = `Question ${this.currentQuizIdx + 1} of ${this.grammarQuizzes.length}`;
    if (qEl) qEl.textContent = q.question;
    if (resBox) resBox.style.display = "none";

    if (optContainer) {
      optContainer.innerHTML = q.options.map((opt, i) => {
        const letter = opt.trim().substring(0, 1);
        return `
          <button class="btn-secondary grammar-opt-btn" data-letter="${letter}" style="text-align:left;padding:12px 18px;font-size:0.95rem;">
            ${escapeHTML(opt)}
          </button>
        `;
      }).join("");

      optContainer.querySelectorAll(".grammar-opt-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const selected = btn.dataset.letter;
          const isCorrect = selected === q.correct_option;
          if (resBox) {
            resBox.style.display = "block";
            resBox.innerHTML = `
              <div style="font-weight:700;font-size:1.05rem;color:${isCorrect ? "var(--success)" : "var(--danger)"};margin-bottom:6px;">
                ${isCorrect ? "🎉 Correct!" : `💡 Not quite. The correct answer is Option ${q.correct_option}.`}
              </div>
              <div style="font-size:0.875rem;color:var(--text-muted);line-height:1.5;">${escapeHTML(q.explanation)}</div>
            `;
          }
        });
      });
    }

    document.getElementById("btn-next-grammar-quiz")?.replaceWith(
      document.getElementById("btn-next-grammar-quiz").cloneNode(true)
    );
    document.getElementById("btn-next-grammar-quiz")?.addEventListener("click", () => {
      this.currentQuizIdx = (this.currentQuizIdx + 1) % this.grammarQuizzes.length;
      this.renderGrammarQuizItem();
    });
  },

  // ----------------- SESSION HISTORY -----------------
  async loadSessionHistory() {
    const sessions = await API.getSessions();
    const tbody = document.getElementById("history-table-body");
    if (!tbody) return;

    if (!sessions.length) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;color:var(--text-muted);">No sessions recorded yet. Start practicing above!</td></tr>`;
      return;
    }

    tbody.innerHTML = [...sessions].reverse().map(s => `
      <tr>
        <td><strong>${escapeHTML(s.date)}</strong></td>
        <td><span class="difficulty-tag diff-beginner">${escapeHTML(s.mode)}</span></td>
        <td><strong>${escapeHTML(s.scenario_title)}</strong></td>
        <td><span style="font-weight:800;color:var(--primary);">${s.score_overall}/100</span></td>
        <td style="max-width:240px;color:var(--text-muted);">${escapeHTML(s.key_improvement || "General practice")}</td>
        <td>
          <button class="btn-chat-action btn-review-session" data-id="${s.id}">Review</button>
        </td>
      </tr>
    `).join("");

    tbody.querySelectorAll(".btn-review-session").forEach(btn => {
      btn.addEventListener("click", async () => {
        const sess = await API.getSessionById(btn.dataset.id);
        if (sess) this.openSessionReviewModal(sess);
      });
    });
  },

  openSessionReviewModal(session) {
    const titleEl = document.getElementById("review-modal-title");
    const metaEl = document.getElementById("review-modal-meta");
    const transcriptEl = document.getElementById("review-modal-transcript");

    if (titleEl) titleEl.textContent = session.scenario_title;
    if (metaEl) metaEl.textContent = `Date: ${session.date} • Duration: ${session.duration_minutes}m • Score: ${session.score_overall}/100`;

    if (transcriptEl) {
      transcriptEl.innerHTML = (session.transcript || []).map(m => `
        <div style="margin-bottom:12px;padding:10px 14px;border-radius:8px;background:${m.sender === "user" ? "var(--primary-light)" : "var(--bg-tertiary)"};">
          <div style="font-weight:700;font-size:0.75rem;margin-bottom:4px;color:${m.sender === "user" ? "var(--primary)" : "var(--secondary)"};">
            ${m.sender === "user" ? State.profile.name : (session.role || "AI Coach")}
          </div>
          <div style="font-size:0.875rem;">${escapeHTML(m.text)}</div>
        </div>
      `).join("");
    }

    UI.openModal("modal-review-session");
  }
};

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
