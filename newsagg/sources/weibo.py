import hashlib
import httpx
from ..models import Article

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://weibo.com/",
}


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        try:
            resp = await client.get(
                "https://weibo.com/ajax/side/hotSearch",
            )
            data = resp.json()
            items = data.get("data", {}).get("realtime", [])
            for item in items[:limit]:
                word = item.get("word", "")
                if not word:
                    continue
                url = f"https://s.weibo.com/weibo?q=%23{word}%23"
                articles.append(Article(
                    id=f"weibo_{hashlib.md5(word.encode()).hexdigest()[:12]}",
                    title=f"#{word}#",
                    url=url,
                    source="weibo",
                    lang="zh",
                    score=item.get("num"),
                    tags=["微博热搜", item.get("category", "")],
                ))
        except Exception:
            pass
    return articles
