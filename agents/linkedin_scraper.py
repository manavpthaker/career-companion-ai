"""LinkedIn Job Scraper using Playwright for detailed job extraction."""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from playwright.async_api import async_playwright, Page, Browser
import time

class LinkedInScraper:
    """Scrape LinkedIn job postings with Playwright."""
    
    def __init__(self, logger=None, headless=True):
        """Initialize the LinkedIn scraper."""
        self.logger = logger or logging.getLogger(__name__)
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        
        # Cache directory for scraped data
        self.cache_dir = Path('data/linkedin_cache')
        self.cache_dir.mkdir(exist_ok=True)
        
        # Selectors for LinkedIn job pages
        self.selectors = {
            'title': 'h1.jobs-unified-top-card__job-title',
            'company': 'div.jobs-unified-top-card__company-name a',
            'location': 'span.jobs-unified-top-card__bullet',
            'workplace_type': 'span.jobs-unified-top-card__workplace-type',
            'posted_time': 'span.jobs-unified-top-card__posted-date',
            'applicants': 'span.jobs-unified-top-card__applicant-count',
            'description': 'div.jobs-description__content',
            'seniority': 'span.description__job-criteria-text',
            'employment_type': 'span.description__job-criteria-text',
            'job_function': 'span.description__job-criteria-text',
            'industries': 'span.description__job-criteria-text',
            # Alternative selectors for different page layouts
            'alt_title': 'h2.jobs-details-top-card__job-title',
            'alt_company': 'a.jobs-details-top-card__company-url',
            'alt_location': 'div.jobs-details-top-card__bullet',
            'alt_description': 'article.jobs-description'
        }
    
    async def initialize(self):
        """Initialize browser and page."""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context with realistic viewport and user agent
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Add cookies to appear more legitimate
            await self.context.add_cookies([
                {
                    'name': 'li_at',
                    'value': 'dummy_session',
                    'domain': '.linkedin.com',
                    'path': '/'
                }
            ])
            
            self.page = await self.context.new_page()
            
            # Set extra headers
            await self.page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            })
    
    async def close(self):
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def scrape_job(self, url: str) -> Dict[str, Any]:
        """Scrape a single LinkedIn job posting."""
        
        # Check cache first
        cached_data = self._get_cached_job(url)
        if cached_data:
            self.logger.info(f"Using cached data for {url}")
            return cached_data
        
        await self.initialize()
        
        job_data = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'source': 'LinkedIn'
        }
        
        try:
            # Navigate to job page
            self.logger.info(f"Scraping {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await self.page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Additional wait for dynamic content
            
            # Try to dismiss any popups
            await self._dismiss_popups()
            
            # Extract job details
            job_data.update(await self._extract_job_details())
            
            # Cache the scraped data
            self._cache_job(url, job_data)
            
            self.logger.info(f"Successfully scraped: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            job_data['error'] = str(e)
            
            # Try alternative extraction for public job view
            try:
                job_data.update(await self._extract_public_job_details())
            except Exception as e2:
                self.logger.error(f"Alternative extraction also failed: {e2}")
        
        return job_data
    
    async def _extract_job_details(self) -> Dict[str, Any]:
        """Extract job details from LinkedIn page."""
        
        details = {}
        
        # Title
        try:
            title_elem = await self.page.query_selector(self.selectors['title'])
            if not title_elem:
                title_elem = await self.page.query_selector(self.selectors['alt_title'])
            if title_elem:
                details['title'] = await title_elem.inner_text()
        except:
            pass
        
        # Company
        try:
            company_elem = await self.page.query_selector(self.selectors['company'])
            if not company_elem:
                company_elem = await self.page.query_selector(self.selectors['alt_company'])
            if company_elem:
                details['company'] = await company_elem.inner_text()
        except:
            pass
        
        # Location
        try:
            location_elem = await self.page.query_selector(self.selectors['location'])
            if not location_elem:
                location_elem = await self.page.query_selector(self.selectors['alt_location'])
            if location_elem:
                details['location'] = await location_elem.inner_text()
        except:
            pass
        
        # Workplace type (Remote/Hybrid/Onsite)
        try:
            workplace_elem = await self.page.query_selector(self.selectors['workplace_type'])
            if workplace_elem:
                details['workplace_type'] = await workplace_elem.inner_text()
        except:
            pass
        
        # Posted time
        try:
            posted_elem = await self.page.query_selector(self.selectors['posted_time'])
            if posted_elem:
                details['posted_time'] = await posted_elem.inner_text()
        except:
            pass
        
        # Number of applicants
        try:
            applicants_elem = await self.page.query_selector(self.selectors['applicants'])
            if applicants_elem:
                details['applicants'] = await applicants_elem.inner_text()
        except:
            pass
        
        # Job description
        try:
            desc_elem = await self.page.query_selector(self.selectors['description'])
            if not desc_elem:
                desc_elem = await self.page.query_selector(self.selectors['alt_description'])
            if desc_elem:
                details['description'] = await desc_elem.inner_text()
                
                # Extract key information from description
                details.update(self._parse_description(details['description']))
        except:
            pass
        
        # Job criteria (seniority, employment type, etc.)
        try:
            criteria_elements = await self.page.query_selector_all('li.description__job-criteria-item')
            for elem in criteria_elements:
                label_elem = await elem.query_selector('h3')
                value_elem = await elem.query_selector('span')
                
                if label_elem and value_elem:
                    label = await label_elem.inner_text()
                    value = await value_elem.inner_text()
                    
                    if 'seniority' in label.lower():
                        details['seniority_level'] = value
                    elif 'employment' in label.lower():
                        details['employment_type'] = value
                    elif 'function' in label.lower():
                        details['job_function'] = value
                    elif 'industries' in label.lower():
                        details['industries'] = value
        except:
            pass
        
        return details
    
    async def _extract_public_job_details(self) -> Dict[str, Any]:
        """Extract details from public job view (no login required)."""
        
        details = {}
        
        # Try to extract from meta tags
        try:
            # Title from page title
            title = await self.page.title()
            if title:
                # LinkedIn titles are usually formatted as "Job Title - Company | LinkedIn"
                parts = title.split(' - ')
                if parts:
                    details['title'] = parts[0].strip()
                    if len(parts) > 1:
                        company_part = parts[1].split('|')[0].strip()
                        details['company'] = company_part
        except:
            pass
        
        # Try to extract from any visible text
        try:
            # Get all text content
            body_text = await self.page.inner_text('body')
            
            # Look for patterns
            if 'Remote' in body_text:
                details['workplace_type'] = 'Remote'
            elif 'Hybrid' in body_text:
                details['workplace_type'] = 'Hybrid'
            elif 'On-site' in body_text or 'Onsite' in body_text:
                details['workplace_type'] = 'On-site'
            
            # Extract salary if mentioned
            salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per|/)\s*(?:year|yr|annually))?'
            salary_match = re.search(salary_pattern, body_text)
            if salary_match:
                details['salary'] = salary_match.group(0)
            
            # Set description to visible text if we couldn't get structured data
            if 'description' not in details:
                details['description'] = body_text[:5000]  # First 5000 chars
        except:
            pass
        
        return details
    
    def _parse_description(self, description: str) -> Dict[str, Any]:
        """Parse job description for key information."""
        
        parsed = {}
        desc_lower = description.lower()
        
        # Required experience
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\s*-\s*(\d+)\s*years?\s*(?:of\s*)?experience'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                if match.lastindex == 2:
                    parsed['required_experience'] = f"{match.group(1)}-{match.group(2)} years"
                else:
                    parsed['required_experience'] = f"{match.group(1)}+ years"
                break
        
        # Technical requirements
        tech_keywords = ['python', 'java', 'sql', 'aws', 'azure', 'gcp', 'kubernetes', 
                        'docker', 'react', 'node', 'tensorflow', 'pytorch', 'llm', 
                        'genai', 'machine learning', 'deep learning', 'nlp']
        
        found_tech = [tech for tech in tech_keywords if tech in desc_lower]
        if found_tech:
            parsed['technical_requirements'] = found_tech
        
        # Salary information
        salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per|/)\s*(?:year|yr|annually))?'
        salary_match = re.search(salary_pattern, description)
        if salary_match:
            parsed['salary'] = salary_match.group(0)
        
        # Education requirements
        if 'bachelor' in desc_lower or 'bs' in desc_lower or 'ba' in desc_lower:
            parsed['education'] = "Bachelor's degree"
        elif 'master' in desc_lower or 'ms' in desc_lower or 'mba' in desc_lower:
            parsed['education'] = "Master's degree"
        elif 'phd' in desc_lower or 'doctorate' in desc_lower:
            parsed['education'] = "PhD/Doctorate"
        
        # Team size
        team_pattern = r'(?:manage|lead|oversee)\s*(?:a\s*)?team\s*of\s*(\d+)'
        team_match = re.search(team_pattern, desc_lower)
        if team_match:
            parsed['team_size'] = f"{team_match.group(1)} people"
        
        return parsed
    
    async def _dismiss_popups(self):
        """Try to dismiss common LinkedIn popups."""
        
        try:
            # Try to click "Not now" on sign-in prompt
            not_now = await self.page.query_selector('button:has-text("Not now")')
            if not_now:
                await not_now.click()
                await asyncio.sleep(1)
        except:
            pass
        
        try:
            # Try to dismiss cookie banner
            dismiss = await self.page.query_selector('button[action-type="DISMISS"]')
            if dismiss:
                await dismiss.click()
                await asyncio.sleep(1)
        except:
            pass
    
    def _get_cached_job(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached job data if available and fresh."""
        
        # Create cache key from URL
        job_id = self._extract_job_id(url)
        if not job_id:
            return None
        
        cache_file = self.cache_dir / f"{job_id}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # Check if cache is fresh (less than 7 days old)
                cached_time = datetime.fromisoformat(data.get('scraped_at', ''))
                age = datetime.now() - cached_time
                
                if age.days < 7:
                    return data
            except:
                pass
        
        return None
    
    def _cache_job(self, url: str, data: Dict[str, Any]):
        """Cache job data."""
        
        job_id = self._extract_job_id(url)
        if not job_id:
            return
        
        cache_file = self.cache_dir / f"{job_id}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error caching job data: {e}")
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL."""
        
        # Pattern: /jobs/view/1234567890/
        match = re.search(r'/jobs/view/(\d+)', url)
        if match:
            return match.group(1)
        
        return None
    
    async def scrape_multiple_jobs(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple job URLs."""
        
        results = []
        
        await self.initialize()
        
        for url in urls:
            try:
                job_data = await self.scrape_job(url)
                results.append(job_data)
                
                # Add delay between requests to avoid rate limiting
                await asyncio.sleep(3)
                
            except Exception as e:
                self.logger.error(f"Error processing {url}: {e}")
                results.append({
                    'url': url,
                    'error': str(e),
                    'scraped_at': datetime.now().isoformat()
                })
        
        await self.close()
        
        return results