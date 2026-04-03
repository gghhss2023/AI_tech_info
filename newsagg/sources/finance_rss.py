import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

FEEDS = {
    "en": [
        ("https://feeds.reuters.com/reuters/technologyNews", "Reuters Tech"),
        ("https://feeds.bloomberg.com/technology/news.rss", "Bloomberg Tech"),
        ("https://feeds.wsj.com/xml/rss/3_7085.xml", "WSJ Tech"),
    ],
    "zh": [
        ("https://www.cls.cn/api/sw?app=CLS-ARTICLE&os=mac&sv=7.7.5&rss=1", "财联社"),
        ("https://wallstreetcn.com/feed", "华尔街见闻"),
    ],
}


async def fetch(lang: str = "en", limit: int = 10) -> list[Article]:
    feeds = FEEDS.get(lang, FEEDS["en"])
    articles = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for feed_url, name in feeds:
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
                        id=f"finance_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source=f"finance_{lang}",
                        lang=lang,
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        tags=[name, "finance"],
                    ))
            except Exception:
                continue
    return articles[:limit]
