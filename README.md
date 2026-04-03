# AI_tech_info — All-in-One News Aggregator SDK

A Python SDK that aggregates tech and AI news from 22+ sources across EN / ZH / JA / KO / ID — with deduplication, sorting, and CLI support.

## Sources

| Source | Language | Category |
|--------|----------|----------|
| HackerNews | EN | Tech |
| Reddit | EN / ZH / JA | Social |
| GitHub Trending | EN / ZH / JA | Dev |
| Medium | EN | Blog |
| Dev.to | EN | Blog |
| Lobsters | EN | Tech |
| Product Hunt | EN | Products |
| ArXiv (AI/ML/NLP) | EN | Research |
| Papers with Code | EN | Research |
| BBC / TechCrunch / The Verge / Wired / Ars Technica / MIT Tech Review | EN | News |
| InfoQ / The Register / ZDNet / Engadget | EN | Tech News |
| Reuters / Bloomberg / WSJ | EN | Finance |
| CoinDesk / CoinTelegraph / Decrypt | EN | Crypto |
| YouTube (Tech) | EN | Video |
| 36Kr / 少数派 / 虎嗅 / 钛媒体 / InfoQ中文 | ZH | Tech News |
| 微博热搜 | ZH | Social |
| B站热门 | ZH | Video |
| 微信公众号 (via RSSHub) | ZH | Blog |
| 财联社 / 华尔街见闻 | ZH | Finance |
| 知乎热榜 | ZH | Q&A |
| ITmedia / Gigazine / Publickey / はてなブックマーク | JA | Tech |
| 전자신문 / ZDNet Korea / ITWorld Korea | KO | Tech |
| Detik / Kompas Tekno / Tech in Asia | ID | Tech |

## Install

```bash
pip install -e .
```

## CLI Usage

```bash
# Fetch all sources, mixed sort, save to file
newsagg --sort mixed --limit 10 -o digest.json

# Chinese-first, top sources only
newsagg --sources hackernews weibo bilibili news_zh --lang-priority zh en --limit 20

# AI research focus
newsagg --sources arxiv paperswithcode hackernews devto --sort time --limit 15

# Available sort modes
#   mixed  = score (60%) + recency (40%)  [default]
#   score  = by upvotes/views
#   time   = latest first
```

## Python Usage

```python
import newsagg

# Quick run
result = newsagg.run(
    sources=["hackernews", "weibo", "arxiv"],
    langs=["en", "zh"],
    limit_per_source=10,
    sort_by="mixed",
    lang_priority=["zh", "en"],
    output_file="digest.json",
)

print(f"{result.total} articles from {result.sources}")

# Async
import asyncio
result = asyncio.run(newsagg.fetch_all(sources=["hackernews"], langs=["en"]))
```

## Output Format

```json
{
  "generated_at": "2026-04-03T10:00:00+00:00",
  "total": 42,
  "sources": ["hackernews", "weibo", "arxiv"],
  "articles": [
    {
      "id": "hn_12345",
      "title": "Article title",
      "url": "https://...",
      "source": "hackernews",
      "lang": "en",
      "published_at": "2026-04-03T08:00:00Z",
      "author": "username",
      "summary": "...",
      "score": 342,
      "comments": 87,
      "tags": ["ai", "llm"]
    }
  ]
}
```

## Available Sources

```
hackernews  reddit      github      news_en     news_zh     news_ja
medium      zhihu       weibo       bilibili    wechat      producthunt
hatena      devto       arxiv       finance_en  finance_zh  lobsters
paperswithcode  crypto  tech_en_extra  news_ko  news_id    youtube
```

## License

MIT
