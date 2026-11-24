"""Base spider implementation for Indonesian tourism portals.

Provides polite rate limiting, standardized user agent, robust error handling,
HTML cleaning utilities, and a consistent document schema.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseSpider:
    """Abstract base crawler spider for Indonesian tourism web scraping."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "WisataNusantaraBot/1.0 (Kelompok 10 Educational IR Project)"
    )

    def __init__(
        self,
        source_name: str,
        base_url: str,
        rate_limit_delay: float = 0.5,
        timeout: int = 10,
    ) -> None:
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept-Language": "id,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

    def fetch(self, url: str) -> Optional[str]:
        """Fetch raw HTML with polite rate limiting and retry handling."""
        time.sleep(self.rate_limit_delay)
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.text
            logger.warning(
                "Received HTTP %d when fetching %s", response.status_code, url
            )
            return None
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Strip excess whitespace and unwanted characters."""
        if not raw_text:
            return ""
        text = re.sub(r"\s+", " ", raw_text)
        text = re.sub(r"\s+([.,!?;:])", r"\1", text)
        return text.strip()

    @staticmethod
    def strip_html(html_content: str) -> str:
        """Strip HTML tags while preserving text boundaries."""
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        return BaseSpider.clean_text(soup.get_text(separator=" "))

    def build_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        url: str,
        location: str,
        category: str,
    ) -> Dict[str, Any]:
        """Format a document into the standardized corpus schema."""
        return {
            "doc_id": doc_id,
            "title": self.clean_text(title),
            "content": self.clean_text(content),
            "url": url.strip(),
            "source": self.source_name,
            "location": self.clean_text(location),
            "category": self.clean_text(category),
        }

    def crawl(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Execute crawling and return a list of standard documents.

        Subclasses implement domain-specific crawling and article parsing.
        """
        raise NotImplementedError("Subclasses must implement crawl().")
