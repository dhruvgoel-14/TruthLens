import { useEffect, useState } from "react";
import { fetchCommunityClaims } from "../api";
import { timeAgo, verdicts } from "../lib";

const PAGE_SIZE = 8;

export default function CommunityFactChecks({ onOpenReport, refreshKey }) {
  const [page, setPage] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [openError, setOpenError] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let cancelled = false;

    fetchCommunityClaims(page, PAGE_SIZE)
      .then((data) => {
        if (!cancelled) {
          setError("");
          setResult(data);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [page, refreshKey, retry]);

  const loading = !error && (!result || result.page !== page);

  function changePage(next) {
    setError("");
    setPage(next);
  }

  function retryLoad() {
    setError("");
    setRetry((n) => n + 1);
  }

  async function handleOpen(id) {
    setOpenError("");
    try {
      await onOpenReport(id);
    } catch (err) {
      setOpenError(err.message || "Could not open this report.");
    }
  }

  const items = result?.items || [];

  return (
    <section className="cfc-section">
      <div className="cfc-header">
        <div className="kicker">COMMUNITY</div>
        <h2>Community Fact-Checks</h2>
        <p>
          Claims recently investigated by TruthLens users. See what is
          circulating and what the evidence says.
        </p>
      </div>

      {openError && <div className="cfc-error">{openError}</div>}

      {error && (
        <div className="cfc-error">
          {error} <button onClick={retryLoad}>Try again</button>
        </div>
      )}

      {loading && <div className="cfc-empty">Loading fact-checks…</div>}

      {!loading && !error && items.length === 0 && (
        <div className="cfc-empty">
          No fact-checks yet. Analyze a claim and it will appear here.
        </div>
      )}

      <div className="cfc-list">
        {items.map((item) => (
          <article className="cfc-card" key={item.id}>
            <div className="cfc-card-top">
              <span className={`cfc-badge ${verdicts[item.verdict]?.tone || "unverified"}`}>
                {verdicts[item.verdict]?.label || item.verdict}
              </span>
              {item.zombie_suspected && (
                <span className="cfc-badge recycled">↻ Possibly recycled</span>
              )}
              {item.analysis_count > 1 && (
                <span className="cfc-badge count">
                  Checked {item.analysis_count} times
                </span>
              )}
              <span
                className="cfc-time"
                title={new Date(item.last_analyzed_at).toLocaleString()}
              >
                {timeAgo(item.last_analyzed_at)}
              </span>
            </div>

            <p className="cfc-claim">{item.claim}</p>
            {item.explanation_snippet && (
              <p className="cfc-snippet">{item.explanation_snippet}</p>
            )}

            <div className="cfc-footer">
              <span>
                Consensus score:{" "}
                <strong>{item.consensus_score ?? "—"}</strong>
                {item.consensus_score != null && "/100"}
              </span>
              <button className="cfc-open" onClick={() => handleOpen(item.id)}>
                View full report →
              </button>
            </div>
          </article>
        ))}
      </div>

      {result && result.total_pages > 1 && (
        <div className="cfc-pagination">
          <button disabled={page <= 1} onClick={() => changePage(page - 1)}>
            ← Previous
          </button>
          <span>
            Page {result.page} of {result.total_pages}
          </span>
          <button
            disabled={page >= result.total_pages}
            onClick={() => changePage(page + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </section>
  );
}