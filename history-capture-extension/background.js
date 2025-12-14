const BACKEND_URL = "http://localhost:8000/api/history";

let lastSentUrl = null;
let lastSentTime = 0;
const DEDUPE_MS = 2000;

function normalizeUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);

    const trackingParams = [
      "gclid", "fbclid", "utm_source", "utm_medium",
      "utm_campaign", "utm_term", "utm_content",
      "gad_source", "gbraid"
    ];

    trackingParams.forEach(p => url.searchParams.delete(p));

    return url.toString();
  } catch {
    return null;
  }
}
chrome.history.onVisited.addListener((item) => {
  if (!item.url) return;
  if (!item.url.startsWith("http")) return;
  if (item.url.includes("localhost:8000")) return;
  if (item.url.startsWith("https://www.google.com/search")) return;

  //Block Google Ads redirect URLs
  try {
    const u = new URL(item.url);
    if (u.pathname.includes("/aclk")) return;
  } catch {
    return;
  }

  const cleanUrl = normalizeUrl(item.url);
  if (!cleanUrl) return;

  const now = Date.now();
  if (
    cleanUrl === lastSentUrl &&
    now - lastSentTime < DEDUPE_MS
  ) return;

  lastSentUrl = cleanUrl;
  lastSentTime = now;

  fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url: cleanUrl,
      title: item.title || null
    })
  }).catch(console.error);
});
