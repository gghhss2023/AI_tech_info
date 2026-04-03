import asyncio
import json
from datetime import datetime, timezone
from typing import Optional

from .models import DigestResult
from .dedup import dedup, sort_articles
from .sources import (
    hackernews, reddit, github, news_rss, medium, zhihu,
    weibo, bilibili, wechat, producthunt, hatena, devto,
    arxiv, finance_rss, lobsters, paperswithcode, crypto_rss,
    tech_rss_extra, korea, indonesia, youtube,
)

AVAILABLE_SOURCES = [
    "hackernews", "reddit", "github", "news_en", "news_zh", "news_ja",
    "medium", "zhihu", "weibo", "bilibili", "wechat",
    "producthunt", "hatena", "devto", "arxiv",
    "finance_en", "finance_zh", "lobsters",
    "paperswithcode", "crypto", "tech_en_extra",
    "news_ko", "news_id", "youtube",
]


async def fetch_all(
    sources: Optional[list[str]] = None,
    limit_per_source: int = 10,
    langs: Optional[list[str]] = None,
    sort_by: str = "mixed",
    lang_priority: Optional[list[str]] = None,
) -> DigestResult:
    if sources is None:
        sources = AVAILABLE_SOURCES
    if langs is None:
        langs = ["en", "zh", "ja"]

    tasks = []

    if "hackernews" in sources:
        tasks.append(hackernews.fetch(limit=limit_per_source))

    if "reddit" in sources:
        for lang in langs:
            tasks.append(reddit.fetch(lang=lang, limit=limit_per_source))

    if "github" in sources:
        for lang in langs:
            tasks.append(github.fetch(lang=lang, limit=limit_per_source))

    for lang in langs:
        key = f"news_{lang}"
        if key in sources:
            tasks.append(news_rss.fetch(lang=lang, limit=limit_per_source))

    if "medium" in sources:
        tasks.append(medium.fetch(limit=limit_per_source))

    if "zhihu" in sources:
        tasks.append(zhihu.fetch(limit=limit_per_source))

    if "weibo" in sources:
        tasks.append(weibo.fetch(limit=limit_per_source))

    if "bilibili" in sources:
        tasks.append(bilibili.fetch(limit=limit_per_source))

    if "wechat" in sources:
        tasks.append(wechat.fetch(limit=limit_per_source))

    if "producthunt" in sources:
        tasks.append(producthunt.fetch(limit=limit_per_source))

    if "hatena" in sources:
        tasks.append(hatena.fetch(limit=limit_per_source))

    if "devto" in sources:
        tasks.append(devto.fetch(limit=limit_per_source))

    if "arxiv" in sources:
        tasks.append(arxiv.fetch(limit=limit_per_source))

    if "lobsters" in sources:
        tasks.append(lobsters.fetch(limit=limit_per_source))

    for lang in langs:
        key = f"finance_{lang}"
        if key in sources:
            tasks.append(finance_rss.fetch(lang=lang, limit=limit_per_source))

    if "paperswithcode" in sources:
        tasks.append(paperswithcode.fetch(limit=limit_per_source))

    if "crypto" in sources:
        tasks.append(crypto_rss.fetch(limit=limit_per_source))

    if "tech_en_extra" in sources:
        tasks.append(tech_rss_extra.fetch(limit=limit_per_source))

    if "news_ko" in sources:
        tasks.append(korea.fetch(limit=limit_per_source))

    if "news_id" in sources:
        tasks.append(indonesia.fetch(limit=limit_per_source))

    if "youtube" in sources:
        tasks.append(youtube.fetch(limit=limit_per_source))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    articles = []
    active_sources = []
    for result in results:
        if isinstance(result, list) and result:
            articles.extend(result)
            src = result[0].source
            if src not in active_sources:
                active_sources.append(src)

    articles = dedup(articles)
    articles = sort_articles(articles, by=sort_by, lang_priority=lang_priority)

    return DigestResult(
        generated_at=datetime.now(timezone.utc).isoformat(),
        total=len(articles),
        sources=active_sources,
        articles=articles,
    )


def run(
    sources: Optional[list[str]] = None,
    limit_per_source: int = 10,
    langs: Optional[list[str]] = None,
    sort_by: str = "mixed",
    lang_priority: Optional[list[str]] = None,
    output_file: Optional[str] = None,
) -> DigestResult:
    result = asyncio.run(fetch_all(
        sources=sources,
        limit_per_source=limit_per_source,
        langs=langs,
        sort_by=sort_by,
        lang_priority=lang_priority,
    ))

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

    return result
