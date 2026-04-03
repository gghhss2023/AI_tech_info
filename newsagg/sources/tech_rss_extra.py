import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

FEEDS = [
    ("https://www.infoq.com/feed/", "InfoQ EN"),
    ("https://www.theregister.com/headlines.atom", "The Register"),
    ("https://www.zdnet.com/news/rss.xml", "ZDNet"),
    ("https://www.engadget.com/rss.xml", "Engadget"),
    ("https://arstechnica.com/gadgets/feed/", "Ars Gadgets"),
]


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for feed_url, name in FEEDS:
            try:
                resp = await client.get(feed_url)
                root = ET.fromstring(resp.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}

                # RSS 2.0
                for item in root.findall(".//item")[:limit // len(FEEDS) + 1]:
                    title = item.findtext("title", "").strip()
                    url = item.findtext("link", "").strip()
                    pub = item.findtext("pubDate", "")
                    desc = item.findtext("description", "")
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"tech_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="tech_en",
                        lang="en",
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        tags=[name],
                    ))

                # Atom
                for entry in root.findall("atom:entry", ns)[:limit // len(FEEDS) + 1]:
                    title = entry.findtext("atom:title", "", ns).strip()
                    link = entry.find("atom:link", ns)
                    url = link.get("href", "") if link is not None else ""
                    pub = entry.findtext("atom:updated", "", ns)
                    summary = entry.findtext("atom:summary", "", ns)
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"tech_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="tech_en",
                        lang="en",
                        published_at=pub or None,
                        summary=summary[:200] if summary else None,
                        tags=[name],
                    ))
            except Exception:
                continue
    return articles[:limit]
