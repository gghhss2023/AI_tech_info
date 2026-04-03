import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

FEEDS = [
    ("https://www.detik.com/inet/rss.xml", "Detik Inet"),
    ("https://tekno.kompas.com/rss/2014/07/22/rss2.0.xml", "Kompas Tekno"),
    ("https://www.techinasia.com/feed", "Tech in Asia"),
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
                        id=f"id_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="news_id",
                        lang="id",
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        tags=[name],
                    ))
            except Exception:
                continue
    return articles[:limit]
