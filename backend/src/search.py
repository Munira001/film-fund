"""Search functions using Parallel API"""

from parallel_api import ParallelGrantSearch
from models import Filmmaker, Grant
from logs import logger


class FilmGrantSearcher:
    """Search for real film grants using Parallel API"""

    def __init__(self):
        self.parallel_api = ParallelGrantSearch()

    def search_grants(self, filmmaker: Filmmaker) -> list:
        """Search REAL film grants from Parallel API"""
        try:
            query = (
                f"film grants {filmmaker.genre} "
                f"${filmmaker.budget_min}-${filmmaker.budget_max}"
            )

            logger.info(f"Searching REAL grants: {query}")

            results = self.parallel_api.search(query)

            grants = []

            for result in results:
                grant = Grant(
                    name=result.get("title", "Unknown Grant"),
                    amount=0,
                    deadline="Unknown",
                    eligibility=result.get("excerpt", ""),
                    organization="Unknown",
                    link=result.get("url", ""),
                )
                grants.append(grant)

            logger.info(
                f"Found {len(grants)} REAL grants from Parallel API"
            )

            return grants

        except Exception as e:
            logger.error(f"Real grant search failed: {str(e)}")
            return []

    def search_producers(self, filmmaker: Filmmaker) -> list:
        """Search REAL production companies"""
        try:
            query = (
                f"production companies {filmmaker.genre} "
                f"budget ${filmmaker.budget_min}"
            )

            logger.info(f"Searching REAL producers: {query}")

            results = self.parallel_api.search(query)

            logger.info(f"Found {len(results)} REAL producers")

            return results

        except Exception as e:
            logger.error(f"Producer search failed: {str(e)}")
            return []