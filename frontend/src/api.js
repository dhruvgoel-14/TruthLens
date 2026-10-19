// All backend calls live here. Vite proxies /api to the FastAPI server.

// FastAPI sends `detail` as a string (our errors) or a list (validation errors).
function errorMessage(data, fallback) {
  const detail = data?.detail ?? data?.error;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join("; ");
  return fallback;
}

async function request(url, options, fallbackMessage) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(errorMessage(data, fallbackMessage));
  }
  return data;
}

export const analyzeClaim = (claim) =>
  request(
    "/api/analyze",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        claim: claim.trim(),
        max_sources: 5,
      }),
    },
    "Claim analysis failed."
  );

export const fetchCommunityClaims = (page, pageSize) =>
  request(
    `/api/community-claims?page=${page}&page_size=${pageSize}`,
    undefined,
    "Could not load community fact-checks."
  );

export const fetchCommunityReport = (id) =>
  request(`/api/community-claims/${id}`, undefined, "Could not load this report.");

// Streams an analysis over Server-Sent Events (POST, so we read the body
// ourselves instead of using EventSource). The backend detects the claim's
// language, so none is sent. Calls onProgress for each pipeline
// stage and resolves with the final report.
export async function analyzeClaimStream(claim, onProgress, signal) {
  const response = await fetch("/api/analyze/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({
      claim: claim.trim(),
      max_sources: 5,
    }),
    signal,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(errorMessage(data, "Claim analysis failed."));
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let report = null;

  function handleFrame(frame) {
    let event = "message";
    let payload = "";
    for (const line of frame.split("\n")) {
      if (line.startsWith("event:")) event = line.slice(6).trim();
      else if (line.startsWith("data:")) payload += line.slice(5).trim();
    }
    if (!payload) return; // keep-alive comment
    const data = JSON.parse(payload);

    if (event === "progress") onProgress?.(data);
    else if (event === "result") report = data;
    else if (event === "error") throw new Error(data.detail || "Claim analysis failed.");
  }

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
    const frames = buffer.split("\n\n");
    buffer = frames.pop(); // the last piece may be an incomplete frame
    frames.forEach(handleFrame);
  }

  if (!report) throw new Error("The analysis ended unexpectedly. Please try again.");
  return report;
}
