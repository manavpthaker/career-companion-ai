"""Company Intelligence Engine using News API for deep research."""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

class CompanyIntelligenceEngine:
    """Research companies using news APIs and web sources."""
    
    def __init__(self, logger=None):
        """Initialize the intelligence engine."""
        self.logger = logger or logging.getLogger(__name__)
        
        # API Keys
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        
        # Preferred news sources for business intelligence
        self.trusted_sources = [
            'techcrunch', 'bloomberg', 'reuters', 'the-wall-street-journal',
            'financial-times', 'business-insider', 'forbes', 'fortune',
            'the-verge', 'wired', 'cnbc', 'venture-beat'
        ]
        
        # Source credibility scores
        self.source_credibility = {
            'the-wall-street-journal': 95,
            'reuters': 92,
            'bloomberg': 90,
            'financial-times': 88,
            'techcrunch': 85,
            'forbes': 80,
            'fortune': 80,
            'business-insider': 75,
            'cnbc': 75,
            'the-verge': 70,
            'wired': 70,
            'venture-beat': 65
        }
        
        # Cache for API responses
        self.cache_dir = Path('data/company_research_cache')
        self.cache_dir.mkdir(exist_ok=True)
    
    async def research_company(self, company_name: str, job_title: str = None) -> Dict[str, Any]:
        """Comprehensive company research combining multiple sources."""
        
        self.logger.info(f"🔍 Researching {company_name}")
        
        research = {
            'company': company_name,
            'research_date': datetime.now().isoformat(),
            'recent_news': [],
            'key_events': [],
            'company_momentum': 'unknown',
            'talking_points': [],
            'strategic_initiatives': [],
            'challenges': [],
            'culture_values': [],
            'leadership_changes': [],
            'financial_events': [],
            'product_launches': [],
            'industry_position': ''
        }
        
        # Check cache first
        cached = self._get_cached_research(company_name)
        if cached and self._is_cache_fresh(cached):
            self.logger.info(f"✅ Using cached research for {company_name}")
            return cached
        
        # Fetch news from multiple sources
        if self.news_api_key:
            news_data = await self._fetch_news_api(company_name)
            research['recent_news'] = news_data['articles']
            
            # Analyze news for insights
            insights = self._analyze_news_content(news_data['articles'])
            research.update(insights)
        
        # Generate talking points based on research
        research['talking_points'] = self._generate_talking_points(research, job_title)
        
        # Determine company momentum
        research['company_momentum'] = self._assess_company_momentum(research)
        
        # Cache the research
        self._cache_research(company_name, research)
        
        return research
    
    async def _fetch_news_api(self, company_name: str) -> Dict[str, Any]:
        """Fetch news from NewsAPI."""
        
        # Calculate date range (last 30 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': f'"{company_name}"',
            'apiKey': self.news_api_key,
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'sortBy': 'relevancy',
            'language': 'en',
            'pageSize': 20
        }
        
        # Add trusted sources if available
        if self.trusted_sources:
            params['sources'] = ','.join(self.trusted_sources[:5])  # Top 5 sources
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Enhance articles with credibility scores
                        for article in data.get('articles', []):
                            source_id = article.get('source', {}).get('id', '')
                            article['credibility_score'] = self.source_credibility.get(source_id, 60)
                            article['relevance'] = self._calculate_relevance(article, company_name)
                        
                        # Sort by credibility and relevance
                        data['articles'] = sorted(
                            data.get('articles', []),
                            key=lambda x: x['credibility_score'] * x['relevance'],
                            reverse=True
                        )[:10]  # Top [STREET_ADDRESS] credible and relevant
                        
                        return data
                    else:
                        self.logger.warning(f"News API returned status {response.status}")
                        return {'articles': []}
                        
        except Exception as e:
            self.logger.error(f"Error fetching news: {e}")
            return {'articles': []}
    
    def _analyze_news_content(self, articles: List[Dict]) -> Dict[str, Any]:
        """Analyze news articles for key insights."""
        
        insights = {
            'key_events': [],
            'strategic_initiatives': [],
            'challenges': [],
            'leadership_changes': [],
            'financial_events': [],
            'product_launches': []
        }
        
        # Keywords for categorization
        categories = {
            'financial_events': ['funding', 'revenue', 'ipo', 'acquisition', 'merger', 'investment', 'valuation', 'earnings'],
            'product_launches': ['launch', 'release', 'announce', 'introduce', 'unveil', 'new product', 'new feature'],
            'leadership_changes': ['ceo', 'cto', 'cfo', 'hire', 'appoint', 'resign', 'departure', 'leadership'],
            'strategic_initiatives': ['strategy', 'partnership', 'expansion', 'initiative', 'transformation', 'pivot'],
            'challenges': ['layoff', 'lawsuit', 'challenge', 'issue', 'problem', 'decline', 'loss', 'struggle']
        }
        
        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            # Categorize article
            for category, keywords in categories.items():
                if any(keyword in content for keyword in keywords):
                    event = {
                        'title': article.get('title'),
                        'date': article.get('publishedAt'),
                        'source': article.get('source', {}).get('name'),
                        'url': article.get('url'),
                        'summary': article.get('description')
                    }
                    
                    insights[category].append(event)
                    
                    # Add to key events if highly credible
                    if article.get('credibility_score', 0) >= 80:
                        insights['key_events'].append(event)
        
        # Limit to top events per category
        for category in insights:
            insights[category] = insights[category][:3]
        
        return insights
    
    def _calculate_relevance(self, article: Dict, company_name: str) -> float:
        """Calculate relevance score for an article."""
        
        relevance = 0.5  # Base score
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        company_lower = company_name.lower()
        
        # Title mentions
        if company_lower in title:
            relevance += 0.3
        
        # Description mentions
        if company_lower in description:
            relevance += 0.2
        
        # Recency bonus (more recent = more relevant)
        published = article.get('publishedAt', '')
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
                if days_old <= 7:
                    relevance += 0.2
                elif days_old <= 14:
                    relevance += 0.1
            except:
                pass
        
        return min(relevance, 1.0)
    
    def _generate_talking_points(self, research: Dict, job_title: str = None) -> List[str]:
        """Generate interview talking points based on research."""
        
        talking_points = []
        
        # Recent achievements
        if research['financial_events']:
            event = research['financial_events'][0]
            talking_points.append(
                f"Congratulations on {event['title']} - how is this impacting the product roadmap?"
            )
        
        # Product launches
        if research['product_launches']:
            launch = research['product_launches'][0]
            talking_points.append(
                f"I saw the recent {launch['title']} - I'd love to discuss how my experience with {self._get_relevant_experience(launch)} could contribute"
            )
        
        # Strategic initiatives
        if research['strategic_initiatives']:
            initiative = research['strategic_initiatives'][0]
            talking_points.append(
                f"Your {initiative['title']} aligns with my work on {self._get_relevant_experience(initiative)}"
            )
        
        # Challenges (frame positively)
        if research['challenges']:
            challenge = research['challenges'][0]
            talking_points.append(
                f"I've navigated similar challenges at my previous companies and have ideas on approaching {self._extract_challenge_type(challenge)}"
            )
        
        # Leadership changes
        if research['leadership_changes']:
            change = research['leadership_changes'][0]
            talking_points.append(
                f"With the recent {change['title']}, I imagine there are exciting new directions for the product team"
            )
        
        # Job-specific talking point
        if job_title:
            if 'ai' in job_title.lower() or 'ml' in job_title.lower():
                talking_points.append(
                    "I'd love to share how I reduced PM overhead by 80% using multi-agent AI systems at [CURRENT_COMPANY]"
                )
            elif 'director' in job_title.lower() or 'principal' in job_title.lower():
                talking_points.append(
                    "Having led 15-20 person cross-functional teams, I understand the challenges of scaling product organizations"
                )
        
        return talking_points[:5]  # Top 5 talking points
    
    def _get_relevant_experience(self, event: Dict) -> str:
        """Map event to relevant personal experience."""
        
        # This would be enhanced with personal context manager
        event_text = str(event).lower()
        
        if 'ai' in event_text or 'ml' in event_text:
            return "LLM orchestration and AI platform development"
        elif 'growth' in event_text or 'scale' in event_text:
            return "scaling products from 0 to 20K+ users"
        elif 'platform' in event_text:
            return "platform thinking and reusable component libraries"
        elif 'revenue' in event_text or 'monetization' in event_text:
            return "achieving <$10 CAC with LTV >$1,000"
        else:
            return "end-to-end product development"
    
    def _extract_challenge_type(self, challenge: Dict) -> str:
        """Extract the type of challenge for positive framing."""
        
        challenge_text = str(challenge).lower()
        
        if 'layoff' in challenge_text:
            return "organizational efficiency"
        elif 'competition' in challenge_text:
            return "competitive differentiation"
        elif 'regulation' in challenge_text:
            return "regulatory compliance"
        elif 'growth' in challenge_text:
            return "sustainable scaling"
        else:
            return "operational challenges"
    
    def _assess_company_momentum(self, research: Dict) -> str:
        """Assess overall company momentum based on news."""
        
        positive_signals = len(research['financial_events']) + len(research['product_launches']) + len(research['strategic_initiatives'])
        negative_signals = len(research['challenges'])
        
        if positive_signals > negative_signals * 2:
            return 'strong_growth'
        elif positive_signals > negative_signals:
            return 'steady_growth'
        elif negative_signals > positive_signals:
            return 'facing_challenges'
        else:
            return 'stable'
    
    def _get_cached_research(self, company_name: str) -> Optional[Dict]:
        """Get cached research for a company."""
        
        cache_file = self.cache_dir / f"{company_name.lower().replace(' ', '_')}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def _is_cache_fresh(self, cached_data: Dict, max_age_hours: int = 24) -> bool:
        """Check if cached data is still fresh."""
        
        if 'research_date' not in cached_data:
            return False
        
        try:
            cached_date = datetime.fromisoformat(cached_data['research_date'])
            age = datetime.now() - cached_date
            return age.total_seconds() < (max_age_hours * 3600)
        except:
            return False
    
    def _cache_research(self, company_name: str, research: Dict):
        """Cache research data for a company."""
        
        cache_file = self.cache_dir / f"{company_name.lower().replace(' ', '_')}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(research, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error caching research: {e}")