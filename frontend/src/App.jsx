import { useEffect, useReducer, useRef, useState } from "react";
import "./App.css";
import { analyzeClaimStream, fetchCommunityReport } from "./api";
import { initialProgress, progressReducer } from "./progress";
import Sidebar from "./components/Sidebar";
import AnalyzeForm from "./components/AnalyzeForm";
import Results from "./components/Results";
import CommunityFactChecks from "./components/CommunityFactChecks";

const viewTitles = { analyze: "Analyze", community: "Community Fact-Checks" };

export default function App() {
  const [view, setView] = useState("analyze");
  const [claim, setClaim] = useState("");
  const [language, setLanguage] = useState("en");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [progress, dispatchProgress] = useReducer(progressReducer, initialProgress);
  const abortRef = useRef(null);

  // Cancel any in-flight analysis when the app unmounts.
  useEffect(() => () => abortRef.current?.abort(), []);

  async function handleAnalyze(event) {
    event?.preventDefault();

    if (!claim.trim()) {
      setError("Enter a claim before starting the analysis.");
      return;
    }

    setError("");
    setAnalysis(null);
    setSelectedSegment(null);
    dispatchProgress({ stage: "reset" });
    setLoading(true);

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const report = await analyzeClaimStream(
        claim,
        language,
        dispatchProgress,
        controller.signal
      );
      setAnalysis(report);
    } catch (err) {
      if (err.name !== "AbortError") {
        setError(err.message || "Something went wrong.");
      }
    } finally {
      if (abortRef.current === controller) setLoading(false);
    }
  }

  // Opens a stored community report in the Analyze view (no re-analysis).
  async function openCommunityReport(id) {
    const data = await fetchCommunityReport(id);
    setClaim(data.claim);
    setAnalysis(data);
    setError("");
    setSelectedSegment(null);
    setView("analyze");
    setTimeout(() => {
      document
        .querySelector(".results")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  }

  return (
    <div className="app-shell">
      <Sidebar view={view} onChange={setView} />

      <main className="main">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{viewTitles[view]}</strong>
          </div>
          <span className="live-pill">
            <i /> LIVE API
          </span>
        </header>

        <div className="page">
          {view === "community" ? (
            <CommunityFactChecks
              onOpenReport={openCommunityReport}
              refreshKey={analysis?.analysis_id}
            />
          ) : (
            <>
              <AnalyzeForm
                claim={claim}
                onClaimChange={(value) => {
                  setClaim(value);
                  setError("");
                }}
                language={language}
                onLanguageChange={setLanguage}
                loading={loading}
                progress={progress}
                error={error}
                onSubmit={handleAnalyze}
              />
              {analysis && !loading && (
                <Results
                  analysis={analysis}
                  isHindi={language === "hi"}
                  selected={selectedSegment}
                  onSelect={setSelectedSegment}
                  onClear={() => {
                    setAnalysis(null);
                    setError("");
                  }}
                />
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
