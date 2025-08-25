#!/usr/bin/env python3
"""Add new LinkedIn job URLs to the tracker."""

import asyncio
import yaml
from typing import List

from agents.linkedin_scraper import LinkedInScraper
from agents.enhanced_template_engine import EnhancedTemplateEngine
from agents.google_drive_agent import GoogleDriveAgent
from agents.company_intelligence_engine import CompanyIntelligenceEngine
from agents.personal_context_manager import PersonalContextManager

class LinkedInJobAdder:
    """Add specific LinkedIn jobs to the tracker."""
    
    def __init__(self, config_path='config/job_search_config.yaml'):
        """Initialize the job adder."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.scraper = LinkedInScraper(headless=True)
        self.template_engine = EnhancedTemplateEngine()
        self.drive_agent = GoogleDriveAgent(self.config)
        self.intelligence_engine = CompanyIntelligenceEngine()
        self.context_manager = PersonalContextManager()
    
    async def add_jobs(self, urls: List[str]):
        """Add LinkedIn jobs to the tracker."""
        
        print("🚀 Adding New LinkedIn Jobs")
        print("=" * 60)
        print(f"Processing {len(urls)} job URLs...\n")
        
        # Scrape the jobs
        scraped_jobs = await self.scraper.scrape_multiple_jobs(urls)
        
        processed_count = 0
        
        for scraped_data in scraped_jobs:
            # Skip if scraping failed
            if 'error' in scraped_data and not scraped_data.get('title'):
                print(f"⏭️ Skipping failed scrape: {scraped_data['url']}")
                continue
            
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
            
            # Generate application if high/medium priority
            if scraped_data['priority'] in ['HIGH', 'MEDIUM']:
                await self._generate_and_add_application(scraped_data)
                processed_count += 1
            else:
                # Just add to tracker without generating application
                await self._add_to_tracker_only(scraped_data)
                processed_count += 1
            
            await asyncio.sleep(2)  # Rate limiting
        
        print(f"\n✅ Successfully processed {processed_count} jobs!")
        print("Check your Google Sheets tracker for the new opportunities.")
    
    def _calculate_match_score(self, job: dict) -> float:
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
            score += weights['seniority_match'] * 0.6
        
        # Technical match
        desc = job.get('description', '').lower()
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
    
    async def _generate_and_add_application(self, job_data: dict):
        """Generate application and add to tracker."""
        
        print(f"  📝 Generating application materials...")
        
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
                print(f"  ✅ Application created in Google Drive")
                
                # Add to tracker with documents
                await self._add_to_tracker(job_data, app_result)
            else:
                print(f"  ❌ Failed to create application: {result.get('error')}")
                # Add to tracker without documents
                await self._add_to_tracker_only(job_data)
                
        except Exception as e:
            print(f"  ❌ Error generating application: {e}")
            # Add to tracker without documents
            await self._add_to_tracker_only(job_data)
    
    async def _add_to_tracker(self, job_data: dict, drive_result: dict):
        """Add job to tracker with application documents."""
        
        try:
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
                'Apply this week' if job_data.get('priority') == 'HIGH' else 'Review and apply',  # Next Action
                job_data.get('url', '')                                                 # Job URL
            ]
            
            await self.drive_agent._ensure_tracker_sheet()
            self.drive_agent.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.drive_agent.tracker_sheet_id,
                range='Applications!A:M',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()
            
            print(f"  ✅ Added to Google Sheets tracker with documents")
            
        except Exception as e:
            print(f"  ⚠️ Error adding to tracker: {e}")
    
    async def _add_to_tracker_only(self, job_data: dict):
        """Add job to tracker without application documents."""
        
        try:
            row_data = [
                job_data.get('title', ''),                                              # Role
                job_data.get('company', ''),                                            # Company
                'Not Started',                                                          # Status
                job_data.get('priority', 'LOW'),                                       # Priority
                job_data.get('posted_time', ''),                                       # Date Posted
                f"{job_data.get('match_score', 0)*100:.1f}%",                         # Match Score
                '',                                                                     # Deadline
                '',                                                                     # Date Applied
                '',                                                                     # Resume Link (empty)
                '',                                                                     # Cover Letter Link (empty)
                f"LinkedIn | {job_data.get('workplace_type', '')} | {job_data.get('applicants', 'Unknown applicants')}",  # Notes
                'Generate application materials' if job_data.get('priority') in ['HIGH', 'MEDIUM'] else 'Review when time permits',  # Next Action
                job_data.get('url', '')                                                 # Job URL
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

async def main():
    """Main entry point."""
    
    # New LinkedIn job URLs to add
    new_urls = [
        "https://www.linkedin.com/jobs/view/4277852534/?refId=d358e15d-557b-4df1-bbd2-8fc8589ec5a1&trackingId=Kh0gYCVgRIOG00e7FYigNQ%3D%3D",
        "https://www.linkedin.com/jobs/view/4283025676"
    ]
    
    adder = LinkedInJobAdder()
    
    # Ensure Google Drive is set up
    await adder.drive_agent._ensure_root_folder()
    await adder.drive_agent._ensure_tracker_sheet()
    
    # Add the jobs
    await adder.add_jobs(new_urls)

if __name__ == "__main__":
    asyncio.run(main())