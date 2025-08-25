#!/usr/bin/env python3
"""
Anonymization script to remove personal information from job search automation files.
Creates sanitized versions for public sharing.
"""

import re
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, List

class Anonymizer:
    """Anonymize personal information in job search files."""
    
    def __init__(self, source_dir: str, target_dir: str):
        """Initialize the anonymizer."""
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Personal information patterns to replace
        self.patterns = {
            # Personal details
            r'\b\d{3}-\d{3}-\d{4}\b': '[PHONE_NUMBER]',
            r'\b\d{3}\.\d{3}\.\d{4}\b': '[PHONE_NUMBER]',
            r'\(\d{3}\)\s*\d{3}-\d{4}': '[PHONE_NUMBER]',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}': '[EMAIL]',
            r'\d{1,5}\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Plaza|Pl)\b': '[STREET_ADDRESS]',
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}\b': '[CITY_STATE_ZIP]',
            
            # LinkedIn profiles
            r'linkedin\.com/in/[\w-]+': 'linkedin.com/in/[USERNAME]',
            r'github\.com/[\w-]+': 'github.com/[USERNAME]',
            
            # API Keys and tokens
            r'sk-[a-zA-Z0-9]{48}': '[OPENAI_API_KEY]',
            r'claude-[a-zA-Z0-9]{40}': '[ANTHROPIC_API_KEY]',
            r'[a-fA-F0-9]{32}': '[API_TOKEN]',
            
            # Google credentials
            r'"client_id":\s*"[^"]+\.apps\.googleusercontent\.com"': '"client_id": "[GOOGLE_CLIENT_ID]"',
            r'"client_secret":\s*"[^"]+"': '"client_secret": "[GOOGLE_CLIENT_SECRET]"',
        }
        
        # Specific name replacements (customize these)
        self.name_replacements = {
            '[YOUR_NAME]': '[YOUR_NAME]',
            '[FIRST_NAME]': '[FIRST_NAME]',
            '[LAST_NAME]': '[LAST_NAME]',
            '[USERNAME]': '[USERNAME]',
            '[CITY]': '[CITY]',
            '[STATE]': '[STATE]',
            '[STATE_ABBR]': '[STATE_ABBR]',
            '[CURRENT_COMPANY]': '[CURRENT_COMPANY]',
            '[PREVIOUS_COMPANY]': '[PREVIOUS_COMPANY]',
        }
    
    def anonymize_text(self, text: str) -> str:
        """Anonymize text content."""
        # Replace specific names first
        for name, replacement in self.name_replacements.items():
            text = text.replace(name, replacement)
        
        # Apply regex patterns
        for pattern, replacement in self.patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def anonymize_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Anonymize YAML configuration file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Anonymize specific fields in job search config
        if 'core_requirements' in data:
            # Anonymize location preferences
            if 'location' in data['core_requirements']:
                loc = data['core_requirements']['location']
                if 'home_base' in loc:
                    loc['home_base'] = '[YOUR_CITY], [YOUR_STATE]'
                if 'preferred' in loc:
                    loc['preferred'] = [
                        '[PRIMARY_CITY]',
                        'Remote',
                        'Hybrid - [YOUR_AREA]'
                    ]
            
            # Anonymize compensation (use ranges)
            if 'compensation' in data['core_requirements']:
                comp = data['core_requirements']['compensation']
                comp['minimum_base'] = 100000
                comp['target_base'] = 150000
                comp['preferred_range_min'] = 120000
                comp['preferred_range_max'] = 180000
        
        # Anonymize company-specific URLs
        if 'job_boards' in data:
            if 'company_specific' in data['job_boards']:
                data['job_boards']['company_specific'] = [
                    "https://careers.example-company1.com",
                    "https://careers.example-company2.com",
                    "https://careers.example-company3.com",
                    "# Add your target company career pages here"
                ]
        
        return data
    
    def create_example_resume(self) -> str:
        """Create an example resume template."""
        return """[YOUR_NAME]
[YOUR_TITLE] | [YOUR_SPECIALIZATION]
[YOUR_ADDRESS] | [YOUR_PHONE] | [YOUR_EMAIL] | linkedin.com/in/[YOUR_LINKEDIN]

EXECUTIVE SUMMARY
[2-3 sentences describing your experience and value proposition. Focus on:
- Years of experience and domain expertise
- Key achievements and metrics
- Unique skills or perspectives you bring]

TECHNICAL EXPERTISE
[PRIMARY_SKILLS]: [List 4-5 primary technical skills]
[FRAMEWORKS]: [List relevant frameworks and tools]
[LANGUAGES]: [Programming languages if applicable]
[TOOLS]: [Other relevant tools and platforms]

EXPERIENCE

[CURRENT_ROLE] | [CURRENT_COMPANY] | [START_DATE]-Present
• [Achievement [STREET_ADDRESS] - use action verbs]
• [Achievement 2 focusing on business value delivered]
• [Achievement 3 highlighting technical or leadership skills]
• [Achievement 4 demonstrating innovation or problem-solving]

[PREVIOUS_ROLE] | [PREVIOUS_COMPANY] | [START_DATE]-[END_DATE]
• [Key achievement with metrics]
• [Project or initiative you led]
• [Technical accomplishment]
• [Team or process improvement]

[EARLIER_ROLE] | [COMPANY] | [START_DATE]-[END_DATE]
• [Relevant accomplishment]
• [Skill demonstration]
• [Value delivered]

EDUCATION

[DEGREE] | [UNIVERSITY] | [GRADUATION_YEAR]
[Relevant coursework, honors, or activities if recent graduate]

CERTIFICATIONS & TRAINING
• [Relevant certification 1]
• [Relevant certification 2]
• [Online courses or bootcamps if relevant]

PROJECTS & PUBLICATIONS
• [Open source project with GitHub link]
• [Blog post or article if relevant]
• [Speaking engagement or presentation]

ADDITIONAL INFORMATION
• [Languages spoken]
• [Volunteer work]
• [Relevant hobbies or interests]"""
    
    def create_example_cover_letter(self) -> str:
        """Create an example cover letter template."""
        return """[HIRING_MANAGER_NAME]
[TITLE]
[COMPANY_NAME]
[COMPANY_ADDRESS]

Dear [HIRING_MANAGER_NAME / Hiring Team],

**[HOOK: Company-specific challenge or opportunity]**

[EXAMPLE: "As [COMPANY] scales its [SPECIFIC_INITIATIVE]..." OR "Your recent announcement about [NEWS/PRODUCT] aligns perfectly with..."]

I bring [X years] of experience in [RELEVANT_DOMAIN], with a proven track record of [KEY_ACHIEVEMENT]. At [CURRENT/RECENT_COMPANY], I [SPECIFIC_ACCOMPLISHMENT_WITH_METRICS]. This experience directly aligns with your need for someone who can [REQUIREMENT_FROM_JOB_POSTING].

**Why I'm Uniquely Qualified**

• **[Their Requirement 1]**: In my role at [COMPANY], I [SPECIFIC_ACHIEVEMENT]. This demonstrates exactly the [CAPABILITY] you're seeking.

• **[Their Requirement 2]**: My experience with [RELEVANT_SKILL/TECHNOLOGY] enabled me to [SPECIFIC_RESULT], which would translate directly to [VALUE_FOR_THEIR_COMPANY].

• **[Their Requirement 3]**: I've successfully [RELEVANT_EXPERIENCE], giving me the [SKILL/PERSPECTIVE] needed to [CONTRIBUTE_TO_THEIR_GOALS].

**The Value I'll Deliver**

In my first 90 days, I would:
• Assess your current [RELEVANT_AREA] and identify immediate opportunities for [IMPROVEMENT_TYPE]
• Implement [SPECIFIC_SOLUTION/PROCESS] based on my experience with [RELEVANT_BACKGROUND]
• Build relationships with [RELEVANT_STAKEHOLDERS] to ensure [DESIRED_OUTCOME]
• Begin developing [LONG_TERM_INITIATIVE] to support [COMPANY_GOAL]

**Why [COMPANY], Why Now**

[COMPANY]'s mission to [COMPANY_MISSION/VALUE] resonates deeply with my belief in [RELATED_VALUE]. Your approach to [SPECIFIC_COMPANY_ATTRIBUTE] aligns with my experience in [RELEVANT_AREA]. I'm excited about the opportunity to contribute to [SPECIFIC_COMPANY_GOAL_OR_PROJECT].

I would welcome the opportunity to discuss how my experience with [KEY_SKILL/ACHIEVEMENT] can contribute to [COMPANY]'s continued success. I'm available for a conversation at your convenience and can be reached at [PHONE] or [EMAIL].

Thank you for considering my application. I look forward to the possibility of contributing to [COMPANY]'s [SPECIFIC_GOAL/MISSION].

Sincerely,
[YOUR_NAME]

---
Attachments: Resume, Portfolio Link: [YOUR_PORTFOLIO_URL]"""
    
    def create_example_config(self) -> Dict[str, Any]:
        """Create an example configuration file."""
        return {
            'core_requirements': {
                'job_titles': {
                    'primary': [
                        "[YOUR_TARGET_TITLE_1]",
                        "[YOUR_TARGET_TITLE_2]",
                        "[YOUR_TARGET_TITLE_3]"
                    ],
                    'secondary': [
                        "[FALLBACK_TITLE_1]",
                        "[FALLBACK_TITLE_2]"
                    ]
                },
                'location': {
                    'preferred': [
                        "[PRIMARY_CITY]",
                        "Remote",
                        "Hybrid"
                    ],
                    'acceptable': [
                        "[SECONDARY_CITY]",
                        "Remote USA"
                    ],
                    'max_commute_minutes': 60,
                    'home_base': "[YOUR_CITY], [YOUR_STATE]"
                },
                'compensation': {
                    'minimum_base': 80000,
                    'target_base': 120000,
                    'preferred_range_min': 100000,
                    'preferred_range_max': 150000
                }
            },
            'company_criteria': {
                'stage': {
                    'required': [
                        "Public Company",
                        "Series C+",
                        "Profitable"
                    ],
                    'avoid': [
                        "Seed",
                        "Pre-revenue"
                    ]
                },
                'industry_preference': {
                    'tier1': [
                        "[YOUR_TOP_INDUSTRY_1]",
                        "[YOUR_TOP_INDUSTRY_2]"
                    ],
                    'tier2': [
                        "[ACCEPTABLE_INDUSTRY_1]",
                        "[ACCEPTABLE_INDUSTRY_2]"
                    ],
                    'avoid': [
                        "[INDUSTRY_TO_AVOID]"
                    ]
                },
                'size': {
                    'minimum_employees': 100,
                    'preferred_employees': 500
                }
            },
            'keywords': {
                'required': [
                    "[MUST_HAVE_SKILL_1]",
                    "[MUST_HAVE_SKILL_2]"
                ],
                'preferred': [
                    "[NICE_TO_HAVE_1]",
                    "[NICE_TO_HAVE_2]"
                ]
            },
            'application_settings': {
                'auto_submit': False,
                'max_applications_per_day': 10,
                'follow_up_days': 7
            },
            'rate_limits': {
                'requests_per_minute': 5,
                'pause_between_requests_seconds': 12
            }
        }
    
    def anonymize_project(self):
        """Anonymize the entire project."""
        print("🔐 Starting anonymization process...")
        
        # Copy source to target
        if self.source_dir != self.target_dir:
            print(f"Copying from {self.source_dir} to {self.target_dir}")
            shutil.copytree(self.source_dir, self.target_dir, dirs_exist_ok=True)
        
        # Create example files
        print("Creating example templates...")
        
        # Example resume
        resume_path = self.target_dir / 'templates' / 'resume.example.txt'
        resume_path.parent.mkdir(parents=True, exist_ok=True)
        with open(resume_path, 'w') as f:
            f.write(self.create_example_resume())
        
        # Example cover letter
        cover_path = self.target_dir / 'templates' / 'cover_letter.example.txt'
        with open(cover_path, 'w') as f:
            f.write(self.create_example_cover_letter())
        
        # Example config
        config_path = self.target_dir / 'config' / 'config.example.yaml'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(self.create_example_config(), f, default_flow_style=False)
        
        # Create .env.example
        env_path = self.target_dir / '.env.example'
        with open(env_path, 'w') as f:
            f.write("""# API Keys (optional for enhanced features)
ANTHROPIC_API_KEY=[YOUR_ANTHROPIC_KEY]
OPENAI_API_KEY=[YOUR_OPENAI_KEY]

# Google Cloud (for Drive integration)
GOOGLE_CLIENT_ID=[YOUR_CLIENT_ID]
GOOGLE_CLIENT_SECRET=[YOUR_CLIENT_SECRET]

# Optional Services
SCRAPERAPI_KEY=[YOUR_SCRAPER_KEY]
PROXYMESH_PASSWORD=[YOUR_PROXY_PASSWORD]
""")
        
        # Remove sensitive files
        sensitive_files = [
            'config/google_credentials.json',
            'config/google_token.pickle',
            'config/.env',
            'data/applications.db',
            'templates/resume.txt',
            'templates/cover_letter.txt',
            'config/job_search_config.yaml'
        ]
        
        for file in sensitive_files:
            file_path = self.target_dir / file
            if file_path.exists():
                print(f"Removing sensitive file: {file}")
                file_path.unlink()
        
        # Anonymize Python files
        print("Anonymizing Python files...")
        for py_file in self.target_dir.glob('**/*.py'):
            if 'venv' not in str(py_file):
                with open(py_file, 'r') as f:
                    content = f.read()
                anonymized = self.anonymize_text(content)
                with open(py_file, 'w') as f:
                    f.write(anonymized)
        
        # Anonymize markdown files
        print("Anonymizing documentation...")
        for md_file in self.target_dir.glob('**/*.md'):
            with open(md_file, 'r') as f:
                content = f.read()
            anonymized = self.anonymize_text(content)
            with open(md_file, 'w') as f:
                f.write(anonymized)
        
        print("✅ Anonymization complete!")
        print(f"Sanitized project available at: {self.target_dir}")
        
    def create_gitignore(self):
        """Create a comprehensive .gitignore file."""
        gitignore_content = """# Personal and sensitive data
config/google_credentials.json
config/google_token.pickle
config/token.json
config/.env
.env
*.pickle
*.db
*.sqlite

# Personal templates
templates/resume.txt
templates/cover_letter.txt
config/job_search_config.yaml

# Application data
data/applications/
data/approved/
data/reviews/
data/results/

# Logs
logs/
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Project specific
data/progress.db
data/metrics.json
data/dashboard.html
"""
        
        gitignore_path = self.target_dir / '.gitignore'
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("Created .gitignore file")


def main():
    """CLI interface for anonymization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Anonymize job search project')
    parser.add_argument('--source', default='.',
                       help='Source directory to anonymize')
    parser.add_argument('--target', default='./anonymized',
                       help='Target directory for anonymized version')
    parser.add_argument('--create-examples', action='store_true',
                       help='Only create example files')
    
    args = parser.parse_args()
    
    anonymizer = Anonymizer(args.source, args.target)
    
    if args.create_examples:
        print("Creating example files only...")
        anonymizer.target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create templates directory
        templates_dir = anonymizer.target_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        # Create example files
        with open(templates_dir / 'resume.example.txt', 'w') as f:
            f.write(anonymizer.create_example_resume())
        
        with open(templates_dir / 'cover_letter.example.txt', 'w') as f:
            f.write(anonymizer.create_example_cover_letter())
        
        config_dir = anonymizer.target_dir / 'config'
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / 'config.example.yaml', 'w') as f:
            yaml.dump(anonymizer.create_example_config(), f, default_flow_style=False)
        
        print("✅ Example files created!")
    else:
        anonymizer.anonymize_project()
        anonymizer.create_gitignore()


if __name__ == "__main__":
    main()