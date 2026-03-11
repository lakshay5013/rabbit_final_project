import { useState } from "react";
import "./App.css";

// Backend URL — change for production
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Pipeline step labels
const STEPS = [
  { key: "signals", label: "Signal Capture", icon: "📡" },
  { key: "research", label: "Research", icon: "🔬" },
  { key: "email", label: "Outreach", icon: "📧" },
];

function App() {
  // ─── Form State ────────────────────────────────────────
  const [icp, setIcp] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [recipientName, setRecipientName] = useState("");

  // ─── UI State ──────────────────────────────────────────
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // ─── Run Agent ─────────────────────────────────────────
  const handleRun = async () => {
    if (!icp.trim() || !company.trim() || !email.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    setError(null);
    setResult(null);
    setLoading(true);

    // Simulate pipeline steps for UX
    setCurrentStep("signals");
    const stepTimer1 = setTimeout(() => setCurrentStep("research"), 3000);
    const stepTimer2 = setTimeout(() => setCurrentStep("email"), 7000);

    try {
      const response = await fetch(`${API_URL}/run-agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ icp, company, email, recipient_name: recipientName }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Agent execution failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to connect to backend");
    } finally {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setLoading(false);
      setCurrentStep(null);
    }
  };

  return (
    <div className="app">
      {/* ─── Header ──────────────────────────────────── */}
      <header className="header">
        <h1 className="header__logo">
          🔥 <span className="gradient-text">FireReach</span>
        </h1>
        <p className="header__tagline">
          Autonomous Outreach Engine — Agentic AI with Tool Calling
        </p>
      </header>

      {/* ─── Pipeline Indicator ──────────────────────── */}
      <div className="pipeline">
        {STEPS.map((step, i) => (
          <div key={step.key} style={{ display: "flex", alignItems: "center" }}>
            <span
              className={`pipeline__step ${
                currentStep === step.key
                  ? "pipeline__step--active"
                  : result && !loading
                  ? "pipeline__step--done"
                  : ""
              }`}
            >
              {step.icon} {step.label}
            </span>
            {i < STEPS.length - 1 && <span className="pipeline__arrow">→</span>}
          </div>
        ))}
      </div>

      {/* ─── Input Card ──────────────────────────────── */}
      <div className="input-card">
        <h2 className="input-card__title">⚙️ Agent Configuration</h2>

        <div className="input-card__grid">
          <div className="field field--full">
            <label className="field__label" htmlFor="icp">
              Ideal Customer Profile (ICP)
            </label>
            <textarea
              id="icp"
              className="field__textarea"
              placeholder="e.g. We sell high-end cybersecurity training to Series B+ startups"
              value={icp}
              onChange={(e) => setIcp(e.target.value)}
              rows={3}
            />
          </div>

          <div className="field">
            <label className="field__label" htmlFor="company">
              Target Company
            </label>
            <input
              id="company"
              type="text"
              className="field__input"
              placeholder="e.g. Ramp"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
          </div>

          <div className="field">
            <label className="field__label" htmlFor="email">
              Candidate Email
            </label>
            <input
              id="email"
              type="email"
              className="field__input"
              placeholder="e.g. alex@ramp.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="field">
            <label className="field__label" htmlFor="recipientName">
              Recipient Name
            </label>
            <input
              id="recipientName"
              type="text"
              className="field__input"
              placeholder="e.g. Alex Johnson"
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
            />
          </div>
        </div>

        <button
          className="btn-run"
          onClick={handleRun}
          disabled={loading}
        >
          {loading ? "⏳ Agent Running..." : "🚀 Run FireReach Agent"}
        </button>
      </div>

      {/* ─── Error ───────────────────────────────────── */}
      {error && <div className="error">❌ {error}</div>}

      {/* ─── Loading ─────────────────────────────────── */}
      {loading && (
        <div className="loading">
          <div className="loading__spinner" />
          <p className="loading__text">Agent is executing the pipeline...</p>
          {currentStep && (
            <p className="loading__step">
              {STEPS.find((s) => s.key === currentStep)?.icon}{" "}
              {STEPS.find((s) => s.key === currentStep)?.label}
            </p>
          )}
        </div>
      )}

      {/* ─── Results ─────────────────────────────────── */}
      {result && !loading && (
        <div className="results">
          {/* Signals Card */}
          <div className="result-card">
            <div className="result-card__header">
              <div className="result-card__icon result-card__icon--signals">📡</div>
              <h3 className="result-card__title">Captured Signals</h3>
              <span className="result-card__badge">
                {result.signals.length} signals
              </span>
            </div>
            <ul className="signals-list">
              {result.signals.map((signal, i) => (
                <li key={i} className="signals-list__item">
                  {signal}
                </li>
              ))}
            </ul>
          </div>

          {/* Account Brief Card */}
          <div className="result-card">
            <div className="result-card__header">
              <div className="result-card__icon result-card__icon--brief">🔬</div>
              <h3 className="result-card__title">Account Brief</h3>
            </div>
            <p className="brief-text">{result.account_brief}</p>
          </div>

          {/* Email Card */}
          <div className="result-card">
            <div className="result-card__header">
              <div className="result-card__icon result-card__icon--email">📧</div>
              <h3 className="result-card__title">Outreach Email</h3>
              <span
                className="result-card__badge"
                style={
                  result.email_sent
                    ? {}
                    : { background: "rgba(239,68,68,0.15)", color: "#f87171" }
                }
              >
                {result.email_sent ? "✓ Sent" : "⚠ Not Sent"}
              </span>
            </div>
            {!result.email_sent && result.email_error && (
              <div className="error" style={{ marginBottom: 16 }}>
                ⚠️ {result.email_error}
              </div>
            )}
            <div className="email-preview">
              <div className="email-preview__subject">
                <span className="email-preview__subject-label">Subject:</span>
                <span className="email-preview__subject-text">
                  {result.email_subject}
                </span>
              </div>
              <div className="email-preview__body">{result.email_body}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
