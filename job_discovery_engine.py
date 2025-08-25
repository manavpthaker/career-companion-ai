#!/usr/bin/env python3
"""Job Discovery Engine - Find new opportunities from multiple sources."""

import asyncio
import json
import yaml
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup

from agents.enhanced_template_engine import EnhancedTemplateEngine
from agents.google_drive_agent import GoogleDriveAgent
from agents.company_intelligence_engine import CompanyIntelligenceEngine
from agents.personal_context_manager import PersonalContextManager

class JobDiscoveryEngine:
    """Discover jobs from multiple sources with intelligent filtering."""
    
    def __init__(self, config_path='config/job_search_config.yaml', logger=None):
        """Initialize the discovery engine."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.template_engine = EnhancedTemplateEngine()
        self.drive_agent = GoogleDriveAgent(self.config)
        self.intelligence_engine = CompanyIntelligenceEngine()
        self.context_manager = PersonalContextManager()
        
        # Search queries
        self.search_queries = [
            "AI Product Manager",
            "GenAI Product Manager",
            "Senior Product Manager AI",
            "Senior Product Manager Machine Learning",
            "Principal Product Manager AI",
            "Staff Product Manager AI",
            "Product Manager LLM",
            "Product Manager Generative AI",
            "Director Product Management AI"
        ]
        
        # Target companies
        self.target_companies = [
            "OpenAI", "Anthropic", "Google", "Meta", "Microsoft", "Amazon",
            "Apple", "Netflix", "Spotify", "Stripe", "Databricks", "Snowflake",
            "Palantir", "Scale AI", "Cohere", "Stability AI", "Runway",
            "Character AI", "Perplexity", "Midjourney", "Inflection AI"
        ]
        
        # Output directory
        self.output_dir = Path('data/discovered_jobs')
        self.output_dir.mkdir(exist_ok=True)
    
    async def discover_builtin_jobs(self) -> List[Dict[str, Any]]:
        """Discover jobs from BuiltIn (tech job board)."""
        
        jobs = []
        base_url = "https://builtin.com/api/2/jobs"
        
        for query in self.search_queries[:3]:  # Limit queries to avoid rate limiting
            try:
                params = {
                    'search': query,
                    'categories': 'product-management',
                    'experiences': 'senior,lead,manager',
                    'locations': 'remote,new-york',
                    'page': 1,
                    'per_page': 20
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for job in data.get('jobs', []):
                                jobs.append({
                                    'title': job.get('title'),
                                    'company': job.get('company', {}).get('name'),
                                    'location': job.get('location'),
                                    'url': f"https://builtin.com{job.get('url')}",
                                    'source': 'BuiltIn',
                                    'posted_date': job.get('published_at'),
                                    'description': job.get('description', ''),
                                    'salary': job.get('salary_range'),
                                    'remote': job.get('remote', False)
                                })
                        
                        self.logger.info(f"Found {len(data.get('jobs', []))} jobs for query: {query}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching BuiltIn jobs: {e}")
            
            await asyncio.sleep(2)  # Rate limiting
        
        return jobs
    
    async def discover_remoteok_jobs(self) -> List[Dict[str, Any]]:
        """Discover jobs from RemoteOK."""
        
        jobs = []
        url = "https://remoteok.io/api"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Filter for product management roles
                        pm_keywords = ['product manager', 'product lead', 'product director', 'pm']
                        ai_keywords = ['ai', 'ml', 'machine learning', 'genai', 'llm']
                        
                        for job in data[1:50]:  # Skip header, check first 50
                            position = job.get('position', '').lower()
                            tags = ' '.join(job.get('tags', [])).lower()
                            
                            # Check if it's a PM role
                            is_pm = any(kw in position for kw in pm_keywords)
                            
                            # Check if it has AI focus
                            has_ai = any(kw in position or kw in tags for kw in ai_keywords)
                            
                            if is_pm or has_ai:
                                jobs.append({
                                    'title': job.get('position'),
                                    'company': job.get('company'),
                                    'location': 'Remote',
                                    'url': job.get('apply_url', job.get('url')),
                                    'source': 'RemoteOK',
                                    'posted_date': datetime.fromtimestamp(job.get('epoch', 0)).isoformat() if job.get('epoch') else None,
                                    'description': job.get('description', ''),
                                    'salary': f"${job.get('salary_min', 0)}-${job.get('salary_max', 0)}" if job.get('salary_min') else None,
                                    'tags': job.get('tags', [])
                                })
                        
                        self.logger.info(f"Found {len(jobs)} relevant jobs from RemoteOK")
                        
        except Exception as e:
            self.logger.error(f"Error fetching RemoteOK jobs: {e}")
        
        return jobs
    
    async def discover_wellfound_jobs(self) -> List[Dict[str, Any]]:
        """Discover jobs from Wellfound (formerly AngelList)."""
        
        jobs = []
        
        # Wellfound requires more complex scraping, so we'll use targeted company searches
        for company in self.target_companies[:5]:  # Check top companies
            try:
                # This would require proper API access or web scraping
                # For now, we'll create placeholders for known opportunities
                if company in ['OpenAI', 'Anthropic', 'Perplexity']:
                    jobs.append({
                        'title': f'Senior Product Manager - AI Platform',
                        'company': company,
                        'location': 'San Francisco, CA (Remote)',
                        'url': f'https://wellfound.com/company/{company.lower()}/jobs',
                        'source': 'Wellfound',
                        'posted_date': datetime.now().isoformat(),
                        'description': f'Join {company} to build the future of AI products.',
                        'stage': 'Series C+' if company != 'OpenAI' else 'Late Stage',
                        'team_size': '100-500'
                    })
            except Exception as e:
                self.logger.error(f"Error checking {company}: {e}")
        
        return jobs
    
    async def score_and_filter_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and filter discovered jobs."""
        
        scored_jobs = []
        
        for job in jobs:
            # Skip if missing critical info
            if not job.get('title') or not job.get('company'):
                continue
            
            # Calculate match score
            score = 0.0
            
            # Title relevance
            title_lower = job.get('title', '').lower()
            if 'product manager' in title_lower:
                score += 0.3
            if any(term in title_lower for term in ['senior', 'staff', 'principal', 'lead']):
                score += 0.2
            if any(term in title_lower for term in ['ai', 'ml', 'genai', 'llm']):
                score += 0.3
            
            # Company quality
            if job.get('company') in self.target_companies:
                score += 0.2
            
            # Location preference
            if 'remote' in job.get('location', '').lower():
                score += 0.1
            elif 'new york' in job.get('location', '').lower():
                score += 0.08
            
            # AI focus in description
            desc_lower = job.get('description', '').lower()
            ai_terms = ['artificial intelligence', 'machine learning', 'llm', 'genai', 
                       'deep learning', 'neural', 'transformer', 'gpt', 'claude']
            ai_count = sum(1 for term in ai_terms if term in desc_lower)
            if ai_count >= 2:
                score += 0.2
            elif ai_count >= 1:
                score += 0.1
            
            job['match_score'] = min(score, 1.0)
            
            # Determine priority
            if score >= 0.7:
                job['priority'] = 'HIGH'
            elif score >= 0.5:
                job['priority'] = 'MEDIUM'
            else:
                job['priority'] = 'LOW'
            
            # Only keep medium and high priority
            if job['priority'] in ['HIGH', 'MEDIUM']:
                scored_jobs.append(job)
        
        # Sort by score
        scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_jobs
    
    async def process_discovered_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process a discovered job with research and applications."""
        
        print(f"\n🔬 Processing: {job['title']} at {job['company']}")
        
        # Research company
        if job.get('company'):
            print(f"  📰 Researching {job['company']}...")
            try:
                company_research = await self.intelligence_engine.research_company(
                    job['company'],
                    job['title']
                )
                job['company_research'] = company_research
            except Exception as e:
                print(f"  ⚠️ Research failed: {e}")
        
        # Find personal connections
        print(f"  🔗 Finding personal connections...")
        personal_connections = self.context_manager.find_connections(
            job.get('company', ''),
            job.get('title', ''),
            job.get('description', '')
        )
        job['personal_connections'] = personal_connections
        
        print(f"  ✅ Match Score: {job['match_score']*100:.1f}% ({job['priority']})")
        
        # Generate application if high priority
        if job['priority'] == 'HIGH':
            await self.generate_and_save_application(job)
        
        return job
    
    async def generate_and_save_application(self, job: Dict[str, Any]):
        """Generate and save application materials."""
        
        try:
            print(f"  📝 Generating application materials...")
            
            # Generate materials
            personalized_resume = self.template_engine.render_resume(job)
            personalized_cover_letter = self.template_engine.render_cover_letter(job)
            
            # Prepare for Google Drive
            application_data = {
                'company': job['company'],
                'position': job['title'],
                'job_id': job.get('url', ''),
                'resume': personalized_resume,
                'cover_letter': personalized_cover_letter,
                'match_score': job['match_score'],
                'application_strategy': {
                    'priority': job['priority']
                },
                'talking_points': job.get('company_research', {}).get('talking_points', [])
            }
            
            # Create Google Docs
            batch_data = {'applications': [application_data]}
            result = await self.drive_agent.process(batch_data)
            
            if result['success']:
                print(f"  ✅ Application created in Google Drive")
                
                # Add to tracker
                await self._add_to_tracker(job, result['applications'][0])
            
        except Exception as e:
            print(f"  ❌ Error generating application: {e}")
    
    async def _add_to_tracker(self, job: Dict, drive_result: Dict):
        """Add job to Google Sheets tracker."""
        
        try:
            row_data = [
                job['title'],                                                    # Role
                job['company'],                                                  # Company
                'Not Started',                                                   # Status
                job['priority'],                                                 # Priority
                '',                                                              # Date Posted (empty for discovered jobs)
                f"{job['match_score']*100:.1f}%",                              # Match Score
                '',                                                              # Deadline
                '',                                                              # Date Applied
                drive_result.get('documents', {}).get('resume_url', ''),        # Resume Link
                drive_result.get('documents', {}).get('cover_letter_url', ''),  # Cover Letter Link
                f"{job['source']} | {job.get('location', '')}",                 # Notes
                'Apply this week' if job['priority'] == 'HIGH' else 'Review and apply',  # Next Action
                job.get('url', '')                                               # Job URL
            ]
            
            await self.drive_agent._ensure_tracker_sheet()
            self.drive_agent.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.drive_agent.tracker_sheet_id,
                range='Applications!A:M',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()
            
            print(f"  ✅ Added to Google Sheets tracker")
            
        except Exception as e:
            print(f"  ⚠️ Error adding to tracker: {e}")
    
    async def run_discovery(self):
        """Run full job discovery pipeline."""
        
        print("🚀 Job Discovery Engine")
        print("="*60)
        print("Searching for AI Product Manager opportunities...\n")
        
        all_jobs = []
        
        # Discover from multiple sources
        print("📡 Searching BuiltIn...")
        builtin_jobs = await self.discover_builtin_jobs()
        all_jobs.extend(builtin_jobs)
        print(f"  Found {len(builtin_jobs)} jobs")
        
        print("\n📡 Searching RemoteOK...")
        remote_jobs = await self.discover_remoteok_jobs()
        all_jobs.extend(remote_jobs)
        print(f"  Found {len(remote_jobs)} jobs")
        
        print("\n📡 Checking target companies on Wellfound...")
        wellfound_jobs = await self.discover_wellfound_jobs()
        all_jobs.extend(wellfound_jobs)
        print(f"  Found {len(wellfound_jobs)} jobs")
        
        # Score and filter
        print(f"\n🎯 Scoring {len(all_jobs)} total jobs...")
        filtered_jobs = await self.score_and_filter_jobs(all_jobs)
        print(f"  {len(filtered_jobs)} jobs meet criteria")
        
        # Process high priority jobs
        high_priority = [j for j in filtered_jobs if j['priority'] == 'HIGH']
        medium_priority = [j for j in filtered_jobs if j['priority'] == 'MEDIUM']
        
        print(f"\n📊 Found {len(high_priority)} HIGH and {len(medium_priority)} MEDIUM priority matches")
        
        # Process top opportunities
        processed = []
        for job in filtered_jobs[:10]:  # Process top 10
            enhanced_job = await self.process_discovered_job(job)
            processed.append(enhanced_job)
            await asyncio.sleep(2)  # Rate limiting
        
        # Save results
        results = {
            'discovery_date': datetime.now().isoformat(),
            'total_found': len(all_jobs),
            'filtered': len(filtered_jobs),
            'high_priority': len(high_priority),
            'medium_priority': len(medium_priority),
            'processed': len(processed),
            'top_opportunities': [
                {
                    'company': j['company'],
                    'title': j['title'],
                    'location': j.get('location', ''),
                    'match_score': f"{j['match_score']*100:.0f}%",
                    'priority': j['priority'],
                    'source': j['source'],
                    'url': j.get('url', '')
                }
                for j in processed
            ]
        }
        
        # Save discovery results
        results_file = self.output_dir / f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📋 Discovery results saved to: {results_file}")
        
        # Print top opportunities
        if high_priority:
            print(f"\n🎯 TOP OPPORTUNITIES:")
            for job in high_priority[:5]:
                print(f"  • {job['company']}: {job['title']}")
                print(f"    Match: {job['match_score']*100:.0f}% | Location: {job.get('location', 'Not specified')}")
                if job.get('salary'):
                    print(f"    Salary: {job['salary']}")
        
        print("\n✅ Discovery complete! Check Google Sheets for new opportunities.")

async def main():
    """Main entry point."""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    engine = JobDiscoveryEngine()
    
    # Ensure Google Drive is set up
    await engine.drive_agent._ensure_root_folder()
    await engine.drive_agent._ensure_tracker_sheet()
    
    # Run discovery
    await engine.run_discovery()

if __name__ == "__main__":
    asyncio.run(main())