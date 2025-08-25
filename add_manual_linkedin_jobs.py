#!/usr/bin/env python3
"""Manually add LinkedIn job URLs to tracker when scraping fails."""

import asyncio
import yaml
from datetime import datetime

from agents.google_drive_agent import GoogleDriveAgent

async def add_manual_jobs():
    """Add jobs manually to the tracker."""
    
    print("📝 Adding LinkedIn Jobs Manually")
    print("=" * 50)
    
    # Load config and initialize Google Drive agent
    with open('config/job_search_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    drive_agent = GoogleDriveAgent(config)
    await drive_agent._ensure_root_folder()
    await drive_agent._ensure_tracker_sheet()
    
    # Clean up URLs and extract job IDs
    jobs_to_add = [
        {
            'url': 'https://www.linkedin.com/jobs/view/4277852534/',
            'job_id': '4277852534',
            'title': 'LinkedIn Job 4277852534',  # Placeholder
            'company': 'TBD',
            'priority': 'MEDIUM',
            'notes': 'LinkedIn | Manual entry - scraping blocked'
        },
        {
            'url': 'https://www.linkedin.com/jobs/view/4283025676/',
            'job_id': '4283025676', 
            'title': 'LinkedIn Job 4283025676',  # Placeholder
            'company': 'TBD',
            'priority': 'MEDIUM',
            'notes': 'LinkedIn | Manual entry - scraping blocked'
        }
    ]
    
    for job in jobs_to_add:
        print(f"\n➕ Adding: {job['title']}")
        
        # Use the correct column order: Role | Company | Status | Priority | Date Posted | Match Score | Deadline | Date Applied | Resume Link | Cover Letter Link | Notes | Next Action | Job URL
        row_data = [
            job['title'],                           # Role
            job['company'],                         # Company  
            'Not Started',                          # Status
            job['priority'],                        # Priority
            '',                                     # Date Posted
            'TBD',                                  # Match Score (to be filled after manual review)
            '',                                     # Deadline
            '',                                     # Date Applied
            '',                                     # Resume Link (empty - to be generated)
            '',                                     # Cover Letter Link (empty - to be generated) 
            job['notes'],                           # Notes
            'Review job details and generate application', # Next Action
            job['url']                              # Job URL
        ]
        
        try:
            drive_agent.sheets_service.spreadsheets().values().append(
                spreadsheetId=drive_agent.tracker_sheet_id,
                range='Applications!A:M',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()
            
            print(f"  ✅ Added {job['job_id']} to tracker")
            
        except Exception as e:
            print(f"  ❌ Error adding {job['job_id']}: {e}")
    
    print(f"\n🎯 Next Steps:")
    print("1. Open your Google Sheets tracker")
    print("2. Manually visit the LinkedIn URLs to get job details")
    print("3. Update the Role, Company, and Match Score columns") 
    print("4. Generate application materials when ready")
    print("\n✅ Manual entries complete!")

if __name__ == "__main__":
    asyncio.run(add_manual_jobs())