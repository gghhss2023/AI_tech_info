from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    id: str
    title: str
    url: str
    source: str          # hackernews | reddit | github | x | news_en | news_zh | news_ja
    lang: str            # en | zh | ja
    published_at: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    score: Optional[int] = None
    comments: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DigestResult:
    generated_at: str
    total: int
    sources: list[str]
    articles: list[Article]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "total": self.total,
            "sources": self.sources,
            "articles": [a.to_dict() for a in self.articles],
        }
