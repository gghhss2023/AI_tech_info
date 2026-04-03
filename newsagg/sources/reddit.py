import httpx
from ..models import Article

SUBREDDITS = {
    "en": ["technology", "artificial", "MachineLearning", "worldnews"],
    "zh": ["China", "ChineseLanguage"],
    "ja": ["japan", "japanese"],
}

HEADERS = {"User-Agent": "newsagg/1.0 (daily digest sdk)"}


async def fetch(lang: str = "en", limit: int = 10) -> list[Article]:
    subs = SUBREDDITS.get(lang, SUBREDDITS["en"])
    articles = []

    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        for sub in subs:
            try:
                resp = await client.get(
                    f"https://www.reddit.com/r/{sub}/hot.json",
                    params={"limit": limit},
                )
                data = resp.json()
                for post in data.get("data", {}).get("children", []):
                    p = post["data"]
                    if p.get("is_self") or not p.get("url"):
                        continue
                    articles.append(Article(
                        id=f"reddit_{p['id']}",
                        title=p.get("title", ""),
                        url=p.get("url", ""),
                        source="reddit",
                        lang=lang,
                        published_at=str(int(p.get("created_utc", 0))),
                        author=p.get("author"),
                        summary=p.get("selftext", "")[:200] or None,
                        score=p.get("score"),
                        comments=p.get("num_comments"),
                        tags=[sub],
                        raw=p,
                    ))
            except Exception:
                continue

    return articles
