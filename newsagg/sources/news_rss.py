import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

RSS_FEEDS = {
    "en": [
        ("https://feeds.bbci.co.uk/news/technology/rss.xml", "BBC Tech"),
        ("https://techcrunch.com/feed/", "TechCrunch"),
        ("https://www.theverge.com/rss/index.xml", "The Verge"),
        ("https://www.wired.com/feed/rss", "Wired"),
        ("https://feeds.arstechnica.com/arstechnica/index", "Ars Technica"),
        ("https://feeds.feedburner.com/mit-technology-review/","MIT Tech Review"),
        ("https://medium.com/feed/tag/technology", "Medium Tech"),
        ("https://substackcdn.com/api/v1/feed", "Substack"),
    ],
    "zh": [
        ("https://www.36kr.com/feed", "36Kr"),
        ("https://sspai.com/feed", "少数派"),
        ("https://www.ifanr.com/feed", "爱范儿"),
        ("https://www.huxiu.com/rss/0.xml", "虎嗅"),
        ("https://www.tmtpost.com/feed", "钛媒体"),
        ("https://www.infoq.cn/feed", "InfoQ中文"),
        ("https://zhihu.com/rss", "知乎热榜"),
    ],
    "ja": [
        ("https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml", "ITmedia"),
        ("https://gigazine.net/news/rss_2.0/", "Gigazine"),
        ("https://www.publickey1.jp/atom.xml", "Publickey"),
        ("https://note.com/hashtag/テクノロジー?format=rss", "note.com"),
    ],
}


def _parse_feed(xml_text: str, source_name: str, lang: str) -> list[Article]:
    articles = []
    try:
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # RSS 2.0
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            url = item.findtext("link", "").strip()
            pub = item.findtext("pubDate", "")
            desc = item.findtext("description", "")
            if not title or not url:
                continue
            articles.append(Article(
                id=f"rss_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                title=title,
                url=url,
                source=f"news_{lang}",
                lang=lang,
                published_at=pub or None,
                summary=desc[:200] if desc else None,
                tags=[source_name],
            ))

        # Atom
        for entry in root.findall(".//atom:entry", ns):
            title = entry.findtext("atom:title", "", ns).strip()
            link = entry.find("atom:link", ns)
            url = link.get("href", "") if link is not None else ""
            pub = entry.findtext("atom:published", "", ns)
            summary = entry.findtext("atom:summary", "", ns)
            if not title or not url:
                continue
            articles.append(Article(
                id=f"rss_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                title=title,
                url=url,
                source=f"news_{lang}",
                lang=lang,
                published_at=pub or None,
                summary=summary[:200] if summary else None,
                tags=[source_name],
            ))
    except Exception:
        pass
    return articles


async def fetch(lang: str = "en", limit: int = 10) -> list[Article]:
    feeds = RSS_FEEDS.get(lang, RSS_FEEDS["en"])
    articles = []

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for url, name in feeds:
            try:
                resp = await client.get(url)
                parsed = _parse_feed(resp.text, name, lang)
                articles.extend(parsed[:limit])
            except Exception:
                continue

    return articles[:limit * len(feeds)]
