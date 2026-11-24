"""Spiders package for scraping Indonesian tourism portals."""

from crawler.spiders.base_spider import BaseSpider
from crawler.spiders.nativeindonesia import NativeIndonesiaSpider
from crawler.spiders.indonesiatravel import IndonesiaTravelSpider
from crawler.spiders.wisato import WisatoSpider

__all__ = [
    "BaseSpider",
    "NativeIndonesiaSpider",
    "IndonesiaTravelSpider",
    "WisatoSpider",
]
