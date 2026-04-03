import httpx
from ..models import Article

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        try:
            # 热门视频
            resp = await client.get(
                "https://api.bilibili.com/x/web-interface/popular",
                params={"ps": limit, "pn": 1},
            )
            data = resp.json()
            for item in data.get("data", {}).get("list", [])[:limit]:
                articles.append(Article(
                    id=f"bili_{item.get('bvid', item.get('aid', ''))}",
                    title=item.get("title", ""),
                    url=f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    source="bilibili",
                    lang="zh",
                    author=item.get("owner", {}).get("name"),
                    summary=item.get("desc", "")[:200] or None,
                    score=item.get("stat", {}).get("view"),
                    comments=item.get("stat", {}).get("reply"),
                    tags=[item.get("tname", "")],
                ))
        except Exception:
            pass
    return articles
