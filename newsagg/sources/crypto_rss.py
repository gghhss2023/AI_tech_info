import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

FEEDS = [
    ("https://www.coindesk.com/arc/outboundfeeds/rss/", "CoinDesk"),
    ("https://cointelegraph.com/rss", "CoinTelegraph"),
    ("https://decrypt.co/feed", "Decrypt"),
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
                        id=f"crypto_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="crypto",
                        lang="en",
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        tags=[name, "crypto", "web3"],
                    ))
            except Exception:
                continue
    return articles[:limit]
