import hashlib
import re
from .models import Article


def _normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def _title_hash(title: str) -> str:
    return hashlib.md5(_normalize_title(title).encode()).hexdigest()


def _url_domain(url: str) -> str:
    match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return match.group(1) if match else url


def dedup(articles: list[Article], similarity_threshold: int = 8) -> list[Article]:
    seen_ids: set[str] = set()
    seen_title_hashes: set[str] = set()
    result = []

    for article in articles:
        if article.id in seen_ids:
            continue

        th = _title_hash(article.title)
        if th in seen_title_hashes:
            continue

        seen_ids.add(article.id)
        seen_title_hashes.add(th)
        result.append(article)

    return result


def sort_articles(
    articles: list[Article],
    by: str = "score",
    lang_priority: list[str] | None = None,
) -> list[Article]:
    """
    by: 'score' | 'time' | 'mixed'
    mixed = weighted score: normalized_score * 0.6 + recency * 0.4
    """
    if by == "time":
        return sorted(articles, key=lambda a: a.published_at or "", reverse=True)

    if by == "score":
        return sorted(articles, key=lambda a: a.score or 0, reverse=True)

    if by == "mixed":
        import time
        from datetime import datetime, timezone

        def parse_ts(pub: str | None) -> float:
            if not pub:
                return 0.0
            try:
                if pub.isdigit():
                    return float(pub)
                for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00",
                            "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S.%f+00:00"):
                    try:
                        return datetime.strptime(pub, fmt).timestamp()
                    except ValueError:
                        continue
            except Exception:
                pass
            return 0.0

        now = time.time()
        max_score = max((a.score or 0 for a in articles), default=1) or 1

        def mixed_key(a: Article) -> float:
            norm_score = (a.score or 0) / max_score
            ts = parse_ts(a.published_at)
            age_hours = (now - ts) / 3600 if ts else 168
            recency = max(0.0, 1.0 - age_hours / 168)  # decay over 7 days
            return norm_score * 0.6 + recency * 0.4

        sorted_articles = sorted(articles, key=mixed_key, reverse=True)

        if lang_priority:
            def lang_key(a: Article) -> int:
                try:
                    return lang_priority.index(a.lang)
                except ValueError:
                    return len(lang_priority)
            sorted_articles = sorted(sorted_articles, key=lang_key)

        return sorted_articles

    return articles
