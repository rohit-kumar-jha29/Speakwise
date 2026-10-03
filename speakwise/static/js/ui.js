/**
 * ui.js - DOM Renderers, Speech & Modal Controllers for SpeakWise AI.
 */

const UI = {
  // ----------------- TOAST NOTIFICATIONS -----------------
  showToast(message, type = "info") {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.style.cssText = "position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:9999;display:flex;flex-direction:column;gap:8px;";
      document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    const colors = {
      info: "background:#1e293b;color:#f8fafc;border:1px solid #4f46e5;",
      success: "background:#064e3b;color:#a7f3d0;border:1px solid #10b981;",
      warning: "background:#78350f;color:#fde68a;border:1px solid #f59e0b;",
      danger: "background:#7f1d1d;color:#fecaca;border:1px solid #ef4444;"
    };
    toast.style.cssText = `${colors[type] || colors.info}padding:10px 18px;border-radius:10px;font-size:0.85rem;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.4);animation:fadeIn 0.2s ease;`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  },

  // ----------------- VIEW SWITCHER -----------------
  switchView(viewName) {
    document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
    const target = document.getElementById(`view-${viewName}`);
    if (target) {
      target.classList.add("active");
    }
    document.querySelectorAll(".nav-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.view === viewName);
    });
    State.activeView = viewName;

    // Mobile sidebar auto-close
    const sidebar = document.getElementById("sidebar");
    if (sidebar) sidebar.classList.remove("mobile-open");
  },

  // ----------------- CHAT RENDERING -----------------
  appendMessage(sender, text, roleName = "AI Coach") {
    const container = document.getElementById("messages-container");
    const emptyState = document.getElementById("chat-empty-state");
    if (emptyState) emptyState.style.display = "none";
    if (!container) return;

    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const isUser = sender === "user";
    const avatar = isUser ? State.profile.avatar || "👨‍💼" : "🤖";
    const displayName = isUser ? State.profile.name : roleName;

    row.innerHTML = `
      <div class="msg-avatar">${avatar}</div>
      <div class="msg-body">
        <div class="msg-header">
          <strong>${displayName}</strong>
          <span>${now}</span>
        </div>
        <div class="msg-bubble">${escapeHTML(text)}</div>
        ${!isUser ? `
          <div class="msg-tools">
            <button class="msg-tool-btn btn-speak" title="Listen with Audio">🔊 Listen</button>
            <button class="msg-tool-btn btn-copy" title="Copy text">📋 Copy</button>
          </div>
        ` : `
          <div class="msg-tools">
            <button class="msg-tool-btn btn-resend" title="Try Again with this input">🔄 Resend</button>
          </div>
        `}
      </div>
    `;

    if (!isUser) {
      row.querySelector(".btn-speak")?.addEventListener("click", () => UI.speakText(text));
      row.querySelector(".btn-copy")?.addEventListener("click", () => {
        navigator.clipboard.writeText(text);
        UI.showToast("Copied to clipboard!", "success");
      });
    } else {
      row.querySelector(".btn-resend")?.addEventListener("click", () => {
        const input = document.getElementById("chat-textarea");
        if (input) {
          input.value = text;
          input.focus();
        }
      });
    }

    container.appendChild(row);
    container.scrollTop = container.scrollHeight;
  },

  showTyping(show = true) {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) {
      indicator.style.display = show ? "flex" : "none";
      const container = document.getElementById("messages-container");
      if (show && container) container.scrollTop = container.scrollHeight;
    }
  },

  clearChat() {
    const container = document.getElementById("messages-container");
    if (container) container.innerHTML = "";
    const emptyState = document.getElementById("chat-empty-state");
    if (emptyState) emptyState.style.display = "block";
  },

  // ----------------- LIVE FEEDBACK PANEL -----------------
  updateFeedbackPanel(feedback) {
    if (!feedback) return;

    // Overall score
    const scoreVal = document.getElementById("feedback-overall-score");
    if (scoreVal) {
      const val = feedback.overall_100 || Math.round((feedback.score || 7.8) * 10);
      scoreVal.textContent = `${val}/100`;
    }

    // Progress bars (1-10 mapped to percentage)
    const updateBar = (id, score) => {
      const el = document.getElementById(id);
      const textEl = document.getElementById(`${id}-val`);
      const val = score || 7;
      if (el) el.style.width = `${Math.min(100, Math.max(10, val * 10))}%`;
      if (textEl) textEl.textContent = `${val}/10`;
    };

    updateBar("bar-grammar", feedback.grammar?.score);
    updateBar("bar-vocab", feedback.vocabulary?.score);
    updateBar("bar-clarity", feedback.clarity?.score);
    updateBar("bar-tone", feedback.tone?.score);

    // Grammar Corrections
    const mistakesContainer = document.getElementById("grammar-corrections-list");
    if (mistakesContainer) {
      const errors = feedback.grammar?.errors || [];
      if (errors.length === 0) {
        mistakesContainer.innerHTML = `
          <div style="font-size:0.8rem;color:var(--success);display:flex;align-items:center;gap:6px;">
            <span>✅</span> No major grammatical errors detected!
          </div>
        `;
      } else {
        mistakesContainer.innerHTML = errors.slice(0, 3).map(e => `
          <div class="diff-item">
            <div class="diff-wrong">❌ Original: "${escapeHTML(e.original)}"</div>
            <div class="diff-correct">✅ Improved: "${escapeHTML(e.improved)}"</div>
            <div class="diff-note">${escapeHTML(e.explanation)}</div>
          </div>
        `).join("");
      }
    }

    // Natural English Improvement (Your Response, More Natural, Professional Version)
    const userRespBox = document.getElementById("box-user-response");
    const natQuote = document.getElementById("natural-version-text");
    const profQuote = document.getElementById("professional-version-text");

    if (userRespBox && feedback.original_response) {
      userRespBox.textContent = `"${feedback.original_response}"`;
    }
    if (natQuote && feedback.natural_version) {
      natQuote.textContent = `"${feedback.natural_version}"`;
    }
    if (profQuote && feedback.professional_version) {
      profQuote.textContent = `"${feedback.professional_version}"`;
    }

    // Tone Card
    const toneBadge = document.getElementById("tone-badge");
    const toneExp = document.getElementById("tone-explanation");
    const toneSugg = document.getElementById("tone-suggestion");
    if (toneBadge && feedback.tone) {
      toneBadge.textContent = feedback.tone.label;
      toneBadge.className = `tone-badge ${feedback.tone.badge_class || "badge-primary"}`;
    }
    if (toneExp && feedback.tone) toneExp.textContent = feedback.tone.explanation || "Clear and objective delivery.";
    if (toneSugg && feedback.tone) toneSugg.textContent = feedback.tone.suggestion || "Maintain confident ownership.";

    // Vocabulary Upgrades
    const vocabContainer = document.getElementById("vocab-upgrades-list");
    if (vocabContainer) {
      const suggestions = feedback.vocabulary?.suggestions || [];
      if (suggestions.length === 0) {
        vocabContainer.innerHTML = `<span style="font-size:0.78rem;color:var(--text-muted);">Appropriate vocabulary used.</span>`;
      } else {
        vocabContainer.innerHTML = suggestions.map(s => `
          <div class="vocab-upgrade-chip">${escapeHTML(s.formatted)}</div>
        `).join("");
      }
    }
  },

  // ----------------- TEXT-TO-SPEECH (TTS) -----------------
  speakText(text) {
    if (!window.speechSynthesis) {
      UI.showToast("Speech synthesis not supported in this browser.", "warning");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.lang = "en-US";
    window.speechSynthesis.speak(utterance);
  },

  // ----------------- MODALS -----------------
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add("active");
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove("active");
  },

  // ----------------- END SESSION REPORT MODAL -----------------
  renderSessionSummaryModal(report, session) {
    const scoreVal = document.getElementById("summary-final-score");
    if (scoreVal) scoreVal.textContent = `${report.overall_score}/100`;

    const fillScore = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = `${val}/10`;
    };

    fillScore("rep-g-val", report.scores?.grammar || 7.5);
    fillScore("rep-v-val", report.scores?.vocabulary || 8.0);
    fillScore("rep-c-val", report.scores?.clarity || 8.0);
    fillScore("rep-t-val", report.scores?.tone || 8.5);
    fillScore("rep-conf-val", report.scores?.confidence || 7.0);

    const strList = document.getElementById("summary-strengths-list");
    if (strList && report.strengths) {
      strList.innerHTML = report.strengths.map(s => `
        <div class="pill-item pill-strength"><span>⭐</span> ${escapeHTML(s)}</div>
      `).join("");
    }

    const impList = document.getElementById("summary-improvements-list");
    if (impList && report.areas_to_improve) {
      impList.innerHTML = report.areas_to_improve.map(i => `
        <div class="pill-item pill-focus"><span>🎯</span> ${escapeHTML(i)}</div>
      `).join("");
    }

    UI.openModal("modal-session-summary");
  }
};

function escapeHTML(str) {
  if (!str) return "";
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}
