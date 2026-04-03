import argparse
import json
import sys
from .aggregator import run
from .aggregator import AVAILABLE_SOURCES


def main():
    parser = argparse.ArgumentParser(description="NewsAgg - Daily Digest SDK")
    parser.add_argument("--sources", nargs="+", choices=AVAILABLE_SOURCES, help="Sources to fetch")
    parser.add_argument("--langs", nargs="+", choices=["en", "zh", "ja", "ko", "id"], default=["en", "zh", "ja"])
    parser.add_argument("--limit", type=int, default=10, help="Articles per source")
    parser.add_argument("--sort", choices=["mixed", "score", "time"], default="mixed")
    parser.add_argument("--lang-priority", nargs="+", choices=["en", "zh", "ja", "ko", "id"])
    parser.add_argument("--output", "-o", help="Save JSON to file")
    args = parser.parse_args()

    result = run(
        sources=args.sources,
        limit_per_source=args.limit,
        langs=args.langs,
        sort_by=args.sort,
        lang_priority=args.lang_priority,
        output_file=args.output,
    )

    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    print(f"\n✓ {result.total} articles from {len(result.sources)} sources", file=sys.stderr)


if __name__ == "__main__":
    main()
