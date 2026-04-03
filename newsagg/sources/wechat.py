import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

# 搜狗微信热门文章 RSS
SOGOU_RSS = "https://weixin.sogou.com/weixin?type=2&query=科技&ie=utf8&_sug_=n&_sug_type_=&w=01019900&sut=0&sst0=1700000000&lkt=0,0,0&s_from=input&_sug_=n"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

# 公众号 RSS via RSSHub（需要 RSSHub 实例，默认用公共节点）
WECHAT_FEEDS = [
    ("https://rsshub.app/wechat/mp/1217615494", "爱范儿iPhoneHacks"),  # 示例账号
]


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10, headers=HEADERS, follow_redirects=True) as client:
        for feed_url, name in WECHAT_FEEDS:
            try:
                resp = await client.get(feed_url)
                root = ET.fromstring(resp.text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}

                for item in root.findall(".//item")[:limit]:
                    title = item.findtext("title", "").strip()
                    url = item.findtext("link", "").strip()
                    pub = item.findtext("pubDate", "")
                    desc = item.findtext("description", "")
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"wechat_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="wechat",
                        lang="zh",
                        published_at=pub or None,
                        summary=desc[:200] if desc else None,
                        tags=["微信公众号", name],
                    ))
            except Exception:
                continue
    return articles[:limit]
