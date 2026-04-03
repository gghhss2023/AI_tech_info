import httpx
from ..models import Article

# YouTube Data API v3 - requires API key
# Falls back to RSS for specific channels if no key provided

TECH_CHANNELS = {
    "UCVHFbw7woebKtfvug_tEqjA": "Fireship",
    "UCnUYZLuoy1rq1aVMwx4aTzw": "Google",
    "UC0RhatS1pyxInC00YKjjBqQ": "Marques Brownlee",
}


async def fetch(limit: int = 10, api_key: str = "") -> list[Article]:
    articles = []

    if api_key:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.get(
                    "https://www.googleapis.com/youtube/v3/videos",
                    params={
                        "part": "snippet,statistics",
                        "chart": "mostPopular",
                        "videoCategoryId": "28",  # Science & Technology
                        "maxResults": limit,
                        "key": api_key,
                    },
                )
                for item in resp.json().get("items", [])[:limit]:
                    vid_id = item["id"]
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    articles.append(Article(
                        id=f"yt_{vid_id}",
                        title=snippet.get("title", ""),
                        url=f"https://www.youtube.com/watch?v={vid_id}",
                        source="youtube",
                        lang="en",
                        published_at=snippet.get("publishedAt"),
                        author=snippet.get("channelTitle"),
                        summary=snippet.get("description", "")[:200] or None,
                        score=int(stats.get("viewCount", 0)),
                        comments=int(stats.get("commentCount", 0)),
                        tags=["video", "youtube"],
                    ))
            except Exception:
                pass
    else:
        # RSS fallback for tech channels
        async with httpx.AsyncClient(timeout=10) as client:
            import xml.etree.ElementTree as ET
            import hashlib
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for channel_id, channel_name in list(TECH_CHANNELS.items())[:2]:
                try:
                    resp = await client.get(
                        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    )
                    root = ET.fromstring(resp.text)
                    for entry in root.findall("atom:entry", ns)[:limit // 2]:
                        title = entry.findtext("atom:title", "", ns).strip()
                        link = entry.find("atom:link", ns)
                        url = link.get("href", "") if link is not None else ""
                        pub = entry.findtext("atom:published", "", ns)
                        if not title or not url:
                            continue
                        articles.append(Article(
                            id=f"yt_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                            title=title,
                            url=url,
                            source="youtube",
                            lang="en",
                            published_at=pub or None,
                            author=channel_name,
                            tags=["video", "youtube", channel_name],
                        ))
                except Exception:
                    continue

    return articles[:limit]
