import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

TAGS = ["artificial-intelligence", "technology", "programming", "data-science", "startup"]


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for tag in TAGS[:3]:
            try:
                resp = await client.get(f"https://medium.com/feed/tag/{tag}")
                root = ET.fromstring(resp.text)
                for item in root.findall(".//item")[:limit // 3 + 1]:
                    title = item.findtext("title", "").strip()
                    url = item.findtext("link", "").strip()
                    pub = item.findtext("pubDate", "")
                    author = item.findtext("{http://purl.org/dc/elements/1.1/}creator", "")
                    desc = item.findtext("description", "")
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"medium_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="medium",
                        lang="en",
                        published_at=pub or None,
                        author=author or None,
                        summary=desc[:200] if desc else None,
                        tags=[tag],
                    ))
            except Exception:
                continue
    return articles[:limit]
