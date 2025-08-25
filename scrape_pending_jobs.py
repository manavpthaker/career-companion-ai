#!/usr/bin/env python3
"""Scrape and process pending LinkedIn job URLs using Playwright."""

import asyncio
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from agents.linkedin_scraper import LinkedInScraper
from agents.enhanced_template_engine import EnhancedTemplateEngine
from agents.google_drive_agent import GoogleDriveAgent
from agents.company_intelligence_engine import CompanyIntelligenceEngine
from agents.personal_context_manager import PersonalContextManager

class PendingJobProcessor:
    """Process pending LinkedIn jobs with scraping and intelligence."""
    
    def __init__(self, config_path='config/job_search_config.yaml'):
        """Initialize the processor."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.scraper = LinkedInScraper(headless=True)
        self.template_engine = EnhancedTemplateEngine()
        self.drive_agent = GoogleDriveAgent(self.config)
        self.intelligence_engine = CompanyIntelligenceEngine()
        self.context_manager = PersonalContextManager()
        
        # Output directory
        self.output_dir = Path('data/scraped_jobs')
        self.output_dir.mkdir(exist_ok=True)
    
    def get_pending_urls(self) -> List[str]:
        """Get list of pending LinkedIn URLs to scrape."""
        
        return [
            "https://www.linkedin.com/jobs/view/4272441976/",
            "https://www.linkedin.com/jobs/view/4245709356/",
            "https://www.linkedin.com/jobs/view/4267293359/",
            "https://www.linkedin.com/jobs/view/4240700875/",
            "https://www.linkedin.com/jobs/view/4279025530/",
            "https://www.linkedin.com/jobs/view/4258741830/",
            "https://www.linkedin.com/jobs/view/4263105615/",
            "https://www.linkedin.com/jobs/view/4285593835/"
        ]
    
    async def process_scraped_job(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a scraped job with intelligence and personalization."""
        
        # Skip if scraping failed
        if 'error' in scraped_data and not scraped_data.get('title'):
            print(f"⏭️ Skipping failed scrape: {scraped_data['url']}")
            return scraped_data
        
        print(f"\n🔬 Processing: {scraped_data.get('title', 'Unknown')} at {scraped_data.get('company', 'Unknown')}")
        
        # Research company if we have a company name
        if scraped_data.get('company'):
            print(f"  📰 Researching {scraped_data['company']}...")
            try:
                company_research = await self.intelligence_engine.research_company(
                    scraped_data['company'],
                    scraped_data.get('title', '')
                )
                scraped_data['company_research'] = company_research
            except Exception as e:
                print(f"  ⚠️ Research failed: {e}")
                scraped_data['company_research'] = {}
        
        # Find personal connections
        print(f"  🔗 Finding personal connections...")
        personal_connections = self.context_manager.find_connections(
            scraped_data.get('company', ''),
            scraped_data.get('title', ''),
            scraped_data.get('description', '')
        )
        scraped_data['personal_connections'] = personal_connections
        
        # Calculate match score
        scraped_data['match_score'] = self._calculate_match_score(scraped_data)
        
        # Determine priority
        if scraped_data['match_score'] >= 0.70:
            scraped_data['priority'] = 'HIGH'
        elif scraped_data['match_score'] >= 0.50:
            scraped_data['priority'] = 'MEDIUM'
        else:
            scraped_data['priority'] = 'LOW'
        
        print(f"  ✅ Match Score: {scraped_data['match_score']*100:.1f}% ({scraped_data['priority']})")
        
        return scraped_data
    
    def _calculate_match_score(self, job: Dict[str, Any]) -> float:
        """Calculate match score for a scraped job."""
        
        score = 0.0
        weights = {
            'title_match': 0.25,
            'seniority_match': 0.20,
            'technical_match': 0.25,
            'location_match': 0.15,
            'personal_connection': 0.15
        }
        
        # Title match
        title = job.get('title', '').lower()
        if 'product manager' in title:
            score += weights['title_match'] * 0.7
        if any(term in title for term in ['senior', 'staff', 'principal', 'lead']):
            score += weights['title_match'] * 0.3
        
        # Seniority match
        seniority = job.get('seniority_level', '').lower()
        experience = job.get('required_experience', '').lower()
        
        if 'senior' in seniority or 'senior' in title:
            score += weights['seniority_match'] * 0.8
        elif 'mid' in seniority or '5' in experience or '7' in experience:
            score += weights['seniority_match'] * 1.0
        elif 'director' in title or 'principal' in title:
            score += weights['seniority_match'] * 0.6  # Slight stretch
        
        # Technical match
        desc = job.get('description', '').lower()
        tech_requirements = job.get('technical_requirements', [])
        
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'llm', 
                      'genai', 'generative', 'nlp', 'deep learning']
        
        ai_count = sum([STREET_ADDRESS] in desc)
        if ai_count >= 2:
            score += weights['technical_match']
        elif ai_count >= 1:
            score += weights['technical_match'] * 0.7
        
        # Location match
        location = job.get('location', '').lower()
        workplace = job.get('workplace_type', '').lower()
        
        if 'remote' in location or 'remote' in workplace:
            score += weights['location_match']
        elif 'new york' in location or 'nyc' in location or 'ny,' in location:
            score += weights['location_match'] * 0.8
        elif 'hybrid' in workplace:
            score += weights['location_match'] * 0.6
        
        # Personal connections
        connections = job.get('personal_connections', {})
        if connections.get('relevant_experiences'):
            score += weights['personal_connection']
        
        return min(score, 1.0)
    
    async def generate_application(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized application materials."""
        
        print(f"\n📝 Generating application for {job_data.get('company', 'Unknown')}")
        
        try:
            # Generate personalized materials
            personalized_resume = self.template_engine.render_resume(job_data)
            personalized_cover_letter = self.template_engine.render_cover_letter(job_data)
            
            # Prepare for Google Drive
            application_data = {
                'company': job_data.get('company', 'Unknown'),
                'position': job_data.get('title', 'Unknown Position'),
                'job_id': job_data.get('url', ''),
                'resume': personalized_resume,
                'cover_letter': personalized_cover_letter,
                'match_score': job_data.get('match_score', 0),
                'application_strategy': {
                    'priority': job_data.get('priority', 'LOW')
                },
                'talking_points': job_data.get('company_research', {}).get('talking_points', [])
            }
            
            # Create Google Docs
            batch_data = {'applications': [application_data]}
            result = await self.drive_agent.process(batch_data)
            
            if result['success'] and result['exported_count'] > 0:
                app_result = result['applications'][0]
                print(f"✅ Application created!")
                print(f"   📁 Folder: {app_result['folder_url']}")
                
                # Add to tracker
                await self._add_to_tracker(job_data, app_result)
                
                return {
                    'success': True,
                    'job_info': job_data,
                    'google_drive': app_result
                }
            else:
                print(f"❌ Failed to create application: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
                
        except Exception as e:
            print(f"❌ Error generating application: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _add_to_tracker(self, job_data: Dict, drive_result: Dict):
        """Add job to Google Sheets tracker."""
        
        try:
            # Prepare row data
            row_data = [
                job_data.get('title', ''),                                              # Role
                job_data.get('company', ''),                                            # Company
                'Not Started',                                                          # Status
                job_data.get('priority', 'LOW'),                                       # Priority
                job_data.get('posted_time', ''),                                       # Date Posted
                f"{job_data.get('match_score', 0)*100:.1f}%",                         # Match Score
                '',                                                                     # Deadline
                '',                                                                     # Date Applied
                drive_result.get('documents', {}).get('resume_url', ''),               # Resume Link
                drive_result.get('documents', {}).get('cover_letter_url', ''),         # Cover Letter Link
                f"LinkedIn | {job_data.get('workplace_type', '')} | {job_data.get('applicants', 'Unknown applicants')}",  # Notes
                'Review and apply' if job_data.get('priority') == 'HIGH' else 'Review when time permits',  # Next Action
                job_data.get('url', '')                                                 # Job URL
            ]
            
            # Add to sheet
            await self.drive_agent._ensure_tracker_sheet()
            self.drive_agent.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.drive_agent.tracker_sheet_id,
                range='Applications!A:M',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()
            
            print(f"✅ Added to Google Sheets tracker")
            
        except Exception as e:
            print(f"⚠️ Error adding to tracker: {e}")
    
    async def process_all_pending(self):
        """Process all pending LinkedIn jobs."""
        
        print("🚀 Processing Pending LinkedIn Jobs")
        print("="*60)
        
        # Get pending URLs
        urls = self.get_pending_urls()
        print(f"Found {len(urls)} pending job URLs to scrape\n")
        
        # Scrape all jobs
        print("📡 Starting web scraping with Playwright...")
        print("This may take a few minutes...\n")
        
        scraped_jobs = await self.scraper.scrape_multiple_jobs(urls)
        
        # Save scraped data
        scraped_file = self.output_dir / f"scraped_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(scraped_file, 'w') as f:
            json.dump(scraped_jobs, f, indent=2)
        print(f"\n💾 Scraped data saved to: {scraped_file}")
        
        # Process each scraped job
        processed_jobs = []
        high_priority = []
        medium_priority = []
        
        for scraped_data in scraped_jobs:
            # Process with intelligence
            enhanced_job = await self.process_scraped_job(scraped_data)
            
            # Generate application if it's a good match
            if enhanced_job.get('priority') in ['HIGH', 'MEDIUM'] and enhanced_job.get('title'):
                app_result = await self.generate_application(enhanced_job)
                
                if app_result['success']:
                    processed_jobs.append(enhanced_job)
                    
                    if enhanced_job['priority'] == 'HIGH':
                        high_priority.append(enhanced_job)
                    elif enhanced_job['priority'] == 'MEDIUM':
                        medium_priority.append(enhanced_job)
            
            # Rate limiting
            await asyncio.sleep(2)
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total URLs processed: {len(urls)}")
        print(f"Successfully scraped: {sum(1 for j in scraped_jobs if 'title' in j)}")
        print(f"Failed to scrape: {sum(1 for j in scraped_jobs if 'error' in j and 'title' not in j)}")
        print(f"High priority matches: {len(high_priority)}")
        print(f"Medium priority matches: {len(medium_priority)}")
        
        if high_priority:
            print(f"\n🎯 HIGH PRIORITY OPPORTUNITIES:")
            for job in high_priority:
                print(f"  • {job['company']}: {job['title']} ({job['match_score']*100:.0f}% match)")
                if job.get('salary'):
                    print(f"    Salary: {job['salary']}")
                if job.get('workplace_type'):
                    print(f"    Type: {job['workplace_type']}")
        
        if medium_priority:
            print(f"\n✅ MEDIUM PRIORITY OPPORTUNITIES:")
            for job in medium_priority[:3]:  # Show top 3
                print(f"  • {job['company']}: {job['title']} ({job['match_score']*100:.0f}% match)")
        
        # Save summary report
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_urls': len(urls),
            'successful_scrapes': sum(1 for j in scraped_jobs if 'title' in j),
            'failed_scrapes': sum(1 for j in scraped_jobs if 'error' in j and 'title' not in j),
            'high_priority': len(high_priority),
            'medium_priority': len(medium_priority),
            'jobs': [
                {
                    'company': j.get('company', 'Unknown'),
                    'title': j.get('title', 'Unknown'),
                    'match_score': f"{j.get('match_score', 0)*100:.1f}%",
                    'priority': j.get('priority', 'LOW'),
                    'location': j.get('location', ''),
                    'workplace_type': j.get('workplace_type', ''),
                    'salary': j.get('salary', ''),
                    'url': j.get('url', '')
                }
                for j in processed_jobs
            ]
        }
        
        summary_file = self.output_dir / 'scraping_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📋 Summary report: {summary_file}")
        print("✅ All pending jobs processed!")

async def main():
    """Main entry point."""
    processor = PendingJobProcessor()
    
    # Ensure Google Drive is set up
    await processor.drive_agent._ensure_root_folder()
    await processor.drive_agent._ensure_tracker_sheet()
    
    # Process all pending jobs
    await processor.process_all_pending()

if __name__ == "__main__":
    asyncio.run(main())