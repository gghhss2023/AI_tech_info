import httpx
from ..models import Article

GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"
QUERY = """
{
  posts(first: 20, order: VOTES) {
    edges {
      node {
        id
        name
        tagline
        url
        votesCount
        commentsCount
        createdAt
        topics { edges { node { name } } }
      }
    }
  }
}
"""


async def fetch(limit: int = 10) -> list[Article]:
    articles = []
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(
                GRAPHQL_URL,
                json={"query": QUERY},
                headers={"Content-Type": "application/json"},
            )
            edges = resp.json().get("data", {}).get("posts", {}).get("edges", [])
            for edge in edges[:limit]:
                node = edge["node"]
                topics = [e["node"]["name"] for e in node.get("topics", {}).get("edges", [])]
                articles.append(Article(
                    id=f"ph_{node['id']}",
                    title=node.get("name", ""),
                    url=node.get("url", ""),
                    source="producthunt",
                    lang="en",
                    published_at=node.get("createdAt"),
                    summary=node.get("tagline"),
                    score=node.get("votesCount"),
                    comments=node.get("commentsCount"),
                    tags=topics,
                ))
        except Exception:
            pass
    return articles
