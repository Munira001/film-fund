"""
FILMFUND - Parallel Search API Integration

Live film funding discovery using the Parallel Search API.

Goals:
- Real live web search
- USA, Africa, Worldwide, International coverage
- 2026 and 2027 opportunities
- Preserve source evidence and metadata
- Never create/mock funding opportunities
- Keep enough information for downstream verification
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Any

import requests


logger = logging.getLogger(__name__)


class ParallelGrantSearch:
    """Search for real film funding opportunities using Parallel."""

    ENDPOINT = "https://api.parallel.ai/v1/search"

    REGIONS = [
        "USA",
        "Africa",
        "Worldwide",
        "International",
    ]

    def __init__(self):
        self.api_key = os.getenv("PARALLEL_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "PARALLEL_API_KEY is not configured in the environment."
            )

        logger.info("[ParallelAPI] Initialized")

    def _search_region(
        self,
        query: str,
        region: str,
    ) -> list[dict[str, Any]]:
        """Run one live Parallel search for a geographic region."""

        current_date = date.today().isoformat()

        objective = (
            "Find REAL, currently published film funding opportunities "
            "matching this filmmaker request: "
            f"{query}. "

            f"The current date is {current_date}. "

            "Prioritize opportunities for the 2026 or 2027 funding cycle. "

            f"Search specifically for opportunities that may be relevant "
            f"to {region}. "

            "Look for genuine grants, film funds, production funds, "
            "development funds, post-production funds, fellowships, "
            "residencies, labs, competitions, prizes, and similar "
            "programs that provide financial support. "

            "The opportunity itself must be real and supported by "
            "source evidence. "

            "Prefer the official funder, foundation, film institute, "
            "government, or program website. "

            "Do not fabricate or infer funding amounts, deadlines, "
            "eligibility, geography, application status, or URLs. "

            "If a result is an article or directory that discusses an "
            "opportunity, preserve the evidence but do not assume that "
            "the article proves the opportunity is currently open. "

            "Look specifically for application status, opening dates, "
            "closing dates, 2026/2027 cycle information, funding amounts, "
            "funding type, and geographic eligibility when available."
        )

        search_queries = [
            f"film grants {region} 2026",
            f"film funding {region} 2027",
            f"film grants {region} 2026 2027",
            f"film fund {region} applications 2026 2027",
        ]

        payload = {
            "objective": objective,
            "search_queries": search_queries,
            "mode": "advanced",
            "advanced_settings": {
                "max_results": 20,
                "fetch_policy": {
                    "max_age_seconds": 86400,
                    "timeout_seconds": 30,
                },
                "excerpt_settings": {
                    "max_chars_per_result": 4000,
                },
            },
            "max_chars_total": 40000,
        }

        try:
            logger.info(
                "[ParallelAPI] Starting %s search",
                region,
            )

            response = requests.post(
                self.ENDPOINT,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                },
                timeout=60,
            )

            if response.status_code != 200:
                logger.error(
                    "[ParallelAPI] %s failed: HTTP %s - %s",
                    region,
                    response.status_code,
                    response.text[:500],
                )
                return []

            data = response.json()
            results = data.get("results", [])

            if not isinstance(results, list):
                logger.warning(
                    "[ParallelAPI] %s returned unexpected results format",
                    region,
                )
                return []

            formatted: list[dict[str, Any]] = []

            for result in results:
                if not isinstance(result, dict):
                    continue

                title = str(
                    result.get("title") or ""
                ).strip()

                url = str(
                    result.get("url") or ""
                ).strip()

                excerpts = result.get("excerpts") or []

                evidence: list[str] = []

                if isinstance(excerpts, list):
                    for excerpt in excerpts:
                        text = str(excerpt).strip()

                        if text:
                            evidence.append(text)

                # Some Parallel responses may provide a single excerpt.
                if not evidence and result.get("excerpt"):
                    text = str(
                        result["excerpt"]
                    ).strip()

                    if text:
                        evidence.append(text)

                # Ignore completely unusable records.
                if not title and not url and not evidence:
                    continue

                formatted.append(
                    {
                        "title": title,
                        "url": url,
                        "publish_date": result.get(
                            "publish_date"
                        ),
                        "excerpts": evidence,
                        "excerpt": (
                            evidence[0]
                            if evidence
                            else ""
                        ),
                        "region_searched": region,
                        "source": "Parallel Search API",
                        "live_search": True,
                    }
                )

            logger.info(
                "[ParallelAPI] %s returned %s usable results",
                region,
                len(formatted),
            )

            return formatted

        except requests.Timeout:
            logger.error(
                "[ParallelAPI] %s search timed out",
                region,
            )
            return []

        except requests.RequestException as exc:
            logger.error(
                "[ParallelAPI] %s request failed: %s",
                region,
                exc,
            )
            return []

        except Exception as exc:
            logger.exception(
                "[ParallelAPI] %s unexpected error: %s",
                region,
                exc,
            )
            return []

    def search(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search all target geographic regions concurrently.

        Results are combined and deduplicated.

        Important:
        `region_searched` describes where the search was performed.
        It does NOT prove geographic eligibility.
        Geographic eligibility must be determined from the evidence.
        """

        if not query or not query.strip():
            return []

        query = query.strip()

        all_results: list[dict[str, Any]] = []

        with ThreadPoolExecutor(
            max_workers=len(self.REGIONS)
        ) as executor:

            futures = {
                executor.submit(
                    self._search_region,
                    query,
                    region,
                ): region
                for region in self.REGIONS
            }

            for future in as_completed(futures):
                region = futures[future]

                try:
                    results = future.result()
                    all_results.extend(results)

                except Exception as exc:
                    logger.exception(
                        "[ParallelAPI] %s worker failed: %s",
                        region,
                        exc,
                    )

        unique_results: list[dict[str, Any]] = []

        seen_urls: set[str] = set()
        seen_titles: set[str] = set()

        for result in all_results:
            url = str(
                result.get("url") or ""
            ).strip()

            title = str(
                result.get("title") or ""
            ).strip()

            normalized_url = url.rstrip("/").lower()

            normalized_title = " ".join(
                title.lower().split()
            )

            # URL is the preferred deduplication key.
            if normalized_url:
                if normalized_url in seen_urls:
                    continue

                seen_urls.add(normalized_url)

            # If no URL exists, fall back to title.
            elif normalized_title:
                if normalized_title in seen_titles:
                    continue

                seen_titles.add(normalized_title)

            unique_results.append(result)

        # Assign stable IDs only after deduplication.
        for index, result in enumerate(
            unique_results,
            start=1,
        ):
            result["result_id"] = f"parallel_{index}"

        logger.info(
            "[ParallelAPI] Finished search: "
            "%s total results -> %s unique results",
            len(all_results),
            len(unique_results),
        )

        return unique_results


def search_parallel(
    query: str,
) -> list[dict[str, Any]]:
    """Search the live Parallel API for film funding."""

    return ParallelGrantSearch().search(query)