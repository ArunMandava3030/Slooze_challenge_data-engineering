"""
# src/collectors/alibaba.py
import asyncio
from typing import List, Dict, Any
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from bs4 import BeautifulSoup
from src.collectors.base import BaseCollector
from src.utils.throttle import polite_sleep
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from src.models.product import Product

class AlibabaCollector(BaseCollector):
    async def arun(self, url: str):
        browser_config = BrowserConfig(headless=True, verbose=False)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            crawler_config = CrawlerRunConfig(
                extraction_schema=Product.model_json_schema(),  # <── Structured extraction
                extraction_prompt=(
                    "Extract all product listings from this page. "
                    "Each product should have: name, price (if available), company, description, and link."
                ),
            )
            result = await crawler.arun(url=url, config=crawler_config)
            return result.extracted_content or []
    def collect(self, category: str, category_url: str, limit=100, save_raw=False) -> List[Dict[str, Any]]:
        out, page = [], 1
        seen = set()
        while len(out) < limit and page <= 20:
            page_url = category_url.replace("_p1", f"_p{page}")
            print(f"[CRAWL4AI] Alibaba page {page}: {page_url}")
            html = asyncio.run(self.arun(page_url))
            if not html:
                break

            if save_raw:
                p = Path(self.config.get("raw_dir", "data/raw")) / "alibaba"
                p.mkdir(parents=True, exist_ok=True)
                (p / f"{category.replace(' ','_')}_p{page}.html").write_text(html, encoding="utf-8")

            soup = BeautifulSoup(html, "html.parser")
            nodes = soup.select("div.list-no-v2-outter") or soup.select("a[href*='product-detail']")
            if not nodes:
                break

            for node in nodes:
                if len(out) >= limit:
                    break
                title_node = node.select_one(".elements-title-normal__content, a")
                title = title_node.get_text(" ", strip=True) if title_node else None
                link_node = node.select_one("a[href*='offer']") or node.select_one("a[href*='product-detail']")
                url = link_node["href"] if link_node and link_node.has_attr("href") else None
                if url and url.startswith("//"):
                    url = "https:" + url
                if not title or not url or (url, title) in seen:
                    continue
                seen.add((url, title))

                item = {
                    "marketplace": "alibaba",
                    "category": category,
                    "title": title,
                    "price_min": None,
                    "price_max": None,
                    "currency": None,
                    "unit": None,
                    "supplier_name": None,
                    "supplier_location": None,
                    "url": url,
                    "source_html_snippet": str(node)[:500]
                }
                out.append(item)

            page += 1
            polite_sleep(self.config.get("delay_min", 1.0), self.config.get("delay_max", 2.0))
        return out
"""
# src/collectors/alibaba.py
import asyncio
import re
from typing import List, Dict, Any
from pathlib import Path
from urllib.parse import urljoin

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from bs4 import BeautifulSoup

from src.collectors.base import BaseCollector
from src.utils.throttle import polite_sleep


class AlibabaCollector(BaseCollector):
    async def arun(self, url: str) -> str:
        browser_config = BrowserConfig(headless=True, verbose=False)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            crawler_config = CrawlerRunConfig()
            result = await crawler.arun(url=url, config=crawler_config)
            return result.html or ""

    def _looks_like_product_link(self, href: str) -> bool:
        if not href:
            return False
        href = href.lower()
        tokens = ["product-detail", "offer", "offer/","/product/","/product-detail", "/offer", "alibaba.com/product"]
        return any(t in href for t in tokens)

    def _extract_price(self, text: str):
        if not text:
            return None
        m = re.search(r'((?:₹|Rs\.?|INR|\$|US\$\s?)\s?[\d,]+(?:\.\d+)?(?:\s*-\s*[\d,]+(?:\.\d+)?)?)', text, re.I)
        return m.group(1).strip() if m else None

    def collect(self, category: str, category_url: str, limit=100, save_raw=False) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        page = 1
        seen = set()

        while len(out) < limit and page <= 50:
            page_url = category_url.replace("_p1", f"_p{page}") if "_p1" in category_url else f"{category_url}?page={page}"
            print(f"[CRAWL4AI] Alibaba page {page}: {page_url}")

            html = asyncio.run(self.arun(page_url))
            if not html:
                break

            if save_raw:
                p = Path(self.config.get("raw_dir", "data/raw")) / "alibaba"
                p.mkdir(parents=True, exist_ok=True)
                (p / f"{category.replace(' ', '_')}_p{page}.html").write_text(html, encoding="utf-8")

            soup = BeautifulSoup(html, "html.parser")

            # Prefer explicit product container selectors if present (fast case)
            nodes = soup.select("div.list-no-v2-outter, div.J-offer-wrapper, li.list-item")
            candidates = nodes if nodes else []

            if not candidates:
                # fallback: find product-like anchors across the page
                anchors = soup.find_all("a", href=True)
                for a in anchors:
                    href = a["href"].strip()
                    full = href if href.startswith("http") else urljoin(page_url, href)
                    if self._looks_like_product_link(full):
                        candidates.append(a)

            if not candidates:
                print("[INFO] no product candidates found on this page, stopping")
                break

            for node in candidates:
                if len(out) >= limit:
                    break

                if node.name == "a":
                    a = node
                else:
                    a = node.select_one("a[href]") or node

                title = (a.get_text(" ", strip=True) or a.get("title") or "").strip()
                href = a.get("href", "").strip()
                if href.startswith("//"):
                    href = "https:" + href
                if href and not href.startswith("http"):
                    href = urljoin(page_url, href)

                parent = a
                for _ in range(3):
                    if parent and parent.parent:
                        parent = parent.parent
                snippet_text = parent.get_text(" ", strip=True) if parent else a.get_text(" ", strip=True)
                snippet_html = str(parent)[:1200] if parent else ""

                if not title or not href:
                    continue

                key = (href, title.lower())
                if key in seen:
                    continue
                seen.add(key)

                price = self._extract_price(snippet_text)

                # supplier heuristics
                supplier_node = parent.select_one("[class*='supplier'], [class*='company'], .organic-gallery-title__seller, .company-name") if parent else None
                supplier = supplier_node.get_text(" ", strip=True) if supplier_node else None

                item = {
                    "marketplace": "alibaba",
                    "category": category,
                    "title": title,
                    "price": price,
                    "supplier_name": supplier,
                    "url": href,
                    "source_html_snippet": snippet_html
                }
                out.append(item)

            page += 1
            polite_sleep(self.config.get("delay_min", 1.0), self.config.get("delay_max", 2.0))

        print(f"[INFO] Alibaba extracted {len(out)} items for category '{category}'")
        return out

