"""
Data Collection Service.
Uses DuckDuckGo search to gather current market data, news, and trade information.
Includes rate-limit handling with delays between requests.
"""
import time
from typing import List, Dict

from duckduckgo_search import DDGS

from utils.logger import logger

# Delay between DuckDuckGo requests to avoid rate limiting (seconds)
SEARCH_DELAY = 2.0


class DataCollector:
    """Collects market data and news using DuckDuckGo search."""

    def _search_text(self, query: str, max_results: int = 8) -> List[Dict]:
        """Perform a text search on DuckDuckGo."""
        try:
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))
            logger.info(f"Text search: '{query}' → {len(results)} results")
            return results
        except Exception as e:
            logger.warning(f"Text search failed for '{query}': {e}")
            return []

    def _search_news(self, query: str, max_results: int = 6) -> List[Dict]:
        """Perform a news search on DuckDuckGo."""
        try:
            ddgs = DDGS()
            results = list(ddgs.news(query, max_results=max_results))
            logger.info(f"News search: '{query}' → {len(results)} results")
            return results
        except Exception as e:
            logger.warning(f"News search failed for '{query}': {e}")
            return []

    def collect_sector_data(self, sector: str) -> Dict:
        """
        Collect comprehensive data for a given sector.
        Runs multiple targeted searches and aggregates results.
        """
        logger.info(f"Starting data collection for sector: '{sector}'")

        # Define targeted search queries for Indian market
        search_queries = {
            "market_overview": f"{sector} sector India market overview 2025 2026",
            "trade_opportunities": f"{sector} India trade opportunities export import 2026",
            "govt_policies": f"India government policies {sector} sector recent",
            "market_trends": f"{sector} industry India latest trends growth",
            "key_players": f"top companies {sector} sector India market share",
        }

        news_queries = {
            "recent_news": f"{sector} sector India latest news trade",
            "policy_news": f"India {sector} policy regulation news 2026",
        }

        collected_data = {
            "sector": sector,
            "text_results": {},
            "news_results": {},
            "total_sources": 0,
        }

        # Run text searches (with delays to avoid rate limiting)
        for key, query in search_queries.items():
            results = self._search_text(query, max_results=5)
            collected_data["text_results"][key] = results
            collected_data["total_sources"] += len(results)
            time.sleep(SEARCH_DELAY)  # Respect DuckDuckGo rate limits

        # Run news searches
        for key, query in news_queries.items():
            results = self._search_news(query, max_results=4)
            collected_data["news_results"][key] = results
            collected_data["total_sources"] += len(results)
            time.sleep(SEARCH_DELAY)

        logger.info(
            f"Data collection complete for '{sector}': "
            f"{collected_data['total_sources']} total sources gathered"
        )
        return collected_data

    def format_for_analysis(self, collected_data: Dict) -> str:
        """
        Format collected data into a structured string for the AI analyzer.
        """
        sector = collected_data["sector"]
        lines = [f"=== COLLECTED MARKET DATA FOR: {sector.upper()} SECTOR (INDIA) ===\n"]

        # Format text search results
        for category, results in collected_data["text_results"].items():
            header = category.replace("_", " ").title()
            lines.append(f"\n--- {header} ---")
            if not results:
                lines.append("  No data found for this category.")
                continue
            for i, r in enumerate(results, 1):
                title = r.get("title", "N/A")
                body = r.get("body", r.get("snippet", "N/A"))
                href = r.get("href", r.get("link", ""))
                lines.append(f"  [{i}] {title}")
                lines.append(f"      {body[:300]}")
                if href:
                    lines.append(f"      Source: {href}")

        # Format news results
        for category, results in collected_data["news_results"].items():
            header = category.replace("_", " ").title()
            lines.append(f"\n--- {header} (NEWS) ---")
            if not results:
                lines.append("  No news found for this category.")
                continue
            for i, r in enumerate(results, 1):
                title = r.get("title", "N/A")
                body = r.get("body", r.get("snippet", "N/A"))
                date = r.get("date", "N/A")
                source = r.get("source", "N/A")
                lines.append(f"  [{i}] {title}")
                lines.append(f"      {body[:250]}")
                lines.append(f"      Date: {date} | Source: {source}")

        return "\n".join(lines)


# Global instance
data_collector = DataCollector()
