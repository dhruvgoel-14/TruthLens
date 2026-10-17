import { getDomain, getSourceUrl } from "../lib";

// One panel for evidence + sources. Sources that already supplied a quote are
// shown once (as evidence); only the remaining ones go under "Also consulted".
const urlKey = (item) => getSourceUrl(item).replace(/#.*$/, "").replace(/\/$/, "");

export default function Evidence({ analysis, highlightIds }) {
  const evidence = analysis.evidence || [];
  const sources = analysis.sources || [];
  const search = analysis.search_summary;
  const fetched = analysis.fetch_summary?.fetched;

  const cited = new Set(evidence.map(urlKey));
  const others = sources.filter((source) => !cited.has(urlKey(source)));

  const trail = [
    search?.attempted != null && `${search.succeeded ?? 0}/${search.attempted} searches succeeded`,
    fetched != null && `${fetched} pages read`,
    `${sources.length} sources considered`,
  ].filter(Boolean);

  return (
    <section className="card evidence">
      <div className="panel-head">
        <div>
          <div className="kicker">EVIDENCE &amp; SOURCES</div>
          <h3>What the sources say</h3>
          <p className="caption">Direct quotes from the pages used to reach this verdict.</p>
        </div>
        <span className="pill">{evidence.length} quotes</span>
      </div>

      <div className="trail mono">{trail.join("  ·  ")}</div>

      {evidence.length === 0 && (
        <p className="caption">No verified evidence quotes were returned for this claim.</p>
      )}

      <div className="evidence-list">
        {evidence.map((item, index) => {
          const stance = (item.stance || "evidence").toLowerCase();
          return (
            <article
              className={`evidence-card ${highlightIds.includes(item.chunk_id) ? "highlighted" : ""}`}
              id={`evidence-${index}`}
              key={`${item.chunk_id}-${item.source_url}`}
            >
              <div className="evidence-top">
                <div className="avatar">{getDomain(item).slice(0, 1).toUpperCase() || "S"}</div>
                <div className="evidence-source">
                  <strong>{getDomain(item) || "Source"}</strong>
                  <span className="mono">Evidence #{item.chunk_id} · Tier {item.tier ?? "—"}</span>
                </div>
                <span className={`badge ${stance}`}>{(item.stance || "EVIDENCE").toUpperCase()}</span>
              </div>

              <blockquote>“{item.verbatim_quote}”</blockquote>

              <div className="evidence-bottom">
                <span className={item.quote_verified ? "ok" : "warn"}>
                  {item.quote_verified ? "✓ Quote verified" : "⚠ Unverified quote"}
                </span>
                <a href={getSourceUrl(item)} target="_blank" rel="noreferrer">
                  Read original source ↗
                </a>
              </div>
            </article>
          );
        })}
      </div>

      {others.length > 0 && (
        <details className="also">
          <summary>
            {evidence.length ? "Also consulted" : "Sources consulted"} ({others.length})
            <span aria-hidden="true">⌄</span>
          </summary>
          <ul>
            {others.map((source, index) => (
              <li key={`${getSourceUrl(source)}-${index}`}>
                <a href={getSourceUrl(source)} target="_blank" rel="noreferrer">
                  <strong>{source.title || getDomain(source) || `Source ${index + 1}`}</strong>
                  <small>{getDomain(source)}{source.tier != null && ` · Tier ${source.tier}`}</small>
                </a>
              </li>
            ))}
          </ul>
        </details>
      )}
    </section>
  );
}
