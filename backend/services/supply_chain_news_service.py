"""
Real-time supply chain news fetching service.
Integrates NewsAPI and Mediastack. Fetches every 10 minutes, filters by supply chain keywords,
stores in MongoDB. Includes caching and error handling for API limits.
"""
import os
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import aiohttp

# Logistics and shipment related search queries only (no generic terms)
SEARCH_QUERIES = [
    "port congestion",
    "shipping delay",
    "container shortage",
    "freight disruption",
    "cargo delay",
    "port strike",
    "shipping strike",
    "shipping route disruption",
    "canal blockage",
    "maritime disruption",
    "logistics disruption",
    "cargo vessel delay",
    "shipping backlog",
]

# Strict filter: must contain at least one of these to be stored
LOGISTICS_KEYWORDS = [
    "port",
    "shipping",
    "shipping delays",
    "cargo",
    "cargo disruption",
    "container",
    "container shortage",
    "freight",
    "vessel",
    "port congestion",
    "shipment delay",
    "trade sanctions",
    "export ban",
    "import restriction",
    "oil supply disruption",
    "maritime attack",
    "canal blockage",
    "logistics strike",
    "transport disruption",
    "maritime",
    "red sea",
    "suez canal",
    "panama canal",
    "strait of hormuz",
    "hormuz strait",
    "malacca strait",
    "strait of malacca",
    "logistics",
    "canal",
    "harbor",
    "terminal",
    "customs delay",
]

# Reject articles with these (without logistics context)
BLACKLIST_KEYWORDS = [
    "food resilience",
    "government debate",
    "politics",
    "policy discussion",
    "economic outlook",
    "parliament",
    "minister speech",
]


