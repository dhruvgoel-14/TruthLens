import { verdicts } from "../lib";
import Evidence from "./Evidence";

export default function Results({ analysis, isHindi, selected, onSelect, onClear }) {
  const lang = isHindi ? "local" : "en";
  const pick = (field) => field?.[lang] || field?.en;

  const verdict = analysis.final_verdict || analysis.verdict || "";
  const meta = verdicts[verdict] || { label: verdict.replaceAll("_", " "), tone: "unverified" };
  const score = analysis.consensus_score;
  const segments = analysis.diff_segments || [];
  const activeSegment = selected !== null ? segments[selected] : null;

  const explanation = pick(analysis.explanation) || "No explanation is available.";
  const claimed = pick(analysis.claim_vs_reality?.claimed) || analysis.claim || "";
  const actual = pick(analysis.claim_vs_reality?.actual) || "";

  function focusSegment(index) {
    onSelect(index);
    document
      .getElementById(`evidence-${index}`)
      ?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return (
    <section className="results" aria-live="polite">
      <div className="section-head">
        <div>
          <div className="kicker">INVESTIGATION REPORT</div>
          <h2>Analysis results</h2>
          <p>Review the verdict and explore the evidence behind it.</p>
        </div>
        <button className="text-button" onClick={onClear}>Clear results ×</button>
      </div>

      <div className={`verdict-card ${meta.tone}`}>
        <div className="verdict-copy">
          <span className={`badge ${meta.tone}`}>{meta.label.toUpperCase()}</span>
          <p>{explanation}</p>
        </div>
        <div className="score-panel">
          <span className="kicker">CONSENSUS SCORE</span>
          <div className="score-number">
            {score ?? "—"}
            <span>/100</span>
          </div>
          <div className="score-track">
            <span style={{ width: `${Math.max(0, Math.min(100, score ?? 0))}%` }} />
          </div>
          <small>{analysis.dominant_stance || "No dominant stance"}</small>
        </div>
      </div>

      {analysis.zombie_suspected && (
        <div className="notice">
          <b>↻</b>
          <div>
            <strong>Possible recycled claim</strong>
            <p>This result has been flagged as potentially recycled or resurfacing news.</p>
          </div>
        </div>
      )}

      <section className="card">
        <div className="panel-head">
          <div>
            <div className="kicker">CLAIM BREAKDOWN</div>
            <h3>Pinpoint the difference</h3>
          </div>
          <span className="caption">Select a segment to inspect its correction</span>
        </div>

        <div className="inline-claim" aria-label="Word-by-word claim analysis">
          {segments.map((segment, index) => {
            const label = (segment.label || "MISLEADING").toLowerCase();
            return (
              <button
                type="button"
                key={`${segment.text}-${index}`}
                className={`claim-highlight ${label} ${selected === index ? "chosen" : ""}`}
                onClick={() => focusSegment(index)}
                title={
                  segment.correction
                    ? `${segment.label}: ${segment.correction}`
                    : `${segment.label}: Click to inspect related evidence`
                }
              >
                {segment.text}
                {segment.correction && <span className="claim-correction"> ({segment.correction})</span>}
              </button>
            );
          })}
        </div>

        <div className="legend">
          <span><i className="dot true" /> Verified</span>
          <span><i className="dot misleading" /> Misleading</span>
          <span><i className="dot false" /> Contradicted</span>
        </div>

        {activeSegment && (
          <div className={`segment-note ${String(activeSegment.label || "").toLowerCase()}`}>
            <strong>{activeSegment.label}</strong>
            <span>{activeSegment.correction || "Related evidence is highlighted below."}</span>
          </div>
        )}
      </section>

      <section className="compare-grid">
        <article className="card">
          <div className="kicker">WHAT WAS CLAIMED</div>
          <p>{claimed}</p>
        </article>
        <article className="card reality">
          <div className="kicker accent">THE REALITY</div>
          <p>{actual}</p>
        </article>
      </section>

      <Evidence
        analysis={analysis}
        highlightIds={activeSegment?.evidence_chunk_ids || []}
      />

      <p className="disclaimer">
        ⓘ This report was returned by the live TruthLens backend. The consensus
        score is not a probability that a claim is true.
      </p>
    </section>
  );
}
