"""
FILMFUND - PARALLEL LIVE SEARCH API

Parallel Search API performs the live search.

User query
    ↓
Parallel Search API
    ↓
Live web search
    ↓
Parallel returns results
    ↓
FilmFund passes those results through

No hardcoded grants.
No hardcoded funding.
No hardcoded deadlines.
No hardcoded eligibility.
No manual funding processing.
No manual deadline processing.
No scraping.
"""

import logging
import os
from typing import Any

from parallel import Parallel


logger = logging.getLogger(__name__)


class ParallelGrantSearch:
    """Direct client for Parallel Live Search."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("PARALLEL_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "PARALLEL_API_KEY is not configured in the environment."
            )

        self.client = Parallel(
            api_key=self.api_key
        )

    def search(self, query: str) -> list[dict[str, Any]]:
        """
        Send the user's query directly to Parallel Search.

        Parallel performs the live search and returns the
        actual web results.
        """

        query = (query or "").strip()

        if not query:
            return []

        try:
            logger.info(
                "[ParallelAPI] Live search: %s",
                query,
            )

            response = self.client.search(
                search_queries=[query],
                mode="advanced",
                advanced_settings={
                    "max_results": 10,
                },
                objective=query,
                max_chars_total=5000,
            )

            results = getattr(
                response,
                "results",
                None,
            )

            if results is None and isinstance(
                response,
                dict,
            ):
                results = response.get(
                    "results",
                    [],
                )

            if not results:
                return []

            formatted: list[dict[str, Any]] = []

            for result in results:

                if isinstance(result, dict):
                    title = result.get("title")
                    url = result.get("url")
                    publish_date = result.get(
                        "publish_date"
                    )
                    excerpts = result.get(
                        "excerpts"
                    )

                else:
                    title = getattr(
                        result,
                        "title",
                        None,
                    )

                    url = getattr(
                        result,
                        "url",
                        None,
                    )

                    publish_date = getattr(
                        result,
                        "publish_date",
                        None,
                    )

                    excerpts = getattr(
                        result,
                        "excerpts",
                        None,
                    )

                title = (
                    str(title).strip()
                    if title is not None
                    else ""
                )

                url = (
                    str(url).strip()
                    if url is not None
                    else ""
                )

                if publish_date is not None:
                    publish_date = str(
                        publish_date
                    ).strip()

                if not isinstance(
                    excerpts,
                    list,
                ):
                    excerpts = []

                evidence: list[str] = []

                for excerpt in excerpts:
                    if excerpt is None:
                        continue

                    text = str(
                        excerpt
                    ).strip()

                    if text:
                        evidence.append(text)

                if not title and not url and not evidence:
                    continue

                formatted.append(
                    {
                        "title": title,
                        "url": url,
                        "publish_date": publish_date,
                        "excerpts": evidence,
                        "excerpt": (
                            evidence[0]
                            if evidence
                            else ""
                        ),
                        "source": (
                            "Parallel Search API"
                        ),
                        "live_search": True,
                    }
                )

            logger.info(
                "[ParallelAPI] Parallel returned %s live results",
                len(formatted),
            )

            return formatted

        except Exception as exc:
            logger.exception(
                "[ParallelAPI] Live search failed: %s",
                exc,
            )
            return []


def search_parallel(
    query: str,
) -> list[dict[str, Any]]:
    """
    Search through Parallel Live Search.
    """

    return ParallelGrantSearch().search(query)