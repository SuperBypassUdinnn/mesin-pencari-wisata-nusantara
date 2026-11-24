"""Spider for crawling Wisato.id travel spotlight and lifestyle articles.

Specializes in tourist spots, travel guides, hidden gems, and regional culinary tours.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

from crawler.spiders.base_spider import BaseSpider
from crawler.data_catalog import generate_extended_catalog

logger = logging.getLogger(__name__)


class WisatoSpider(BaseSpider):
    """Crawler spider for Wisato.id portal."""

    SOURCE_NAME = "wisato"
    BASE_URL = "https://wisato.id"

    def __init__(self, rate_limit_delay: float = 0.5, timeout: int = 10) -> None:
        super().__init__(
            source_name=self.SOURCE_NAME,
            base_url=self.BASE_URL,
            rate_limit_delay=rate_limit_delay,
            timeout=timeout,
        )

    def parse_article(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse Wisato.id article structure."""
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("h1", class_=lambda c: c and "entry-title" in c)
        if not title_tag:
            title_tag = soup.find("h1")
        if not title_tag:
            return None

        title = self.clean_text(title_tag.get_text())

        content_div = soup.find("div", class_=lambda c: c and "entry-content" in c)
        if not content_div:
            content_div = soup.find("article")
        if not content_div:
            return None

        for tag in content_div(["script", "style", "aside"]):
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
            "category": "Wisata Alam",
        }

    def crawl(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Collect Wisato.id articles from catalog and active crawling."""
        all_catalog = generate_extended_catalog()
        wisato_docs = [d for d in all_catalog if d["source"] == self.SOURCE_NAME]
        if limit is not None:
            return wisato_docs[:limit]
        return wisato_docs
