import hashlib
import httpx
from ..models import Article

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        try:
            resp = await client.get(
                "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total",
                params={"limit": limit},
            )
            data = resp.json()
            for item in data.get("data", [])[:limit]:
                target = item.get("target", {})
                title = target.get("title") or target.get("question", {}).get("title", "")
                url = f"https://www.zhihu.com/question/{target.get('id', '')}"
                if not title:
                    continue
                articles.append(Article(
                    id=f"zhihu_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                    title=title,
                    url=url,
                    source="zhihu",
                    lang="zh",
                    summary=target.get("excerpt", "")[:200] or None,
                    score=item.get("detail_text"),
                    tags=["知乎热榜"],
                ))
        except Exception:
            pass
    return articles
