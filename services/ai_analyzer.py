"""
AI Analyzer Service.
Uses Google Gemini API to analyze collected market data and generate insights.
Includes retry logic and fallback model support.
"""
import time
import google.generativeai as genai

from config import GEMINI_API_KEY
from utils.logger import logger

# Ordered list of models to try (fallback chain)
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
]


class AIAnalyzer:
    """Analyzes market data using Google Gemini API."""

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.models = {name: genai.GenerativeModel(name) for name in GEMINI_MODELS}
        self.primary_model = GEMINI_MODELS[0]
        logger.info(f"Gemini AI initialized with models: {GEMINI_MODELS}")

    def analyze_sector(self, sector: str, collected_data_text: str) -> str:
        """
        Send collected data to Gemini and get a structured markdown analysis.
        Tries multiple models with retry logic.
        Returns the markdown report string.
        """
        logger.info(f"Sending data to Gemini for sector: '{sector}'")
        prompt = self._build_prompt(sector, collected_data_text)

        # Try each model in fallback order
        last_error = None
        for model_name in GEMINI_MODELS:
            model = self.models[model_name]
            for attempt in range(2):  # 2 attempts per model
                try:
                    logger.info(f"Trying model: {model_name} (attempt {attempt+1})")
                    response = model.generate_content(prompt)

                    if response and response.text:
                        logger.info(
                            f"✅ Analysis received from '{model_name}' for '{sector}' "
                            f"({len(response.text)} characters)"
                        )
                        return response.text
                    else:
                        logger.warning(f"Empty response from {model_name}")

                except Exception as e:
                    last_error = e
                    error_msg = str(e)
                    logger.warning(f"Model {model_name} attempt {attempt+1} failed: {error_msg}")

                    # If rate limited, wait before retry
                    if "429" in error_msg or "quota" in error_msg.lower():
                        wait_time = 5 * (attempt + 1)
                        logger.info(f"Rate limited — waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        break  # Non-rate-limit error, try next model

        # All models failed
        logger.error(f"All Gemini models failed for '{sector}': {last_error}")
        raise RuntimeError(f"AI analysis failed: {str(last_error)}")

    def _build_prompt(self, sector: str, data_text: str) -> str:
        """Build a detailed prompt for Gemini."""

        return f"""You are an expert Indian market analyst. Based on the following collected 
market data, generate a comprehensive **Trade Opportunities Report** for the 
**{sector.title()}** sector in India.

{data_text}

Generate the report in **well-structured Markdown format** with the following sections:

# Trade Opportunities Report: {sector.title()} Sector — India

## 1. Executive Summary
- Brief overview of the sector's current state in India (3-4 sentences)

## 2. Market Overview
- Market size and growth rate
- Key statistics and figures
- India's global position in this sector

## 3. Current Trade Opportunities
### 3.1 Export Opportunities
- Key products/services with export potential
- Target markets and demand drivers

### 3.2 Import Substitution
- Areas where India can reduce imports
- Government initiatives supporting domestic production

## 4. Government Policies & Incentives
- Relevant schemes (PLI, Make in India, etc.)
- Tax benefits and subsidies
- Regulatory changes

## 5. Key Players & Competitive Landscape
- Top companies in this sector
- Market share distribution
- Recent mergers/acquisitions

## 6. Emerging Trends
- Technology adoption
- Sustainability initiatives
- Consumer behavior shifts

## 7. Risks & Challenges
- Regulatory risks
- Global competition
- Supply chain vulnerabilities

## 8. Recommendations
- Short-term opportunities (0-6 months)
- Medium-term strategies (6-18 months)
- Long-term outlook

## 9. Data Sources
- List the sources used for this analysis

---
*Report generated on: [current date]*
*Disclaimer: This report is for informational purposes only.*

IMPORTANT:
- Use REAL data and figures from the provided information
- Keep the analysis specific to India
- Include actual company names, numbers, and statistics where available
- Make it professional and actionable
- Use proper markdown formatting with headers, bullet points, and tables where helpful
"""


# Global instance
ai_analyzer = AIAnalyzer()
