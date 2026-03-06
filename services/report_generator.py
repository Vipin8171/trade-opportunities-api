"""
Report Generator Service.
Handles saving generated markdown reports and managing report history.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional

from utils.logger import logger


class ReportGenerator:
    """Manages generated reports — saves to disk & keeps in-memory history."""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

        # In-memory report history: { sector: [ {timestamp, filename, report} ] }
        self._history: Dict[str, List[Dict]] = {}

        logger.info(f"ReportGenerator initialized (reports dir: {self.reports_dir})")

    def save_report(self, sector: str, report_content: str) -> str:
        """
        Save a markdown report to disk and store in memory.
        Returns the filename of the saved report.
        """
        timestamp = datetime.now()
        filename = (
            f"{sector.lower().replace(' ', '_')}_report_"
            f"{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        )
        filepath = os.path.join(self.reports_dir, filename)

        # Write to disk
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"Report saved: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save report to disk: {e}")

        # Store in memory
        record = {
            "timestamp": timestamp.isoformat(),
            "filename": filename,
            "sector": sector,
            "report": report_content,
            "char_count": len(report_content),
        }

        if sector.lower() not in self._history:
            self._history[sector.lower()] = []
        self._history[sector.lower()].append(record)

        return filename

    def get_history(self, sector: Optional[str] = None) -> List[Dict]:
        """Get report generation history. Optionally filter by sector."""
        if sector:
            return self._history.get(sector.lower(), [])

        # Return all history (without full report text for brevity)
        all_history = []
        for sector_key, records in self._history.items():
            for r in records:
                all_history.append({
                    "sector": r["sector"],
                    "timestamp": r["timestamp"],
                    "filename": r["filename"],
                    "char_count": r["char_count"],
                })
        return sorted(all_history, key=lambda x: x["timestamp"], reverse=True)

    def get_report_count(self) -> int:
        """Get total number of reports generated."""
        return sum(len(v) for v in self._history.values())


# Global instance
report_generator = ReportGenerator()
