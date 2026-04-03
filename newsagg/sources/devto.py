import httpx
from ..models import Article


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                "https://dev.to/api/articles",
                params={"top": 1, "per_page": limit},
            )
            for item in resp.json()[:limit]:
                articles.append(Article(
                    id=f"devto_{item['id']}",
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source="devto",
                    lang="en",
                    published_at=item.get("published_at"),
                    author=item.get("user", {}).get("name"),
                    summary=item.get("description", "")[:200] or None,
                    score=item.get("positive_reactions_count"),
                    comments=item.get("comments_count"),
                    tags=item.get("tag_list", []),
                ))
        except Exception:
            pass
    return articles
