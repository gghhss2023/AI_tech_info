import httpx
from ..models import Article


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get("https://lobste.rs/hottest.json")
            for item in resp.json()[:limit]:
                articles.append(Article(
                    id=f"lobsters_{item.get('short_id', '')}",
                    title=item.get("title", ""),
                    url=item.get("url") or f"https://lobste.rs/s/{item.get('short_id', '')}",
                    source="lobsters",
                    lang="en",
                    published_at=item.get("created_at"),
                    author=item.get("submitter_user", {}).get("username"),
                    score=item.get("score"),
                    comments=item.get("comment_count"),
                    tags=item.get("tags", []),
                ))
        except Exception:
            pass
    return articles
