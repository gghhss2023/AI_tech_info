import httpx
from ..models import Article


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                "https://paperswithcode.com/api/v1/papers/",
                params={"ordering": "-arxiv_id", "page_size": limit},
            )
            for item in resp.json().get("results", [])[:limit]:
                url = f"https://paperswithcode.com/paper/{item.get('arxiv_id', item.get('id', ''))}"
                articles.append(Article(
                    id=f"pwc_{item.get('id', '')}",
                    title=item.get("title", ""),
                    url=url,
                    source="paperswithcode",
                    lang="en",
                    published_at=item.get("published"),
                    summary=item.get("abstract", "")[:200] or None,
                    score=item.get("stars"),
                    tags=["ML", "AI", "research"],
                ))
        except Exception:
            pass
    return articles
