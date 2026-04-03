import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

FEEDS = [
    ("https://feeds.feedburner.com/etnews/total", "전자신문"),
    ("https://rss.zdnet.co.kr/rss", "ZDNet Korea"),
    ("https://www.itworld.co.kr/rss/feed", "ITWorld Korea"),
]


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for feed_url, name in FEEDS:
            try:
                resp = await client.get(feed_url)
                root = ET.fromstring(resp.text)
                for item in root.findall(".//item")[:limit]:
                    title = item.findtext("title", "").strip()
                    url = item.findtext("link", "").strip()
                    pub = item.findtext("pubDate", "")
                    desc = item.findtext("description", "")
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"kr_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="news_ko",
                        lang="ko",
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        tags=[name],
                    ))
            except Exception:
                continue
    return articles[:limit]
