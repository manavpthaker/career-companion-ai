# 🔍 Job Discovery System

## Overview

The Job Discovery Engine aggregates job opportunities from multiple sources including LinkedIn, job boards, and company websites. It's designed to save time by centralizing job search across platforms.

## Architecture

### Multi-Source Integration

```python
class JobDiscoveryEngine:
    """Coordinate job discovery across multiple sources."""
    
    def __init__(self):
        self.sources = {
            'linkedin': LinkedInScraperAgent(rate_limit='5/min'),
            'job_boards': JobBoardAgent(['indeed', 'builtin', 'angellist']),
            'company_direct': CompanyCareerAgent(target_companies),
            'news_intelligence': CompanyNewsAgent(news_api_key)
        }
        
    async def discover_opportunities(self, search_criteria):
        """Run discovery across configured sources."""
        tasks = []
        
        for source_name, agent in self.sources.items():
            if agent.should_run(search_criteria):
                task = asyncio.create_task(
                    self.run_with_monitoring(agent, search_criteria)
                )
                tasks.append(task)
        
        # Parallel execution with failure isolation
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.aggregate_and_deduplicate(results)
```

## LinkedIn Integration

### Playwright-Based Scraping

The system uses Playwright for LinkedIn scraping with rate limiting to respect the platform:

```python
class LinkedInScraperAgent:
    """LinkedIn scraping with rate limiting."""
    
    async def scrape_with_rate_limit(self, job_urls):
        """Scrape LinkedIn with delays between requests."""
        
        browser = await self.get_browser()
        results = []
        
        for url in job_urls:
            try:
                # Rate limiting delay
                await asyncio.sleep(random.uniform(3, 7))
                
                page = await browser.new_page()
                await page.goto(url, wait_until='networkidle')
                
                # Extract job details
                job_data = await self.extract_job_details(page)
                results.append(job_data)
                
            except Exception as e:
                self.logger.warning(f"Failed to scrape {url}: {e}")
                continue
            finally:
                await page.close()
        
        return results
```

### Rate Limiting
- **LinkedIn:** 5 requests per minute
- **Delays:** 3-7 seconds between requests
- **Error Handling:** Graceful failure on blocked requests

## Company Intelligence

### News API Integration

Research companies using public news sources:

```python
class CompanyIntelligenceEngine:
    """Gather company information from news sources."""
    
    async def research_company(self, company_name, job_context):
        """Fetch recent news about company."""
        
        # Get recent news
        news_data = await self.fetch_recent_news(company_name)
        
        # Basic analysis
        return CompanyIntelligence(
            recent_news=news_data,
            job_context=job_context
        )
```

## Job Board Integration

### Supported Boards
- Indeed (via web scraping)
- Built In (via web scraping)
- AngelList (when available)
- Direct company career pages

### Implementation
```python
class JobBoardAgent:
    """Aggregate jobs from multiple boards."""
    
    def __init__(self, boards=['indeed', 'builtin']):
        self.boards = boards
    
    async def search_all_boards(self, criteria):
        """Search configured job boards."""
        results = {}
        
        for board in self.boards:
            try:
                board_results = await self.search_board(board, criteria)
                results[board] = board_results
            except Exception as e:
                self.logger.error(f"Failed to search {board}: {e}")
                results[board] = []
        
        return results
```

## Deduplication

### Simple Similarity Matching

Remove duplicate jobs using title and company matching:

```python
class JobDeduplicator:
    """Remove duplicate job postings."""
    
    def deduplicate_jobs(self, job_list):
        """Basic deduplication by title and company."""
        
        seen = set()
        unique_jobs = []
        
        for job in job_list:
            # Create unique key
            key = f"{job.get('company', '').lower()}_{job.get('title', '').lower()}"
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
```

## Usage

### Basic Discovery

```python
# Initialize engine
engine = JobDiscoveryEngine()

# Define search criteria
criteria = {
    'titles': ['Product Manager', 'Senior PM'],
    'locations': ['Remote', 'New York'],
    'keywords': ['AI', 'machine learning']
}

# Run discovery
jobs = await engine.discover_opportunities(criteria)
print(f"Found {len(jobs)} unique opportunities")
```

### Company Research

```python
# Research specific company
intel_engine = CompanyIntelligenceEngine()

company_data = await intel_engine.research_company(
    company_name="OpenAI",
    job_context={'title': 'Product Manager'}
)
```

## Current Limitations

- Web scraping may break when sites update
- Rate limiting reduces speed
- Not all job boards have APIs
- Deduplication is basic and may miss some duplicates
- Requires manual configuration of search criteria

## Future Improvements

- Add more job board integrations
- Improve deduplication algorithm
- Add job quality scoring
- Implement better error recovery
- Create web interface for configuration

---

*This is technical documentation for an open-source project. Actual performance may vary based on configuration and external factors.*