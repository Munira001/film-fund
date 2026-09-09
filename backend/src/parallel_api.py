"""
FILMFUND - Parallel Search API Integration

Live film-funding discovery using the Parallel Search API.

The Parallel Search API is responsible for:
- Live web search
- Finding real film funding opportunities
- Returning source URLs and evidence
- Finding funding amounts, deadlines, eligibility, status, etc.

FilmFund never invents missing information.
"""

from parallel import Parallel
import logging
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ParallelGrantSearch:
    """
    Live film-funding search powered by Parallel Search.
    """

    ENDPOINT = "https://api.parallel.ai/v1/search"

    # Parallel's Search API supports prioritized search queries.
    # These are intentionally broad enough to cover global film funding.
    SEARCH_QUERIES = [
        (
            "international film grants worldwide drama documentary "
            "indie drama documentary comedy thriller"
        ),
        (
            "USA film grants funding USA all genres indie drama"
        ),
        (
            "European film grants Europe Asia funding drama "
            "documentary comedy short film"
        ),
        (
            "African film grants Africa filmmaker documentary drama"
        ),
        (
            "emerging filmmaker professional grants worldwide "
            "all genres low budget"
        ),
    ]

    def __init__(self):
        self.api_key = os.getenv("PARALLEL_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "PARALLEL_API_KEY is not configured in the environment."
            )

        logger.info(
            "[ParallelAPI] Initializing live Parallel Search client"
        )

        try:
            self.client = Parallel(api_key=self.api_key)

            logger.info(
                "[ParallelAPI] Parallel SDK client initialized successfully"
            )

        except Exception as exc:
            logger.exception(
                "[ParallelAPI] Failed to initialize Parallel SDK: %s",
                exc,
            )
            self.client = None

    # ------------------------------------------------------------------
    # PUBLIC SEARCH
    # ------------------------------------------------------------------

    def search(self, query: str | None = None) -> list[dict[str, Any]]:
        """
        Search Parallel for real film-funding opportunities.

        If the user supplies a query, it is placed first so that it has
        priority while the five global FilmFund queries remain available.
        """

        if query and query.strip():
            search_queries = [
                query.strip(),
                *self.SEARCH_QUERIES,
            ]
        else:
            search_queries = self.SEARCH_QUERIES.copy()

        # Parallel's demonstrated interface uses 1-5 prioritized queries.
        # Keep only the first five.
        search_queries = search_queries[:5]

        logger.info(
            "[ParallelAPI] Searching with %d prioritized queries",
            len(search_queries),
        )

        if not self.client:
            logger.error(
                "[ParallelAPI] Parallel client is unavailable"
            )
            return []

        try:
            response = self.client.search(
                search_queries=search_queries,
                mode="advanced",
                advanced_settings={
                    "max_results": 10,
                },
                objective=(
                    "Find REAL, currently published film funding "
                    "opportunities for filmmakers worldwide. "

                    "Prioritize active or upcoming 2026 and 2027 "
                    "funding and application cycles. "

                    "Search for film grants, film funds, production "
                    "funding, development funding, post-production "
                    "funding, fellowships, labs, residencies, "
                    "competitions, and filmmaker awards. "

                    "For each opportunity, look for explicit factual "
                    "information in the source, including: "

                    "funding amount or award amount, "
                    "application deadline or closing date, "
                    "application opening date, "
                    "eligibility requirements, "
                    "geographic eligibility, "
                    "project or production stage, "
                    "and application status. "

                    "Prefer official funder, foundation, film institute, "
                    "government, festival, or established film "
                    "organization websites. "

                    "Return source evidence that supports the facts. "

                    "Do NOT invent, estimate, infer, or fabricate "
                    "deadlines, funding amounts, eligibility requirements, "
                    "application status, or URLs. "

                    "If a source does not contain a particular fact, "
                    "do not create that fact."
                ),
                max_chars_total=5000,
            )

            results = self._format_parallel_response(response)

            logger.info(
                "[ParallelAPI] Parallel returned %d usable results",
                len(results),
            )

            return self._deduplicate(results)

        except Exception as exc:
            logger.exception(
                "[ParallelAPI] Parallel Search failed: %s",
                exc,
            )

            return []

    # ------------------------------------------------------------------
    # RESPONSE FORMATTING
    # ------------------------------------------------------------------

    def _format_parallel_response(
        self,
        response: Any,
    ) -> list[dict[str, Any]]:
        """
        Convert the Parallel SDK response into FilmFund's internal
        evidence format.

        IMPORTANT:
        We preserve the original Parallel evidence.
        """

        formatted_results: list[dict[str, Any]] = []

        if not response:
            return formatted_results

        raw_results = getattr(response, "results", None)

        if not raw_results:
            logger.warning(
                "[ParallelAPI] Parallel response contained no results"
            )
            return formatted_results

        for result in raw_results:
            title = self._get_value(result, "title")
            url = self._get_value(result, "url")

            excerpt_text = self._extract_excerpt(result)

            if not title and not url:
                continue

            facts = self._extract_facts(excerpt_text)

            formatted_results.append(
                {
                    "title": title.strip(),
                    "url": url.strip(),

                    # Original Parallel evidence.
                    "excerpt": excerpt_text[:4000],
                    "parallel_evidence": excerpt_text[:4000],

                    # Structured facts extracted ONLY from evidence.
                    "funding": facts["funding"],
                    "deadline": facts["deadline"],
                    "eligibility": facts["eligibility"],
                    "funding_type": facts["funding_type"],
                    "status": facts["status"],
                    "cycle_year": facts["cycle_year"],
                    "geographic_eligibility": facts["geographic_eligibility"],

                    "publish_date": self._get_value(
                        result,
                        "publish_date",
                    ),

                    "source": "Parallel Search API",
                    "live_search": True,
                }
            )

        return formatted_results

    # ------------------------------------------------------------------
    # PARALLEL VALUE HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _get_value(
        result: Any,
        field: str,
    ) -> str:
        """
        Safely retrieve a field from a Parallel SDK result.
        """

        try:
            value = getattr(result, field, None)

            if value is None:
                return ""

            return str(value)

        except Exception:
            return ""

    @staticmethod
    def _extract_excerpt(
        result: Any,
    ) -> str:
        """
        Extract Parallel's LLM-friendly excerpts.

        Parallel can return either:
        - excerpts
        - excerpt
        """

        excerpts = getattr(result, "excerpts", None)

        if excerpts:
            if isinstance(excerpts, list):
                return " ".join(
                    str(item)
                    for item in excerpts
                    if item
                ).strip()

            return str(excerpts).strip()

        excerpt = getattr(result, "excerpt", None)

        if excerpt:
            return str(excerpt).strip()

        return ""

    # ------------------------------------------------------------------
    # FACT EXTRACTION
    # ------------------------------------------------------------------

    def _extract_facts(
        self,
        evidence: str,
    ) -> dict[str, str]:
        """
        Extract funding, deadline and eligibility from Parallel's
        evidence.

        This function is deliberately conservative.

        It does NOT invent missing information.
        """

        if not evidence:
            return {
                "funding": "Not stated",
                "deadline": "Not stated",
                "eligibility": "Not stated",
            }

        text = self._clean_text(evidence)

        return {
            "funding": self._extract_funding(text),
            "deadline": self._extract_deadline(text),
            "eligibility": self._extract_eligibility(text),
            "funding_type": self._extract_funding_type(text),
            "status": self._extract_status(text),
            "cycle_year": self._extract_cycle_year(text),
            "geographic_eligibility": self._extract_geographic_eligibility(text),
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean common formatting returned by search snippets.
        """

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        text = text.replace(
            "\\n",
            " ",
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ------------------------------------------------------------------
    # FUNDING
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_funding(
        text: str,
    ) -> str:
        """
        Extract explicit funding/award amounts.

        Examples supported include:
        - $35,000
        - Up to €7,500
        - $3,500 USD cash award plus $20,000+ services
        - grants of $500-$1,000
        - €1.5 million
        """

        funding_patterns = [
            # "Up to $35,000"
            r"(?i)\bup to\s+"
            r"(?:[$€£]\s?[\d,.]+(?:\s?(?:million|thousand))?"
            r"(?:\s?(?:USD|EUR|GBP))?"
            r"(?:\s*[-–]\s*[$€£]?\s?[\d,.]+)?"
            r")",

            # "$35,000 grant"
            r"(?i)(?:[$€£]\s?[\d,.]+"
            r"(?:\s?(?:million|thousand))?"
            r"(?:\s?(?:USD|EUR|GBP))?"
            r"(?:\s*[-–]\s*[$€£]?\s?[\d,.]+)?"
            r")"
            r"\s*(?:cash\s+)?(?:grant|award|fellowship|funding|prize)",

            # "grants of $500-$1,000"
            r"(?i)\bgrants?\s+of\s+"
            r"[$€£]?\s?[\d,.]+"
            r"(?:\s*[-–]\s*[$€£]?\s?[\d,.]+)?"
            r"(?:\s?(?:USD|EUR|GBP))?",

            # "$3,500 USD cash award plus $20,000+ in services"
            r"(?i)[$€£]\s?[\d,.]+"
            r"(?:\s?(?:USD|EUR|GBP))?"
            r"(?:\s?\+)?"
            r"\s+(?:in\s+)?"
            r"(?:cash|services|funding|support|awards?)",

            # "€1.5 million"
            r"(?i)(?:[$€£]\s?[\d,.]+"
            r"(?:\s?(?:million|billion|thousand)))",
        ]

        matches: list[str] = []

        for pattern in funding_patterns:
            for match in re.findall(pattern, text):
                if isinstance(match, tuple):
                    match = " ".join(
                        item for item in match if item
                    )

                value = str(match).strip()

                if value and value not in matches:
                    matches.append(value)

        if not matches:
            return "Not stated"

        # Return the most informative explicit funding phrase(s).
        return "; ".join(matches[:3])

    # ------------------------------------------------------------------
    # DEADLINE
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_deadline(
        text: str,
    ) -> str:
        """
        Extract explicit application closing/deadline information.

        We intentionally require deadline-related language so ordinary
        dates in articles aren't incorrectly presented as deadlines.
        """

        deadline_patterns = [
            # Deadline: June 30, 2026
            r"(?i)\b(?:application\s+)?deadline"
            r"\s*[:\-]?\s*"
            r"([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?"
            r"|\d{1,2}\s+[A-Z][a-z]+(?:\s+\d{4})?"
            r"|\d{4}-\d{2}-\d{2})",

            # submission deadline / closing date
            r"(?i)\b(?:submission|application|applications)"
            r"\s+(?:deadline|closing\s+date|close)"
            r"\s*[:\-]?\s*"
            r"([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?"
            r"|\d{1,2}\s+[A-Z][a-z]+(?:\s+\d{4})?"
            r"|\d{4}-\d{2}-\d{2})",

            # "open until 6 August"
            r"(?i)\bopen\s+until\s+"
            r"([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?"
            r"|\d{1,2}\s+[A-Z][a-z]+(?:\s+\d{4})?)",

            # "applications close on September 10"
            r"(?i)\bapplications?\s+close"
            r"(?:\s+on)?\s+"
            r"([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?"
            r"|\d{1,2}\s+[A-Z][a-z]+(?:\s+\d{4})?)",

            # "closing date: ..."
            r"(?i)\bclosing\s+date"
            r"\s*[:\-]?\s*"
            r"([A-Z][a-z]+\s+\d{1,2}(?:,\s*\d{4})?"
            r"|\d{1,2}\s+[A-Z][a-z]+(?:\s+\d{4})?)",
        ]

        matches: list[str] = []

        for pattern in deadline_patterns:
            for match in re.findall(pattern, text):
                value = str(match).strip()

                if value and value not in matches:
                    matches.append(value)

        if not matches:
            return "Not stated"

        return "; ".join(matches[:4])

    # ------------------------------------------------------------------
    # ELIGIBILITY
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_eligibility(
        text: str,
    ) -> str:
        """
        Extract explicit eligibility statements from Parallel evidence.
        """

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        matches: list[str] = []

        eligibility_keywords = (
            "open to",
            "eligible",
            "eligibility",
            "worldwide",
            "international filmmakers",
            "filmmakers from",
            "based in",
            "based on",
            "no geographic restrictions",
            "geographic restrictions",
            "must have",
            "applicants must",
            "applicant must",
            "projects under",
            "budgets under",
        )

        for sentence in sentences:
            clean_sentence = sentence.strip()

            if not clean_sentence:
                continue

            lowered = clean_sentence.lower()

            if any(
                keyword in lowered
                for keyword in eligibility_keywords
            ):
                if clean_sentence not in matches:
                    matches.append(clean_sentence)

        if not matches:
            return "Not stated"

        return " ".join(matches[:3])

        # ------------------------------------------------------------------
    # FUNDING TYPE
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_funding_type(
        text: str,
    ) -> str:
        """
        Extract an explicit funding/opportunity type from the
        Parallel evidence.

        This does not infer a type when the evidence does not
        explicitly mention one.
        """

        if not text:
            return "Not stated"

        lowered = text.lower()

        funding_types = [
            (
                "post-production funding",
                "Post-production funding",
            ),
            (
                "post-production grant",
                "Post-production grant",
            ),
            (
                "production funding",
                "Production funding",
            ),
            (
                "production grant",
                "Production grant",
            ),
            (
                "development funding",
                "Development funding",
            ),
            (
                "development grant",
                "Development grant",
            ),
            (
                "film fund",
                "Film fund",
            ),
            (
                "film grant",
                "Film grant",
            ),
            (
                "fellowship",
                "Fellowship",
            ),
            (
                "residency",
                "Residency",
            ),
            (
                "competition",
                "Competition",
            ),
            (
                "award",
                "Award",
            ),
            (
                "prize",
                "Prize",
            ),
            (
                "grant",
                "Grant",
            ),
        ]

        for keyword, label in funding_types:
            if keyword in lowered:
                return label

        return "Not stated"

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_status(
        text: str,
    ) -> str:
        """
        Extract explicit application status from Parallel evidence.

        Status is never inferred from a deadline.
        """

        if not text:
            return "Not stated"

        status_patterns = [
            (
                r"\bapplications?\s+(?:are\s+)?open\b",
                "Open",
            ),
            (
                r"\bnow\s+open\b",
                "Open",
            ),
            (
                r"\bcurrently\s+open\b",
                "Open",
            ),
            (
                r"\bapplications?\s+(?:are\s+)?closed\b",
                "Closed",
            ),
            (
                r"\bnow\s+closed\b",
                "Closed",
            ),
            (
                r"\bcurrently\s+closed\b",
                "Closed",
            ),
            (
                r"\bcoming\s+soon\b",
                "Coming soon",
            ),
        ]

        for pattern, label in status_patterns:
            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                return label

        return "Not stated"

    # ------------------------------------------------------------------
    # CYCLE YEAR
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_cycle_year(
        text: str,
    ) -> str:
        """
        Extract explicit 2026/2027 references from the evidence.

        No year is invented if it does not appear in the source
        evidence.
        """

        if not text:
            return "Not stated"

        years = re.findall(
            r"\b(?:2026|2027)\b",
            text,
        )

        unique_years: list[str] = []

        for year in years:
            if year not in unique_years:
                unique_years.append(
                    year
                )

        if not unique_years:
            return "Not stated"

        return ", ".join(
            unique_years
        )

    # ------------------------------------------------------------------
    # GEOGRAPHIC ELIGIBILITY
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_geographic_eligibility(
        text: str,
    ) -> str:
        """
        Extract explicit geographic eligibility statements.

        IMPORTANT:
        The location where a search result was found is NOT treated
        as geographic eligibility.
        """

        if not text:
            return "Not stated"

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        matches: list[str] = []

        geographic_keywords = (
            "worldwide",
            "international filmmakers",
            "international applicants",
            "filmmakers from",
            "applicants from",
            "open to filmmakers from",
            "based in",
            "filmmakers based in",
            "residents of",
            "citizens of",
            "geographic eligibility",
            "geographic restrictions",
            "geographical eligibility",
            "countries",
            "country",
            "africa",
            "african filmmakers",
            "europe",
            "european filmmakers",
            "asia",
            "asian filmmakers",
            "united states",
            "usa",
            "american filmmakers",
        )

        for sentence in sentences:
            clean_sentence = sentence.strip()

            if not clean_sentence:
                continue

            lowered = clean_sentence.lower()

            if any(
                keyword in lowered
                for keyword in geographic_keywords
            ):
                if clean_sentence not in matches:
                    matches.append(
                        clean_sentence
                    )

        if not matches:
            return "Not stated"

        return " ".join(
            matches[:3]
        )



    # ------------------------------------------------------------------
    # DEDUPLICATION
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate(
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate Parallel results by URL/title.
        """

        unique_results: list[dict[str, Any]] = []

        seen_urls: set[str] = set()
        seen_titles: set[str] = set()

        for result in results:
            url = (
                result.get("url") or ""
            ).strip()

            title = (
                result.get("title") or ""
            ).strip()

            normalized_url = url.rstrip("/").lower()

            normalized_title = (
                " ".join(
                    title.lower().split()
                )
            )

            if normalized_url:
                if normalized_url in seen_urls:
                    continue

                seen_urls.add(normalized_url)

            elif normalized_title:
                if normalized_title in seen_titles:
                    continue

                seen_titles.add(normalized_title)

            unique_results.append(result)

        for index, result in enumerate(
            unique_results,
            start=1,
        ):
            result["result_id"] = f"grant_{index}"

        return unique_results


# ----------------------------------------------------------------------
# PUBLIC FUNCTION
# ----------------------------------------------------------------------

def search_parallel(
    query: str | None = None,
) -> list[dict[str, Any]]:
    """
    Public FilmFund entry point.
    """

    searcher = ParallelGrantSearch()

    return searcher.search(query)


# ----------------------------------------------------------------------
# LOCAL TEST
# ----------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("FILMFUND - PARALLEL SEARCH TEST")
    print("=" * 70)

    try:
        results = search_parallel()

        print(
            f"\nFound {len(results)} unique live results.\n"
        )

        for index, result in enumerate(
            results[:10],
            start=1,
        ):
            print("-" * 70)
            print(f"RESULT {index}")
            print(f"Title: {result.get('title')}")
            print(f"URL: {result.get('url')}")
            print(f"Funding: {result.get('funding')}")
            print(f"Deadline: {result.get('deadline')}")
            print(
                f"Eligibility: "
                f"{result.get('eligibility')}"
            )
            print(
                f"Evidence: "
                f"{result.get('parallel_evidence', '')[:500]}"
            )

    except Exception as exc:
        print("\nParallel Search test failed:")
        print(exc)