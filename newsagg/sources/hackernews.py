import httpx
from ..models import Article


async def fetch(limit: int = 20) -> list[Article]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        ids = resp.json()[:limit]

        articles = []
        for item_id in ids:
            try:
                r = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json")
                item = r.json()
                if not item or item.get("type") != "story" or not item.get("url"):
                    continue
                articles.append(Article(
                    id=f"hn_{item_id}",
                    title=item.get("title", ""),
                    url=item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                    source="hackernews",
                    lang="en",
                    published_at=str(item.get("time", "")),
                    author=item.get("by"),
                    score=item.get("score"),
                    comments=item.get("descendants"),
                    raw=item,
                ))
            except Exception:
                continue
        return articles
