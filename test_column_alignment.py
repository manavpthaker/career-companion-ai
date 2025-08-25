#!/usr/bin/env python3
"""Test script to verify Google Sheets column alignment."""

import asyncio
from datetime import datetime

def test_column_mapping():
    """Test that our column mapping matches the expected order."""
    
    # Your updated column order
    expected_columns = [
        "Role",
        "Company", 
        "Status",
        "Priority",
        "Date Posted",
        "Match Score",
        "Deadline",
        "Date Applied",
        "Resume Link",
        "Cover Letter Link",
        "Notes",
        "Next Action",
        "Job URL"
    ]
    
    # Test job data
    job = {
        'title': 'Senior Product Manager - AI Platform',
        'company': 'OpenAI',
        'priority': 'HIGH',
        'match_score': 0.95,
        'source': 'RemoteOK',
        'location': 'San Francisco, CA (Remote)',
        'url': 'https://openai.com/careers/senior-pm-ai'
    }
    
    drive_result = {
        'documents': {
            'resume_url': 'https://docs.google.com/document/d/resume123',
            'cover_letter_url': 'https://docs.google.com/document/d/cover456'
        }
    }
    
    # Simulate job discovery engine row_data
    discovery_row_data = [
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
    
    # Test pending job processor row_data (with LinkedIn data)
    job_data = {
        'title': 'Senior Product Manager - AI Platform',
        'company': 'Anthropic',
        'priority': 'HIGH',
        'match_score': 0.90,
        'posted_time': '2 days ago',
        'workplace_type': 'Remote',
        'applicants': '50+ applicants',
        'url': 'https://linkedin.com/jobs/view/123456'
    }
    
    pending_row_data = [
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
    
    print("🧪 Testing Column Alignment")
    print("=" * 60)
    
    print(f"\n📋 Expected Column Order ({len(expected_columns)} columns):")
    for i, col in enumerate(expected_columns):
        print(f"  {i+1:2d}. {col}")
    
    print(f"\n🔍 Job Discovery Engine Data ({len(discovery_row_data)} columns):")
    for i, (col, data) in enumerate(zip(expected_columns, discovery_row_data)):
        print(f"  {i+1:2d}. {col:15} → {data}")
    
    print(f"\n🔍 Pending Job Processor Data ({len(pending_row_data)} columns):")
    for i, (col, data) in enumerate(zip(expected_columns, pending_row_data)):
        print(f"  {i+1:2d}. {col:15} → {data}")
    
    # Verify alignment
    if len(discovery_row_data) == len(expected_columns):
        print("\n✅ Job Discovery Engine: Column count matches!")
    else:
        print(f"\n❌ Job Discovery Engine: Column mismatch! Expected {len(expected_columns)}, got {len(discovery_row_data)}")
    
    if len(pending_row_data) == len(expected_columns):
        print("✅ Pending Job Processor: Column count matches!")
    else:
        print(f"❌ Pending Job Processor: Column mismatch! Expected {len(expected_columns)}, got {len(pending_row_data)}")
    
    print("\n🎯 Sample Google Sheets Row (Job Discovery):")
    print("   " + " | ".join([str(d)[:20] + "..." if len(str(d)) > 20 else str(d) for d in discovery_row_data]))
    
    print("\n🎯 Sample Google Sheets Row (Pending Jobs):")
    print("   " + " | ".join([str(d)[:20] + "..." if len(str(d)) > 20 else str(d) for d in pending_row_data]))

if __name__ == "__main__":
    test_column_mapping()