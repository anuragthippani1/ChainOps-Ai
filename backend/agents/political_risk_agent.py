import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.schemas import PoliticalRisk
import os

# Country name -> ISO 3166-1 alpha-2 (GNews API expects this)
COUNTRY_TO_ISO = {
    "United Kingdom": "gb", "France": "fr", "Germany": "de", "Italy": "it", "Spain": "es",
    "Netherlands": "nl", "Belgium": "be", "Poland": "pl", "Sweden": "se", "Austria": "at",
    "Portugal": "pt", "Greece": "gr", "Romania": "ro", "Czech Republic": "cz", "Hungary": "hu",
    "Ireland": "ie", "Norway": "no", "Finland": "fi", "Denmark": "dk", "Switzerland": "ch",
    "Ukraine": "ua", "Russia": "ru", "Belarus": "by", "Serbia": "rs", "Croatia": "hr",
    "Bulgaria": "bg", "Slovakia": "sk", "Slovenia": "si", "Lithuania": "lt", "Latvia": "lv",
    "Estonia": "ee", "Moldova": "md", "Bosnia and Herzegovina": "ba", "Albania": "al",
    "North Macedonia": "mk", "Montenegro": "me", "Kosovo": "xk", "Luxembourg": "lu",
    "Brazil": "br", "Argentina": "ar", "Chile": "cl", "Colombia": "co", "Peru": "pe",
    "Ecuador": "ec", "Bolivia": "bo", "Venezuela": "ve", "Uruguay": "uy", "Paraguay": "py",
    "Guyana": "gy", "Suriname": "sr",
    "South Africa": "za", "Nigeria": "ng", "Kenya": "ke", "Egypt": "eg", "Morocco": "ma",
    "Ghana": "gh", "Tanzania": "tz", "Ethiopia": "et", "Algeria": "dz", "Tunisia": "tn",
    "Angola": "ao", "Cameroon": "cm", "Senegal": "sn", "Ivory Coast": "ci", "Uganda": "ug",
    "Sudan": "sd", "Libya": "ly", "Zimbabwe": "zw", "Zambia": "zm", "Mozambique": "mz",
    "Madagascar": "mg", "Mali": "ml", "Burkina Faso": "bf", "Niger": "ne", "Chad": "td",
    "Somalia": "so", "Democratic Republic of the Congo": "cd", "Republic of the Congo": "cg",
    "Rwanda": "rw", "Botswana": "bw", "Namibia": "na", "Mauritius": "mu", "Gabon": "ga",
    "Benin": "bj", "Togo": "tg", "Malawi": "mw", "Mauritania": "mr",
    "China": "cn", "India": "in", "Japan": "jp", "United States": "us", "Canada": "ca",
    "Australia": "au", "Indonesia": "id", "Pakistan": "pk", "Iran": "ir", "Israel": "il",
    "Turkey": "tr", "Saudi Arabia": "sa", "South Korea": "kr", "Vietnam": "vn",
    "Thailand": "th", "Philippines": "ph", "Myanmar": "mm", "Bangladesh": "bd",
    "Sri Lanka": "lk", "Mexico": "mx", "Afghanistan": "af", "Yemen": "ye", "Syria": "sy",
    "North Korea": "kp", "Lebanon": "lb", "Palestine": "ps", "Haiti": "ht",
}