class SupplyChainNewsService:
    def __init__(self, db_client=None):
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.mediastack_key = os.getenv("MEDIASTACK_API_KEY", "")
        self.gnews_key = os.getenv("GNEWS_API_KEY", "")
        self.db_client = db_client
        self._cache: Dict[str, Any] = {}
        self._cache_ttl_sec = 300  # 5 min cache for API responses
        self._last_fetch_ts: Optional[float] = None
        self._fetch_interval_sec = 600  # 10 min between fetches

    def _cache_key(self, source: str, query: str) -> str:
        return hashlib.md5(f"{source}:{query}".encode()).hexdigest()

    def _is_cache_valid(self, key: str) -> bool:
        if key not in self._cache:
            return False
        ts = self._cache[key].get("_ts")
        return ts and (datetime.utcnow().timestamp() - ts) < self._cache_ttl_sec

    def _get_cached(self, key: str) -> Optional[List[Dict]]:
        if self._is_cache_valid(key):
            return self._cache[key].get("data")
        return None

    def _set_cached(self, key: str, data: List[Dict]) -> None:
        self._cache[key] = {"data": data, "_ts": datetime.utcnow().timestamp()}

    def _should_fetch(self) -> bool:
        if self._last_fetch_ts is None:
            return True
        return (datetime.utcnow().timestamp() - self._last_fetch_ts) >= self._fetch_interval_sec

    def _has_logistics_keyword(self, text: str) -> bool:
        """Title or description must contain at least one logistics keyword."""
        t = (text or "").lower()
        return any(kw.lower() in t for kw in LOGISTICS_KEYWORDS)

    def _has_blacklist_keyword(self, text: str) -> bool:
        """Check if article contains blacklisted terms."""
        t = (text or "").lower()
        return any(kw.lower() in t for kw in BLACKLIST_KEYWORDS)

    def _passes_strict_filter(self, title: str, description: str) -> bool:
        """Must have logistics keyword. Reject if blacklist without logistics."""
        combined = f"{title or ''} {description or ''}"
        has_logistics = self._has_logistics_keyword(combined)
        has_blacklist = self._has_blacklist_keyword(combined)
        if not has_logistics:
            return False
        if has_blacklist and not has_logistics:
            return False
        return True

    async def _fetch_newsapi(self, query: str) -> List[Dict[str, Any]]:
        """Fetch from NewsAPI. Requires NEWSAPI_KEY."""
        if not self.newsapi_key or self.newsapi_key in ("", "your-newsapi-key"):
            return []
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": self.newsapi_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 429:
                        print("NewsAPI: Rate limit reached, skipping")
                        return []
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    articles = data.get("articles", [])
                    return [a for a in articles if a.get("title") and self._passes_strict_filter(
                        a.get("title", ""), a.get("description", "")
                    )]
        except asyncio.TimeoutError:
            print("NewsAPI: Request timeout")
            return []
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []

    async def _fetch_gnews(self, query: str) -> List[Dict[str, Any]]:
        """Fetch from GNews API. Requires GNEWS_API_KEY."""
        if not self.gnews_key or self.gnews_key in ("", "your-gnews-key"):
            return []
        url = "https://gnews.io/api/v4/search"
        params = {
            "token": self.gnews_key,
            "q": query,
            "lang": "en",
            "max": 15,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 429:
                        print("GNews: Rate limit reached, skipping")
                        return []
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    articles = data.get("articles", [])
                    return [a for a in articles if a.get("title") and self._passes_strict_filter(
                        a.get("title", ""), a.get("description", "")
                    )]
        except asyncio.TimeoutError:
            print("GNews: Request timeout")
            return []
        except Exception as e:
            print(f"GNews error: {e}")
            return []

    async def _fetch_mediastack(self, query: str) -> List[Dict[str, Any]]:
        """Fetch from Mediastack. Requires MEDIASTACK_API_KEY."""
        if not self.mediastack_key or self.mediastack_key in ("", "your-mediastack-key"):
            return []
        url = "http://api.mediastack.com/v1/news"
        params = {
            "access_key": self.mediastack_key,
            "keywords": query,
            "languages": "en",
            "limit": 25,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 429:
                        print("Mediastack: Rate limit reached, skipping")
                        return []
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    articles = data.get("data", [])
                    return [a for a in articles if a.get("title") and self._passes_strict_filter(
                        a.get("title", ""), a.get("description", "")
                    )]
        except asyncio.TimeoutError:
            print("Mediastack: Request timeout")
            return []
        except Exception as e:
            print(f"Mediastack error: {e}")
            return []

    async def fetch_all_news(self) -> List[Dict[str, Any]]:
        """Fetch from all configured APIs, deduplicate by URL."""
        all_articles = []
        seen_urls = set()

        for query in SEARCH_QUERIES[:3]:  # Limit to avoid rate limits
            # Try cache first
            cache_key_na = self._cache_key("newsapi", query)
            cache_key_ms = self._cache_key("mediastack", query)

            newsapi_results = self._get_cached(cache_key_na)
            if newsapi_results is None:
                newsapi_results = await self._fetch_newsapi(query)
                self._set_cached(cache_key_na, newsapi_results)

            for a in newsapi_results:
                url = a.get("url") or a.get("urlToImage") or ""
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append({
                        "title": a.get("title", ""),
                        "description": a.get("description") or "",
                        "content": a.get("content") or a.get("description") or "",
                        "url": url,
                        "source": a.get("source", {}).get("name", "NewsAPI"),
                        "published_at": a.get("publishedAt", datetime.utcnow().isoformat()),
                        "raw": a,
                    })

            mediastack_results = self._get_cached(cache_key_ms)
            if mediastack_results is None:
                mediastack_results = await self._fetch_mediastack(query)
                self._set_cached(cache_key_ms, mediastack_results)

            for a in mediastack_results:
                url = a.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append({
                        "title": a.get("title", ""),
                        "description": a.get("description") or "",
                        "content": a.get("description") or "",
                        "url": url,
                        "source": a.get("source", "Mediastack"),
                        "published_at": a.get("published_at", datetime.utcnow().isoformat()),
                        "raw": a,
                    })

            gnews_results = self._get_cached(self._cache_key("gnews", query))
            if gnews_results is None:
                gnews_results = await self._fetch_gnews(query)
                self._set_cached(self._cache_key("gnews", query), gnews_results)

            for a in gnews_results:
                url = a.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append({
                        "title": a.get("title", ""),
                        "description": a.get("description") or "",
                        "content": a.get("content") or a.get("description") or "",
                        "url": url,
                        "source": a.get("source", {}).get("name", "GNews") if isinstance(a.get("source"), dict) else "GNews",
                        "published_at": a.get("publishedAt", datetime.utcnow().isoformat()),
                        "raw": a,
                    })

            await asyncio.sleep(1)  # Rate limit between queries

        self._last_fetch_ts = datetime.utcnow().timestamp()
        return all_articles

    async def run_fetch_and_store(self) -> int:
        """Fetch news, process with NLP, store in MongoDB. Returns count stored."""
        if not self._should_fetch() and self.db_client:
            # Still return count from DB for last 24h
            try:
                alerts = await self.db_client.get_supply_chain_news_last_24h()
                return len(alerts)
            except Exception:
                pass
            return 0

        articles = await self.fetch_all_news()
        if not articles:
            return 0

        from services.news_nlp_processor import NewsNLPProcessor
        processor = NewsNLPProcessor()
        stored = 0

        for art in articles:
            try:
                processed = await processor.process_article(art)
                if processed and self.db_client:
                    await self.db_client.store_supply_chain_news(processed)
                    stored += 1
            except Exception as e:
                print(f"Error processing article: {e}")

        return stored
