import httpx
from ..models import Article

HEADERS = {"Accept": "application/vnd.github+json"}


async def fetch(lang: str = "en", limit: int = 10) -> list[Article]:
    spoken_lang = {"en": None, "zh": "zh", "ja": "ja"}.get(lang)
    params = {"since": "daily"}
    if spoken_lang:
        params["spoken_language_code"] = spoken_lang

    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        try:
            resp = await client.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": f"created:>2026-04-01{' language:' + spoken_lang if spoken_lang else ''}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": limit,
                },
            )
            items = resp.json().get("items", [])
        except Exception:
            return []

    articles = []
    for repo in items:
        articles.append(Article(
            id=f"github_{repo['id']}",
            title=repo.get("full_name", ""),
            url=repo.get("html_url", ""),
            source="github",
            lang=lang,
            published_at=repo.get("created_at"),
            author=repo.get("owner", {}).get("login"),
            summary=repo.get("description"),
            score=repo.get("stargazers_count"),
            tags=[repo.get("language")] if repo.get("language") else [],
            raw=repo,
        ))
    return articles