class PoliticalRiskAgent:
    def __init__(self):
        # News API endpoints
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.newsdata_api_key = os.getenv("NEWSDATA_API_KEY", "your-newsdata-key")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY", "your-gnews-key")
        # Keep provider calls responsive for dashboard requests.
        self.http_timeout = aiohttp.ClientTimeout(total=3)
        
        # Risk keywords to look for in news
        self.risk_keywords = [
            "tariff", "sanctions", "strike", "protest", "trade war",
            "embargo", "political unrest", "election", "policy change",
            "regulatory", "export ban", "import restriction", "currency",
            "inflation", "recession", "conflict", "tension"
        ]
    
    async def analyze_risks(self, countries: List[str]) -> List[PoliticalRisk]:
        """Analyze political risks for given countries"""
        async def _analyze_country(country: str) -> List[PoliticalRisk]:
            try:
                # Fetch news for each country
                news_articles = await self._fetch_news_for_country(country)

                # Analyze articles for risk indicators
                return await self._analyze_articles_for_risks(news_articles, country)

            except Exception as e:
                print(f"Error analyzing risks for {country}: {str(e)}")
                # Add a default risk entry if analysis fails
                default_risk = PoliticalRisk(
                    country=country,
                    risk_type="Analysis Error",
                    likelihood_score=1,
                    reasoning=f"Unable to fetch current data: {str(e)}",
                    publication_date=datetime.now().isoformat(),
                    source_title="System Error",
                    source_url=""
                )
                return [default_risk]

        results = await asyncio.gather(*[_analyze_country(country) for country in countries])
        all_risks: List[PoliticalRisk] = []
        for country_risks in results:
            all_risks.extend(country_risks)
        return all_risks
    
    async def _fetch_news_for_country(self, country: str) -> List[Dict[str, Any]]:
        """Fetch news articles for a specific country"""
        articles = []

        # Try NewsAPI first
        try:
            newsapi_articles = await self._fetch_from_newsapi(country)
            print(f"NewsAPI ({country}): {len(newsapi_articles)} articles")
            articles.extend(newsapi_articles)
        except Exception as e:
            print(f"NewsAPI error for {country}: {str(e)}")

        # Try NewsData.io second
        try:
            newsdata_articles = await self._fetch_from_newsdata(country)
            print(f"NewsData ({country}): {len(newsdata_articles)} articles")
            articles.extend(newsdata_articles)
        except Exception as e:
            print(f"NewsData.io error for {country}: {str(e)}")
        
        # Try GNews as backup
        try:
            gnews_articles = await self._fetch_from_gnews(country)
            print(f"GNews ({country}): {len(gnews_articles)} articles")
            articles.extend(gnews_articles)
        except Exception as e:
            print(f"GNews error for {country}: {str(e)}")
        
        # If all APIs fail, return sample data
        if not articles:
            articles = self._get_sample_news_data(country)
            print(f"Sample fallback ({country}): {len(articles)} articles")
        
        return articles

    async def _fetch_from_newsapi(self, country: str) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI.org."""
        if not self.newsapi_key:
            return []

        url = "https://newsapi.org/v2/everything"
        query = (
            f"{country} supply chain OR shipping OR port congestion OR "
            "trade sanctions OR logistics disruption OR oil supply OR maritime conflict"
        )
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": self.newsapi_key,
        }

        async with aiohttp.ClientSession(timeout=self.http_timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get("articles", [])
                    # Normalize keys expected by downstream processing.
                    for article in articles:
                        if article.get("publishedAt") and "pubDate" not in article:
                            article["pubDate"] = article.get("publishedAt")
                        if article.get("url") and "link" not in article:
                            article["link"] = article.get("url")
                    return articles
                raise Exception(f"NewsAPI error: {response.status}")
    
    async def _fetch_from_newsdata(self, country: str) -> List[Dict[str, Any]]:
        """Fetch news from NewsData.io API"""
        url = "https://newsdata.io/api/1/news"
        params = {
            "apikey": self.newsdata_api_key,
            "country": country.lower(),
            "category": "business,politics",
            "language": "en",
            "size": 10
        }
        
        async with aiohttp.ClientSession(timeout=self.http_timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    raise Exception(f"NewsData API error: {response.status}")
    
    def _country_to_iso(self, country: str) -> str:
        """Return ISO 2-letter code for GNews API; fallback to first 2 chars of lower name."""
        code = COUNTRY_TO_ISO.get(country)
        if code:
            return code
        # Fallback: some APIs accept generic or search-only (no country filter)
        return country.lower()[:2] if len(country) >= 2 else country.lower()

    async def _fetch_from_gnews(self, country: str) -> List[Dict[str, Any]]:
        """Fetch news from GNews API (country param expects ISO 2-letter code)"""
        url = "https://gnews.io/api/v4/search"
        country_iso = self._country_to_iso(country)
        params = {
            "token": self.gnews_api_key,
            "q": f"{country} trade politics economy",
            "lang": "en",
            "country": country_iso,
            "max": 10
        }
        
        async with aiohttp.ClientSession(timeout=self.http_timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("articles", [])
                else:
                    raise Exception(f"GNews API error: {response.status}")
    
    def _get_sample_news_data(self, country: str) -> List[Dict[str, Any]]:
        """Return sample news data when APIs are unavailable"""
        sample_articles = {
            "China": [
                {
                    "title": "China Implements New Export Controls on Technology",
                    "description": "New regulations affect semiconductor exports",
                    "content": "China has announced new export controls affecting technology sectors...",
                    "pubDate": datetime.now().isoformat(),
                    "link": "https://example.com/china-tech-export"
                }
            ],
            "Germany": [
                {
                    "title": "German Manufacturing Index Shows Decline",
                    "description": "Economic indicators suggest potential supply chain impacts",
                    "content": "The German manufacturing sector shows signs of contraction...",
                    "pubDate": datetime.now().isoformat(),
                    "link": "https://example.com/germany-manufacturing"
                }
            ],
            "India": [
                {
                    "title": "India Announces New Trade Policies",
                    "description": "Updated regulations affect international trade",
                    "content": "India's new trade policies aim to boost domestic manufacturing...",
                    "pubDate": datetime.now().isoformat(),
                    "link": "https://example.com/india-trade"
                }
            ],
            "Japan": [
                {
                    "title": "Japan's Supply Chain Resilience Initiative",
                    "description": "Government announces new supply chain security measures",
                    "content": "Japan is implementing new measures to strengthen supply chain security...",
                    "pubDate": datetime.now().isoformat(),
                    "link": "https://example.com/japan-supply-chain"
                }
            ],
            "Brazil": [
                {
                    "title": "Brazilian Port Workers Announce Strike",
                    "description": "Potential shipping delays expected",
                    "content": "Port workers in Brazil have announced a planned strike...",
                    "pubDate": datetime.now().isoformat(),
                    "link": "https://example.com/brazil-strike"
                }
            ],
            # Europe
            "France": [{"title": "France EU trade policy update", "description": "EU regulatory changes affect supply chains", "content": "France and EU partners are updating trade and customs rules...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/france-trade"}],
            "United Kingdom": [{"title": "UK post-Brexit trade developments", "description": "Customs and regulatory alignment", "content": "UK continues to align regulations with key trading partners...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/uk-trade"}],
            "Italy": [{"title": "Italian port and logistics reforms", "description": "Infrastructure and customs updates", "content": "Italy is modernizing port and logistics infrastructure...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/italy-logistics"}],
            "Spain": [{"title": "Spain supply chain and energy costs", "description": "Energy and transport impact on logistics", "content": "Spanish logistics face energy and transport cost pressures...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/spain-logistics"}],
            "Poland": [{"title": "Poland regional trade and transit", "description": "Central European transit hub developments", "content": "Poland remains a key transit country for EU trade...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/poland-transit"}],
            "Netherlands": [{"title": "Netherlands port congestion and capacity", "description": "Rotterdam and Amsterdam port updates", "content": "Dutch ports report capacity and congestion trends...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/netherlands-ports"}],
            "Portugal": [{"title": "Portugal maritime and EU trade", "description": "Atlantic and EU corridor trade", "content": "Portugal benefits from EU maritime trade corridors...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/portugal-trade"}],
            "Greece": [{"title": "Greece shipping and regional trade", "description": "Eastern Mediterranean logistics", "content": "Greece continues as a major shipping and transit hub...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/greece-shipping"}],
            "Romania": [{"title": "Romania EU integration and logistics", "description": "Eastern EU supply chain developments", "content": "Romania integrates further into EU supply chains...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/romania-eu"}],
            "Sweden": [{"title": "Sweden Nordic trade and sustainability", "description": "Green logistics and Nordic corridor", "content": "Sweden promotes sustainable logistics and Nordic trade...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/sweden-trade"}],
            "Austria": [{"title": "Austria Central European transit", "description": "Alpine and Danube corridor trade", "content": "Austria remains key for Central European transit...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/austria-transit"}],
            "Belgium": [{"title": "Belgium EU hub and port updates", "description": "Antwerp and Brussels logistics", "content": "Belgian ports and EU institutions drive trade policy...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/belgium-ports"}],
            "Ukraine": [{"title": "Ukraine recovery and trade corridors", "description": "Post-conflict logistics and reconstruction", "content": "Ukraine works to restore trade and logistics capacity...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/ukraine-trade"}],
            "Russia": [{"title": "Russia sanctions and trade restrictions", "description": "International sanctions impact", "content": "Russian trade remains under international sanctions...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/russia-sanctions"}],
            # South America
            "Argentina": [{"title": "Argentina economic and trade policy", "description": "Currency and export regulations", "content": "Argentina adjusts trade and currency policy...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/argentina-trade"}],
            "Chile": [{"title": "Chile Pacific trade and mining", "description": "Mining and Pacific corridor logistics", "content": "Chile remains a key Pacific trade and mining hub...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/chile-trade"}],
            "Colombia": [{"title": "Colombia security and logistics", "description": "Port and road security updates", "content": "Colombia improves security and logistics infrastructure...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/colombia-logistics"}],
            "Peru": [{"title": "Peru mining and export regulations", "description": "Mining and port developments", "content": "Peru updates mining and export regulations...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/peru-mining"}],
            "Ecuador": [{"title": "Ecuador trade and port developments", "description": "Pacific port and trade policy", "content": "Ecuador develops Pacific ports and trade policy...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/ecuador-trade"}],
            "Venezuela": [{"title": "Venezuela sanctions and economy", "description": "Political and economic risk", "content": "Venezuela faces ongoing political and economic challenges...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/venezuela-risk"}],
            "Uruguay": [{"title": "Uruguay stable trade environment", "description": "Mercosur and regional trade", "content": "Uruguay maintains stable trade and Mercosur ties...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/uruguay-trade"}],
            # Africa
            "South Africa": [{"title": "South Africa ports and power challenges", "description": "Port and energy supply impact", "content": "South African logistics face port and power challenges...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/south-africa-logistics"}],
            "Nigeria": [{"title": "Nigeria security and oil sector", "description": "Security and energy sector updates", "content": "Nigeria addresses security and oil sector developments...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/nigeria-energy"}],
            "Kenya": [{"title": "Kenya East Africa trade hub", "description": "East African corridor developments", "content": "Kenya strengthens position as East African trade hub...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/kenya-trade"}],
            "Egypt": [{"title": "Egypt Suez and regional trade", "description": "Suez Canal and regional logistics", "content": "Egypt continues to play a key role in regional trade...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/egypt-suez"}],
            "Morocco": [{"title": "Morocco EU and Africa trade", "description": "EU association and African trade", "content": "Morocco deepens EU and African trade links...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/morocco-trade"}],
            "Ghana": [{"title": "Ghana West Africa logistics", "description": "Port and regional trade", "content": "Ghana invests in port and regional trade capacity...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/ghana-ports"}],
            "Tanzania": [{"title": "Tanzania East Africa corridor", "description": "Port and transit developments", "content": "Tanzania develops port and transit corridors...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/tanzania-corridor"}],
            "Ethiopia": [{"title": "Ethiopia logistics and regional trade", "description": "Landlocked logistics developments", "content": "Ethiopia works on logistics and regional trade access...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/ethiopia-trade"}],
            "Algeria": [{"title": "Algeria energy and trade policy", "description": "Energy exports and regulations", "content": "Algeria updates energy and trade policy...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/algeria-energy"}],
            "Tunisia": [{"title": "Tunisia EU partnership and trade", "description": "Mediterranean trade links", "content": "Tunisia strengthens EU and Mediterranean trade...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/tunisia-eu"}],
            "Senegal": [{"title": "Senegal West Africa hub", "description": "Port and regional integration", "content": "Senegal develops as a West African logistics hub...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/senegal-hub"}],
            "Ivory Coast": [{"title": "Ivory Coast port and cocoa trade", "description": "Abidjan port and commodity trade", "content": "Ivory Coast port and cocoa trade face logistics updates...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/ivory-coast-trade"}],
            "Uganda": [{"title": "Uganda East Africa logistics", "description": "Landlocked trade corridors", "content": "Uganda works on East African trade corridors...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/uganda-logistics"}],
            "Angola": [{"title": "Angola oil and port developments", "description": "Energy and port infrastructure", "content": "Angola invests in oil and port infrastructure...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/angola-ports"}],
            "Cameroon": [{"title": "Cameroon Central Africa trade", "description": "Port and regional trade", "content": "Cameroon serves as Central African trade gateway...", "pubDate": datetime.now().isoformat(), "link": "https://example.com/cameroon-trade"}],
        }
        # Fallback: one generic article so we still get a risk entry for unmapped countries
        default_article = [
            {
                "title": f"Regional trade and policy monitoring – {country}",
                "description": "Supply chain and trade environment",
                "content": f"Ongoing monitoring of trade and political developments in {country}...",
                "pubDate": datetime.now().isoformat(),
                "link": "https://example.com/monitoring"
            }
        ]
        return sample_articles.get(country, default_article)
    
    async def _analyze_articles_for_risks(self, articles: List[Dict[str, Any]], country: str) -> List[PoliticalRisk]:
        """Analyze news articles for political risk indicators"""
        risks = []
        
        for article in articles:
            # Extract text content
            content = ""
            if "content" in article:
                content = article["content"]
            elif "description" in article:
                content = article["description"]
            elif "title" in article:
                content = article["title"]
            
            # Check for risk keywords
            risk_score = self._calculate_risk_score(content)
            
            if risk_score > 0:
                risk_type = self._identify_risk_type(content)
                reasoning = self._generate_reasoning(content, risk_type)
                
                risk = PoliticalRisk(
                    country=country,
                    risk_type=risk_type,
                    likelihood_score=risk_score,
                    reasoning=reasoning,
                    publication_date=article.get("pubDate", datetime.now().isoformat()),
                    source_title=article.get("title", "Unknown"),
                    source_url=article.get("link", "")
                )
                risks.append(risk)
        
        return risks
    
    def _calculate_risk_score(self, content: str) -> int:
        """Calculate risk score based on content analysis"""
        content_lower = content.lower()
        score = 0
        
        # Check for high-risk keywords
        high_risk_keywords = ["strike", "protest", "conflict", "war", "embargo", "sanctions"]
        for keyword in high_risk_keywords:
            if keyword in content_lower:
                score += 3
        
        # Check for medium-risk keywords
        medium_risk_keywords = ["tariff", "policy change", "regulation", "delay", "disruption"]
        for keyword in medium_risk_keywords:
            if keyword in content_lower:
                score += 2
        
        # Check for low-risk keywords
        low_risk_keywords = ["trade", "economic", "business", "manufacturing"]
        for keyword in low_risk_keywords:
            if keyword in content_lower:
                score += 1
        
        # Cap at 5
        return min(score, 5)
    
    def _identify_risk_type(self, content: str) -> str:
        """Identify the type of political risk"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["strike", "protest", "unrest"]):
            return "Labor Disputes"
        elif any(word in content_lower for word in ["tariff", "trade", "export", "import"]):
            return "Trade Policy"
        elif any(word in content_lower for word in ["sanctions", "embargo", "ban"]):
            return "Economic Sanctions"
        elif any(word in content_lower for word in ["regulation", "policy", "law"]):
            return "Regulatory Changes"
        elif any(word in content_lower for word in ["election", "political", "government"]):
            return "Political Instability"
        else:
            return "General Economic Risk"
    
    def _generate_reasoning(self, content: str, risk_type: str) -> str:
        """Generate reasoning for the risk assessment"""
        # Extract key phrases from content
        sentences = content.split('.')[:2]  # Take first two sentences
        key_info = '. '.join(sentences).strip()
        
        return f"Based on recent news: {key_info}. Risk type identified as {risk_type}."
