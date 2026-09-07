from src.parallel_api import ParallelGrantSearch

searcher = ParallelGrantSearch()
results = searcher.search("drama filmmaker grants")
print(f"Found {len(results)} results")
for r in results:
    print(f"- {r['title']}")
    print(f"  {r['url']}")

