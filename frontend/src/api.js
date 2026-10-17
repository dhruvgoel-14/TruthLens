// All backend calls live here. Vite proxies /api to the FastAPI server.
async function request(url, options, fallbackMessage) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || data.error || fallbackMessage);
  }
  return data;
}

export const analyzeClaim = (claim, language) =>
  request(
    "/api/analyze",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        claim: claim.trim(),
        language: language === "hi" ? "hi" : "en",
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
