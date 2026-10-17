
import { useState } from "react";
import "./App.css";
import CommunityFactChecks from "./components/CommunityFactChecks";

const sampleClaims = [
  "Indian Flydubai pilot Smit Machchhar flew his Boeing 737 upside down to knock out an armed hijacker.",
  "The Government of India publishes official press releases through the Press Information Bureau.",
  "Drinking warm water cures viral infections.",
];

const verdictLabels = {
  SUPPORTED: "Supported",
  REFUTED: "Refuted",
  INSUFFICIENT_EVIDENCE: "Insufficient evidence",
  UNVERIFIED_NO_AUTHORITATIVE_SOURCES: "Unverified",
};

const verdictClasses = {
  SUPPORTED: "supported",
  REFUTED: "refuted",
  INSUFFICIENT_EVIDENCE: "insufficient",
  UNVERIFIED_NO_AUTHORITATIVE_SOURCES: "unverified",
};

function formatSeconds(milliseconds) {
  return `${(milliseconds / 1000).toFixed(1)}s`;
}

function getSourceUrl(source) {
  return source.source_url || source.url || "#";
}

function getDomain(source) {
  return (source.domain || "").replace(/^www\./, "");
}

export default function App() {
  const [claim, setClaim] = useState(sampleClaims[0]);
  const [language, setLanguage] = useState("en");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeNav, setActiveNav] = useState("Analyze");
  const [selectedSegment, setSelectedSegment] = useState(null);

  const isHindi = language === "hi";
  const verdict = analysis?.final_verdict || analysis?.verdict || "";
  const verdictClass = verdictClasses[verdict] || "unverified";

  async function handleAnalyze(event) {
    event?.preventDefault();

    if (!claim.trim()) {
      setError("Enter a claim before starting the analysis.");
      return;
    }

    setError("");
    setAnalysis(null);
    setSelectedSegment(null);
    setLoading(true);

    try {
      // Live mode: send the user's claim to the backend API.
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          claim: claim.trim(),
          language: language === "hi" ? "hi" : "en",
          max_sources: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || data.error || "Claim analysis failed."
        );
      }

      setAnalysis(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function selectSample(sample) {
    setClaim(sample);
    setError("");
  }

  async function openCommunityReport(id) {
    const response = await fetch(`/api/community-claims/${id}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Could not load this report.");
    }

    setClaim(data.claim);
    setAnalysis(data);
    setError("");
    setSelectedSegment(null);
    setActiveNav("Analyze");
    setTimeout(() => {
      document
        .querySelector(".results-section")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }

  function focusSegment(index) {
    setSelectedSegment(index);
    document
      .getElementById(`evidence-${index}`)
      ?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  const explanation =
    analysis?.explanation?.[isHindi ? "local" : "en"] ||
    analysis?.explanation?.en ||
    "No explanation is available.";

  const claimedText =
    analysis?.claim_vs_reality?.claimed?.[isHindi ? "local" : "en"] ||
    analysis?.claim_vs_reality?.claimed?.en ||
    analysis?.claim ||
    "";

  const actualText =
    analysis?.claim_vs_reality?.actual?.[isHindi ? "local" : "en"] ||
    analysis?.claim_vs_reality?.actual?.en ||
    "";

  const evidence = analysis?.evidence || [];
  const sources = analysis?.sources || [];
  const diffSegments = analysis?.diff_segments || [];
  const timings = analysis?.timings_ms || {};

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#home" onClick={() => setActiveNav("Analyze")}>
          <span className="brand-mark">T</span>
          <span>
            <strong>TruthLens</strong>
            <small>AI-powered fact checking</small>
          </span>
        </a>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="side-nav" aria-label="Main navigation">
          <button
            className={activeNav === "Analyze" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveNav("Analyze")}
          >
            <span className="nav-icon">⌕</span>
            <span>Analyze claim</span>
            <span className="nav-arrow">↗</span>
          </button>

          <button
            className={activeNav === "Community" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveNav("Community")}
          >
            <span className="nav-icon">◉</span>
            <span>Community Fact-Checks</span>
          </button>

          <button
            className={activeNav === "History" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveNav("History")}
          >
            <span className="nav-icon">◷</span>
            <span>History</span>
          </button>

          <button
            className={activeNav === "Saved reports" ? "nav-item active" : "nav-item"}
            onClick={() => setActiveNav("Saved reports")}
          >
            <span className="nav-icon">▤</span>
            <span>Saved reports</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="mode-card">
            <span className="mode-dot" />
            <div>
              <strong>Live analysis</strong>
              <small>Connected to backend API</small>
            </div>
          </div>

          <div className="profile">
            <div className="avatar">TL</div>
            <div>
              <strong>TruthLens workspace</strong>
              <small>Local development</small>
            </div>
            <span className="profile-more">···</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activeNav}</strong>
          </div>
          <div className="topbar-right">
            <span className="preview-pill live-pill">
              <span /> LIVE API
            </span>
            <button
              className="icon-button"
              title="Live backend mode"
              aria-label="Live backend mode"
            >
              ◈
            </button>
          </div>
        </header>

        <div className="page-content">
          {(activeNav === "History" || activeNav === "Saved reports") &&  (
            <div className="preview-notice">
              History and saved reports are not connected yet. Return to <button onClick={() => setActiveNav("Analyze")}>Analyze claim</button> to run a live verification.
            </div>
          )}
          {activeNav === "Community" ? (
            <CommunityFactChecks
              onOpenReport={openCommunityReport}
              refreshKey={analysis?.analysis_id}
            />
          ) : (
            <>
              <section className="hero">
                <div className="eyebrow">
                  <span className="eyebrow-line" />
                  CLARITY IN A WORLD OF CLAIMS
                </div>
                <h1>
                  Separate the signal
                  <br />
                  from <span>the noise.</span>
                </h1>
                <p>
                  Investigate a claim. Examine the evidence. Get a clearer picture
                  of what is actually true.
                </p>
              </section>

              <section className="analyzer-card">
                <div className="card-heading">
                  <div>
                    <div className="section-kicker">START YOUR INVESTIGATION</div>
                    <h2>What would you like to verify?</h2>
                  </div>
                  <div className="input-symbol">✳</div>
                </div>

                <form onSubmit={handleAnalyze}>
                  <label className="field-label" htmlFor="claim-input">
                    CLAIM OR STATEMENT
                  </label>
                  <textarea
                    id="claim-input"
                    value={claim}
                    onChange={(event) => setClaim(event.target.value)}
                    placeholder="Paste a news headline, social media post, or claim..."
                    maxLength={2000}
                    rows={4}
                  />

                  <div className="input-meta">
                    <span>Be specific for more useful results.</span>
                    <span>{claim.length}/2000</span>
                  </div>

                  <div className="form-bottom">
                    <div className="language-picker">
                      <span className="language-label">LANGUAGE</span>
                      <div className="language-switch" role="group" aria-label="Result language">
                        <button
                          type="button"
                          className={language === "en" ? "selected" : ""}
                          onClick={() => setLanguage("en")}
                        >
                          English
                        </button>
                        <button
                          type="button"
                          className={language === "hi" ? "selected" : ""}
                          onClick={() => setLanguage("hi")}
                        >
                          हिंदी
                        </button>
                      </div>
                    </div>

                    <button className="analyze-button" type="submit" disabled={loading}>
                      {loading ? (
                        <>
                          <span className="spinner" /> Analyzing claim...
                        </>
                      ) : (
                        <>
                          Analyze claim <span>↗</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>

                <div className="sample-area">
                  <span className="sample-label">TRY AN EXAMPLE</span>
                  <div className="sample-chips">
                    {sampleClaims.map((sample, index) => (
                      <button
                        key={sample}
                        className="sample-chip"
                        type="button"
                        onClick={() => selectSample(sample)}
                      >
                        <span>{["✳", "◈", "⌁"][index]}</span>
                        {index === 0
                          ? "A viral aviation story"
                          : index === 1
                            ? "An official government claim"
                            : "A health claim"}
                      </button>
                    ))}
                  </div>
                </div>
              </section>

              {error && (
                <div className="error-banner" role="alert">
                  <span>!</span>
                  {error}
                </div>
              )}

              {loading && (
                <section className="loading-card">
                  <div className="loading-orb">✳</div>
                  <h3>Preparing your analysis</h3>
                  <p>Sending your claim to the TruthLens backend for analysis.</p>
                  <div className="loading-track"><span /></div>
                  <small>Analysis is being processed by the backend.</small>
                </section>
              )}

              {analysis && !loading && (
                <section className="results-section" aria-live="polite">
                  <div className="results-heading">
                    <div>
                      <div className="section-kicker">INVESTIGATION REPORT</div>
                      <h2>Analysis results</h2>
                      <p>Review the verdict and explore the evidence behind it.</p>
                    </div>
                    <button
                      className="text-button"
                      onClick={() => {
                        setAnalysis(null);
                        setError("");
                      }}
                    >
                      Clear results ×
                    </button>
                  </div>

                  <div className={`verdict-card ${verdictClass}`}>
                    <div className="verdict-icon">
                      {verdict === "REFUTED" ? "×" : verdict === "SUPPORTED" ? "✓" : "?"}
                    </div>
                    <div className="verdict-copy">
                      <span className="section-kicker">TRUTHLENS VERDICT</span>
                      <h2>{verdictLabels[verdict] || verdict.replaceAll("_", " ")}</h2>
                      <p>{explanation}</p>
                    </div>
                    <div className="score-panel">
                      <span className="score-label">CONSENSUS SCORE</span>
                      <div className="score-number">
                        {analysis.consensus_score ?? "—"}
                        <span>/100</span>
                      </div>
                      <div className="score-track">
                        <span style={{ width: `${Math.max(0, Math.min(100, analysis.consensus_score ?? 0))}%` }} />
                      </div>
                      <small>{analysis.dominant_stance || "No dominant stance"}</small>
                    </div>
                  </div>

                  {analysis.zombie_suspected && (
                    <div className="zombie-banner">
                      <span>↻</span>
                      <div>
                        <strong>Possible recycled claim</strong>
                        <p>This result has been flagged as potentially recycled or resurfacing news.</p>
                      </div>
                    </div>
                  )}

                  <section className="result-panel">
                    <div className="panel-heading">
                      <div>
                        <span className="section-kicker">CLAIM BREAKDOWN</span>
                        <h3>Pinpoint the difference</h3>
                      </div>
                      <span className="panel-caption">Select a segment to inspect its correction</span>
                    </div>

                    <div className="inline-claim-analysis" aria-label="Word-by-word claim analysis">
                      {diffSegments.map((segment, index) => {
                        const label = (segment.label || "MISLEADING").toLowerCase();
                        return (
                          <button
                            type="button"
                            key={`${segment.text}-${index}`}
                            className={`claim-highlight ${label} ${selectedSegment === index ? "chosen" : ""}`}
                            onClick={() => focusSegment(index)}
                            title={
                              segment.correction
                                ? `${segment.label}: ${segment.correction}`
                                : `${segment.label}: Click to inspect related evidence`
                            }
                            aria-label={`${segment.label}: ${segment.text}${segment.correction ? `. Correction: ${segment.correction}` : ""}`}
                          >
                            {segment.text}
                            {segment.correction && (
                              <span className="claim-correction"> ({segment.correction})</span>
                            )}
                          </button>
                        );
                      })}
                    </div>

                    <div className="diff-legend" aria-label="Claim highlight legend">
                      <span><i className="legend-dot true" /> Verified</span>
                      <span><i className="legend-dot misleading" /> Misleading</span>
                      <span><i className="legend-dot false" /> Contradicted</span>
                    </div>

                    {selectedSegment !== null && diffSegments[selectedSegment] && (
                      <div className={`selected-claim-note ${String(diffSegments[selectedSegment].label || "").toLowerCase()}`}>
                        <strong>{diffSegments[selectedSegment].label}</strong>
                        <span>{diffSegments[selectedSegment].correction || "Related evidence is highlighted below."}</span>
                      </div>
                    )}
                  </section>

                  <section className="comparison-grid">
                    <article className="comparison-card claimed-card">
                      <div className="comparison-title">
                        <span className="comparison-icon">↗</span>
                        <div>
                          <span className="section-kicker">THE ORIGINAL CLAIM</span>
                          <h3>What was claimed</h3>
                        </div>
                      </div>
                      <p>{claimedText}</p>
                    </article>

                    <article className="comparison-card reality-card">
                      <div className="comparison-title">
                        <span className="comparison-icon">✓</span>
                        <div>
                          <span className="section-kicker">WHAT THE EVIDENCE SAYS</span>
                          <h3>The reality</h3>
                        </div>
                      </div>
                      <p>{actualText}</p>
                    </article>
                  </section>

                  <section className="result-panel">
                    <div className="panel-heading">
                      <div>
                        <span className="section-kicker">SOURCE-BASED RESEARCH</span>
                        <h3>Evidence that matters</h3>
                        <p className="panel-description">
                          Examine the supporting material used to assess this claim.
                        </p>
                      </div>
                      <span className="count-pill">{evidence.length} evidence items</span>
                    </div>

                    <div className="evidence-list">
                      {evidence.map((item, index) => (
                        <article
                          className={`evidence-card ${selectedSegment !== null && diffSegments[selectedSegment]?.evidence_chunk_ids?.includes(item.chunk_id) ? "highlighted" : ""}`}
                          id={`evidence-${index}`}
                          key={`${item.chunk_id}-${item.source_url}`}
                        >
                          <div className="evidence-top">
                            <div className="source-avatar">
                              {getDomain(item).slice(0, 1).toUpperCase() || "S"}
                            </div>
                            <div className="evidence-source">
                              <strong>{getDomain(item) || "Source"}</strong>
                              <span>Evidence #{item.chunk_id} · Tier {item.tier ?? "—"}</span>
                            </div>
                            <span className="stance-badge contradicts">
                              {item.stance || "EVIDENCE"}
                            </span>
                          </div>

                          <blockquote>“{item.verbatim_quote}”</blockquote>

                          <div className="evidence-bottom">
                            <span className={item.quote_verified ? "verified-badge" : "unverified-badge"}>
                              {item.quote_verified ? "✓ Quote verified" : "⚠ Unverified quote"}
                            </span>
                            <a
                              href={getSourceUrl(item)}
                              target="_blank"
                              rel="noreferrer"
                            >
                              Read original source ↗
                            </a>
                          </div>
                        </article>
                      ))}
                    </div>
                  </section>

                  <section className="result-panel">
                    <div className="panel-heading">
                      <div>
                        <span className="section-kicker">RESEARCH TRAIL</span>
                        <h3>Sources consulted</h3>
                        <p className="panel-description">
                          Websites considered during the original investigation.
                        </p>
                      </div>
                      <span className="count-pill">{sources.length} sources</span>
                    </div>

                    <div className="search-summary">
                      <div>
                        <strong>{analysis.search_summary?.attempted ?? 0}</strong>
                        <span>Queries attempted</span>
                      </div>
                      <div>
                        <strong>{analysis.search_summary?.succeeded ?? 0}</strong>
                        <span>Queries succeeded</span>
                      </div>
                      <div>
                        <strong>{analysis.fetch_summary?.fetched ?? 0}</strong>
                        <span>Pages fetched</span>
                      </div>
                    </div>

                    <details className="sources-dropdown">
                      <summary className="sources-dropdown-summary">
                        <span className="sources-summary-icon">↗</span>
                        <span className="sources-summary-copy">
                          <strong>Click to view referred sources</strong>
                          <small>{sources.length} source{sources.length === 1 ? "" : "s"} · Opens original websites in a new tab</small>
                        </span>
                        <span className="sources-summary-count">{sources.length}</span>
                        <span className="sources-chevron" aria-hidden="true">⌄</span>
                      </summary>

                      <div className="source-list">
                        {sources.map((source, index) => (
                          <a
                            className="source-row"
                            href={source.url || getSourceUrl(source)}
                            target="_blank"
                            rel="noreferrer"
                            key={`${source.url || getSourceUrl(source)}-${index}`}
                          >
                            <span className="source-number">{String(index + 1).padStart(2, "0")}</span>
                            <span className="source-details">
                              <strong>{source.title || getDomain(source) || `Source ${index + 1}`}</strong>
                              <small>{getDomain(source)} · Tier {source.tier ?? "—"}</small>
                              {source.snippet && <span>{source.snippet}</span>}
                            </span>
                            <span className="external-arrow">↗</span>
                          </a>
                        ))}
                      </div>
                    </details>
                  </section>

                  <div className="timing-strip">
                    <div className="timing-title">
                      <span>◷</span>
                      <div>
                        <strong>Original analysis timings</strong>
                        <small>Recorded in the saved response</small>
                      </div>
                    </div>
                    <div className="timing-item">
                      <small>Evidence collection</small>
                      <strong>{formatSeconds(timings.evidence_collection || 0)}</strong>
                    </div>
                    <div className="timing-item">
                      <small>Judge</small>
                      <strong>{formatSeconds(timings.judge || 0)}</strong>
                    </div>
                    <div className="timing-item">
                      <small>Total</small>
                      <strong>{formatSeconds(timings.total || 0)}</strong>
                    </div>
                  </div>

                  <p className="demo-disclaimer">
                    <span>ⓘ</span>
                    This report was returned by the live TruthLens backend. The consensus score is not a
                    probability that a claim is true.
                  </p>
                </section>
              )}
            </>
          )}
          <footer className="footer">
            <span>© 2026 TruthLens</span>
            <span>Evidence first. Clarity always.</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
