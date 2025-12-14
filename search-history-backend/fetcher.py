import httpx
from bs4 import BeautifulSoup


async def fetch_html(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(
    timeout=10,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    },
    follow_redirects=True
) as client:

            response = await client.get(url, follow_redirects=True)

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                return None

            return response.text
    except Exception as e:
        print("Fetch error:", e)
        return None

#from the fetched html, extract text
from bs4 import BeautifulSoup

def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    #get article content
    main = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", {"data-testid": "post-container"})
        or soup.body
    )

    if not main:
        return ""

    text = main.get_text(separator=" ", strip=True)

    # Clean whitespace
    text = " ".join(text.split())
    print("EXTRACTED TEXT LENGTH:", len(text))

    if len(text) < 50:
        return ""

    return text
