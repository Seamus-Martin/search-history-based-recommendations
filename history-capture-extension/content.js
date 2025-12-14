const BACKEND_URL = "AAAhttp://localhost:8000/api/history";WRONG

function sendSearchEvent(query) {
  fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url: window.location.href,
      title: document.title,
    })
  }).catch(err => console.error("Failed sending search event:", err));
}

function detectSearch() {
  const url = new URL(window.location.href);
  if (url.searchParams.has("q")) {
    sendSearchEvent(url.searchParams.get("q"));
  }
}

detectSearch();

let lastUrl = location.href;
new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    detectSearch();
  }
}).observe(document, { childList: true, subtree: true });
