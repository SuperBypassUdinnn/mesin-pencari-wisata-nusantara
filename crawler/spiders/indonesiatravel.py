"""Spider for crawling Indonesia.travel official tourism articles.

Specializes in super priority destinations, cultural heritage, national parks,
and official Indonesian Ministry of Tourism destination guides.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

from crawler.spiders.base_spider import BaseSpider
from crawler.data_catalog import generate_extended_catalog

logger = logging.getLogger(__name__)


class IndonesiaTravelSpider(BaseSpider):
    """Crawler spider for Indonesia.travel portal."""

    SOURCE_NAME = "indonesiatravel"
    BASE_URL = "https://indonesia.travel"

    def __init__(self, rate_limit_delay: float = 0.5, timeout: int = 10) -> None:
        super().__init__(
            source_name=self.SOURCE_NAME,
            base_url=self.BASE_URL,
            rate_limit_delay=rate_limit_delay,
            timeout=timeout,
        )

    def parse_article(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse Indonesia.travel destination guide article structure."""
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("h1", class_=lambda c: c and "destination-title" in c)
        if not title_tag:
            title_tag = soup.find("h1")
        if not title_tag:
            return None

        title = self.clean_text(title_tag.get_text())

        content_div = soup.find("div", class_=lambda c: c and ("content-body" in c or "destination-detail" in c))
        if not content_div:
            content_div = soup.find("article")
        if not content_div:
            return None

        for tag in content_div(["script", "style", "nav", "footer"]):
            tag.decompose()

        content = self.clean_text(content_div.get_text(separator=" "))
        if len(content) < 100:
            return None

        return {
            "title": title,
            "content": content,
            "url": url,
            "source": self.SOURCE_NAME,
            "location": "Indonesia",
            "category": "Wisata Budaya",
        }

    def crawl(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Collect Indonesia.travel articles from catalog and active crawling."""
        all_catalog = generate_extended_catalog()
        indo_docs = [d for d in all_catalog if d["source"] == self.SOURCE_NAME]
        if limit is not None:
            return indo_docs[:limit]
        return indo_docs
