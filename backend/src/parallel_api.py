"""
FILMFUND - Parallel Search API Integration

Live film funding discovery using the Parallel Search API.

50 Comprehensive Global Search Queries:
- Geographic: USA, Africa, Europe, Asia, Canada, UK, Latin America, Middle East
- Genres: Drama, Documentary, Indie, Short, Comedy, Thriller, Sci-Fi, Animation, etc.
- Budget: $50k, $100k, $250k, $500k, $1M+
- Filmmaker Level: Beginner, Emerging, Professional, First-Time
- Special: Festivals, Labs, Residencies, Development, Production, Post-Production

Goals:
- Real live web search
- Worldwide coverage
- 2026 and 2027 opportunities
- All major film genres and budgets
- Preserve source evidence
- Never create/mock funding opportunities
"""

from parallel import Parallel
import logging
import os
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ParallelGrantSearch:
    """Search for real film funding opportunities using Parallel Search API."""

    ENDPOINT = "https://api.parallel.ai/v1/search"

    # ============================================================
    # 50 COMPREHENSIVE SEARCH QUERIES
    # ============================================================

    SEARCH_QUERIES = [
        # --------------------------------------------------------
        # GEOGRAPHIC COVERAGE (10)
        # --------------------------------------------------------
        "international film grants worldwide",
        "USA film grants",
        "USA film grant",
        "African film grants",
        "European film grants",
        "Asian film grants",
        "Canadian film grants",
        "UK film grants",
        "Latin American film grants",
        "Middle East film grants",

        # --------------------------------------------------------
        # FILM GENRES (15)
        # --------------------------------------------------------
        "drama film grants",
        "documentary filmmaker grants",
        "independent film funding",
        "short film grants",
        "comedy film grants",
        "thriller film grants",
        "science fiction film grants",
        "animation film grants",
        "experimental film grants",
        "horror film grants",
        "romance film grants",
        "action film grants",
        "fantasy film grants",
        "family film grants",
        "crime film grants",

        # --------------------------------------------------------
        # BUDGET & FILMMAKER LEVEL (10)
        # --------------------------------------------------------
        "low budget film grants",
        "micro budget film funding",
        "$100k film grants",
        "$250k film production funding",
        "$500k film grants",
        "$1M film grants",
        "emerging filmmaker grants",
        "beginner filmmaker grants",
        "professional filmmaker grants",
        "first time filmmaker grants",

        # --------------------------------------------------------
        # SPECIAL PROGRAMS (10)
        # --------------------------------------------------------
        "film development grants",
        "film production grants",
        "post production film funding",
        "film production fellowships",
        "film residency programs",
        "screenplay grants",
        "film labs funding",
        "film fund competitions",
        "film financing opportunities",
        "documentary film funding",

        # --------------------------------------------------------
        # PRIORITY & VERIFICATION (5)
        # --------------------------------------------------------
        "film grants 2026 2027",
        "independent film production grants",
        "real film funding opportunities",
        "legitimate film grants",
        "international filmmaker funding opportunities",
    ]

    # ============================================================
    # REGIONAL SEARCH COVERAGE
    # ============================================================

    REGIONS = [
        "USA",
        "Africa",
        "Worldwide",
        "International",
    ]

    def __init__(self):
        """
        Initialize the Parallel Search client.

        The API key must be supplied through the environment:
        PARALLEL_API_KEY
        """

        self.api_key = os.getenv("PARALLEL_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "PARALLEL_API_KEY is not configured in the environment."
            )

        logger.info(
            "[ParallelAPI] Initialized with %d search queries",
            len(self.SEARCH_QUERIES),
        )

        try:
            self.client = Parallel(api_key=self.api_key)
            logger.info("[ParallelAPI] Parallel SDK client created")

        except Exception as e:
            logger.warning(
                "[ParallelAPI] Could not initialize Parallel SDK: %s",
                e,
            )
            self.client = None

    # ============================================================
    # MAIN SEARCH
    # ============================================================

    def search(self, query: str = None) -> list[dict[str, Any]]:
        """
        Search for real film funding opportunities.

        If a user query is supplied, it is added to the 50
        predefined funding searches.

        Returns deduplicated results.
        """

        if query and query.strip():
            search_queries = [query.strip()] + self.SEARCH_QUERIES
        else:
            search_queries = self.SEARCH_QUERIES.copy()

        logger.info(
            "[ParallelAPI] Starting search with %d queries",
            len(search_queries),
        )

        all_results: list[dict[str, Any]] = []

        # ========================================================
        # PARALLEL SDK SEARCH
        # ========================================================

        if self.client:

            try:
                logger.info("[ParallelAPI] Using Parallel SDK client")

                objective = (
                    "Find REAL, currently published film funding opportunities "
                    "matching filmmaker requests. "
                    "Prioritize opportunities for 2026 or 2027 funding cycles. "
                    "Look for genuine grants, film funds, production funds, "
                    "development funds, fellowships, residencies, labs, "
                    "competitions, and prizes. "
                    "The opportunity must be real and supported by source evidence. "
                    "Prefer official funder, foundation, film institute, "
                    "government, festival, or established film organization websites. "
                    "Do not fabricate deadlines, eligibility requirements, "
                    "funding amounts, or URLs. "
                    "Look for application status, opening dates, closing dates, "
                    "funding amounts, and geographic eligibility."
                )

                # Parallel SDK request
                #
                # The SDK may impose a search-query limit, so send the
                # strongest 10 queries in this single request.
                #
                # The complete 50-query library remains available for
                # targeted/batched searches.

                response = self.client.search(
                    search_queries=search_queries[:50],
                    mode="advanced",
                    advanced_settings={
                        "max_results": 30
                    },
                    objective=objective,
                    max_chars_total=40000,
                )

                if response and hasattr(response, "results"):

                    for result in response.results:

                        title = getattr(result, "title", "") or ""
                        url = getattr(result, "url", "") or ""

                        # Parallel may provide excerpts as a list.
                        excerpts = getattr(result, "excerpts", None)

                        if excerpts:
                            if isinstance(excerpts, list):
                                excerpt_text = " ".join(
                                    str(x) for x in excerpts
                                )
                            else:
                                excerpt_text = str(excerpts)

                        else:
                            # Backwards-compatible fallback
                            excerpt_text = (
                                getattr(result, "excerpt", "") or ""
                            )

                        formatted = {
                            "title": title.strip(),
                            "url": url.strip(),
                            "excerpt": excerpt_text[:1000],
                            "publish_date": getattr(
                                result,
                                "publish_date",
                                None,
                            ),
                            "source": "Parallel Search API",
                            "live_search": True,
                        }

                        if formatted["title"] or formatted["url"]:
                            all_results.append(formatted)

                logger.info(
                    "[ParallelAPI] SDK search returned %d results",
                    len(all_results),
                )

            except Exception as e:

                logger.error(
                    "[ParallelAPI] SDK search failed: %s",
                    e,
                )

                logger.info(
                    "[ParallelAPI] Falling back to requests-based search"
                )

                all_results = self._search_with_requests(search_queries)

        # ========================================================
        # REQUESTS FALLBACK
        # ========================================================

        else:

            logger.info(
                "[ParallelAPI] Using requests-based search"
            )

            all_results = self._search_with_requests(
                search_queries
            )

        # ========================================================
        # DEDUPLICATE
        # ========================================================

        unique_results = self._deduplicate(all_results)

        logger.info(
            "[ParallelAPI] Finished: %d total -> %d unique",
            len(all_results),
            len(unique_results),
        )

        return unique_results

    # ============================================================
    # DIRECT REQUESTS FALLBACK
    # ============================================================

    def _search_with_requests(
        self,
        search_queries: list[str],
    ) -> list[dict[str, Any]]:
        """
        Fallback search using Parallel's REST API directly.
        """

        import requests

        all_results: list[dict[str, Any]] = []

        objective = (
            "Find REAL film funding opportunities for filmmakers. "
            "Prioritize 2026 and 2027 funding cycles. "
            "Look for grants, funds, fellowships, residencies, labs, "
            "competitions, prizes, development funding, production funding, "
            "and post-production funding. "
            "Opportunities must be real and supported by source evidence. "
            "Do not fabricate deadlines, eligibility, funding amounts, "
            "or URLs."
        )

        # Keep the REST fallback bounded so one failure doesn't
        # create an excessive number of API requests.
        batches = [
            search_queries[i:i + 10]
            for i in range(0, len(search_queries), 10)
        ]

        for batch_number, batch in enumerate(
            batches,
            start=1,
        ):

            try:

                payload = {
                    "objective": objective,
                    "search_queries": batch,
                    "mode": "advanced",
                    "advanced_settings": {
                        "max_results": 20,
                        "fetch_policy": {
                            "max_age_seconds": 86400,
                            "timeout_seconds": 30,
                        },
                    },
                    "max_chars_total": 40000,
                }

                response = requests.post(
                    self.ENDPOINT,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                    },
                    timeout=60,
                )

                if response.status_code == 200:

                    data = response.json()

                    results = data.get(
                        "results",
                        [],
                    )

                    for result in results:

                        title = (
                            result.get("title") or ""
                        ).strip()

                        url = (
                            result.get("url") or ""
                        ).strip()

                        excerpts = result.get(
                            "excerpts"
                        )

                        if excerpts:

                            if isinstance(
                                excerpts,
                                list,
                            ):
                                excerpt_text = " ".join(
                                    str(x)
                                    for x in excerpts
                                )
                            else:
                                excerpt_text = str(
                                    excerpts
                                )

                        else:

                            excerpt_text = (
                                result.get(
                                    "excerpt"
                                )
                                or ""
                            )

                        if title or url:

                            all_results.append(
                                {
                                    "title": title,
                                    "url": url,
                                    "excerpt": excerpt_text[:1000],
                                    "publish_date": result.get(
                                        "publish_date"
                                    ),
                                    "source": "Parallel Search API",
                                    "live_search": True,
                                }
                            )

                    logger.info(
                        "[ParallelAPI] Batch %d/%d: %d results",
                        batch_number,
                        len(batches),
                        len(results),
                    )

                else:

                    logger.error(
                        "[ParallelAPI] Batch %d failed: HTTP %s",
                        batch_number,
                        response.status_code,
                    )

            except requests.Timeout:

                logger.error(
                    "[ParallelAPI] Batch %d timed out",
                    batch_number,
                )

            except Exception as e:

                logger.error(
                    "[ParallelAPI] Batch %d error: %s",
                    batch_number,
                    e,
                )

        return all_results

    # ============================================================
    # DEDUPLICATION
    # ============================================================

    def _deduplicate(
        self,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate results based on URL and title.
        """

        unique_results: list[dict[str, Any]] = []

        seen_urls = set()
        seen_titles = set()

        for result in results:

            url = (
                result.get("url") or ""
            ).strip()

            title = (
                result.get("title") or ""
            ).strip()

            normalized_url = (
                url.rstrip("/").lower()
            )

            normalized_title = (
                " ".join(
                    title.lower().split()
                )
            )

            # ----------------------------------------------------
            # URL deduplication
            # ----------------------------------------------------

            if normalized_url:

                if normalized_url in seen_urls:
                    continue

                seen_urls.add(
                    normalized_url
                )

            # ----------------------------------------------------
            # Title deduplication
            # ----------------------------------------------------

            elif normalized_title:

                if normalized_title in seen_titles:
                    continue

                seen_titles.add(
                    normalized_title
                )

            unique_results.append(
                result
            )

        # --------------------------------------------------------
        # Stable IDs
        # --------------------------------------------------------

        for index, result in enumerate(
            unique_results,
            start=1,
        ):
            result["result_id"] = (
                f"grant_{index}"
            )

        return unique_results


# ================================================================
# PUBLIC FUNCTION
# ================================================================

def search_parallel(
    query: str = None,
) -> list[dict[str, Any]]:
    """
    Public function to search for film grants.

    Args:
        query:
            Optional specific search query.

    Returns:
        List of real film funding opportunities.
    """

    searcher = ParallelGrantSearch()

    return searcher.search(
        query
    )


# ================================================================
# LOCAL TEST
# ================================================================

if __name__ == "__main__":

    print(
        "Testing FILMFUND Parallel Search API..."
    )

    print(
        "-" * 60
    )

    print(
        f"\nConfigured search queries: "
        f"{len(ParallelGrantSearch.SEARCH_QUERIES)}"
    )

    # ------------------------------------------------------------
    # Test 1
    # ------------------------------------------------------------

    print(
        "\n1. Testing default film funding search..."
    )

    results = search_parallel()

    print(
        f"Found {len(results)} unique grants"
    )

    if results:

        print(
            f"First result: "
            f"{results[0].get('title', 'N/A')}"
        )

        print(
            f"URL: "
            f"{results[0].get('url', 'N/A')}"
        )

    # ------------------------------------------------------------
    # Test 2
    # ------------------------------------------------------------

    print(
        "\n2. Testing USA film grant search..."
    )

    usa_results = search_parallel(
        "USA film grant"
    )

    print(
        f"Found {len(usa_results)} USA-related results"
    )

    if usa_results:

        print(
            f"First result: "
            f"{usa_results[0].get('title', 'N/A')}"
        )

        print(
            f"URL: "
            f"{usa_results[0].get('url', 'N/A')}"
        )

    print(
        "\n" + "-" * 60
    )

    print(
        "Test complete!"
    )