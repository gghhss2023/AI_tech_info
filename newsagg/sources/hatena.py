import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

FEEDS = [
    ("https://b.hatena.ne.jp/hotentry/it.rss", "はてな IT"),
    ("https://b.hatena.ne.jp/hotentry/general.rss", "はてな総合"),
]


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for feed_url, name in FEEDS:
            try:
                resp = await client.get(feed_url)
                root = ET.fromstring(resp.text)
                ns = {
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "rss": "http://purl.org/rss/1.0/",
                    "dc": "http://purl.org/dc/elements/1.1/",
                    "hatena": "http://www.hatena.ne.jp/info/xmlns#",
                }
                for item in root.findall("rss:item", ns)[:limit]:
                    title = item.findtext("rss:title", "", ns).strip()
                    url = item.findtext("rss:link", "", ns).strip()
                    pub = item.findtext("dc:date", "", ns)
                    desc = item.findtext("rss:description", "", ns)
                    bookmarks = item.findtext("hatena:bookmarkcount", "", ns)
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"hatena_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="hatena",
                        lang="ja",
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        score=int(bookmarks) if bookmarks.isdigit() else None,
                        tags=[name],
                    ))
            except Exception:
                continue
    return articles[:limit]
