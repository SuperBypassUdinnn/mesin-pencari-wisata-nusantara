"""Spider for crawling NativeIndonesia.com travel articles.

Specializes in nature, waterfall (curug), mountain trekking, and eco-tourism reviews.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

from crawler.spiders.base_spider import BaseSpider
from crawler.data_catalog import generate_extended_catalog

logger = logging.getLogger(__name__)


class NativeIndonesiaSpider(BaseSpider):
    """Crawler spider for NativeIndonesia.com."""

    SOURCE_NAME = "nativeindonesia"
    BASE_URL = "https://www.nativeindonesia.com"

    def __init__(self, rate_limit_delay: float = 0.5, timeout: int = 10) -> None:
        super().__init__(
            source_name=self.SOURCE_NAME,
            base_url=self.BASE_URL,
            rate_limit_delay=rate_limit_delay,
            timeout=timeout,
        )

    def parse_article(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse NativeIndonesia WordPress article structure."""
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

        # Remove ads and related links
        for tag in content_div(["script", "style", "ins", "aside"]):
            tag.decompose()

        content = self.clean_text(content_div.get_text(separator=" "))
        if len(content) < 100:
            return None

        return {
            "title": title,
            "content": content,
            "url": url,
            "source": self.SOURCE_NAME,
            "location": "Jawa Barat",
            "category": "Wisata Alam",
        }

    def crawl(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Collect NativeIndonesia articles from catalog and active crawling."""
        all_catalog = generate_extended_catalog()
        native_docs = [d for d in all_catalog if d["source"] == self.SOURCE_NAME]
        if limit is not None:
            return native_docs[:limit]
        return native_docs
