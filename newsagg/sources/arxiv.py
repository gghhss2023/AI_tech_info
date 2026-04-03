import hashlib
import httpx
import xml.etree.ElementTree as ET
from ..models import Article

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL"]
BASE_URL = "http://export.arxiv.org/api/query"


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=15) as client:
        for cat in CATEGORIES[:2]:
            try:
                resp = await client.get(
                    BASE_URL,
                    params={
                        "search_query": f"cat:{cat}",
                        "sortBy": "submittedDate",
                        "sortOrder": "descending",
                        "max_results": limit // 2 + 1,
                    },
                )
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                root = ET.fromstring(resp.text)
                for entry in root.findall("atom:entry", ns):
                    title = entry.findtext("atom:title", "", ns).strip().replace("\n", " ")
                    url = entry.findtext("atom:id", "", ns).strip()
                    pub = entry.findtext("atom:published", "", ns)
                    summary = entry.findtext("atom:summary", "", ns).strip()[:200]
                    authors = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)]
                    if not title or not url:
                        continue
                    articles.append(Article(
                        id=f"arxiv_{hashlib.md5(url.encode()).hexdigest()[:12]}",
                        title=title,
                        url=url,
                        source="arxiv",
                        lang="en",
                        published_at=pub or None,
                        author=", ".join(authors[:3]),
                        summary=summary or None,
                        tags=[cat],
                    ))
            except Exception:
                continue
    return articles[:limit]
