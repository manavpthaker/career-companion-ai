"""Enhanced Template Engine using [FIRST_NAME]'s personalized application kits."""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from agents.application_kit_parser import ApplicationKitParser

class EnhancedTemplateEngine:
    """Generate personalized application materials using [FIRST_NAME]'s actual content."""
    
    def __init__(self, logger=None):
        """Initialize the enhanced template engine."""
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize the parser to load application kits
        self.parser = ApplicationKitParser(logger)
        
        # Cache parsed content
        self.senior_kit = self.parser.senior_kit
        self.director_kit = self.parser.director_kit
    
    def render_resume(self, job_data: Dict[str, Any]) -> str:
        """Generate personalized resume for a specific job."""
        
        # Determine which variant to use
        variant_level = self.parser.get_variant_for_role(job_data.get('title', ''))
        kit = self.director_kit if variant_level == 'director' else self.senior_kit
        
        # Check for company-specific variant
        company_variant = self.parser.get_company_variant(job_data.get('company', ''))
        
        # Build resume sections
        resume_lines = []
        
        # Header
        header = kit.get('header', {})
        resume_lines.append(f"**{header.get('name', '[YOUR_NAME]')}**")
        resume_lines.append(f"{header.get('location', '[CITY], [STATE_ABBR]')} • {header.get('phone', '[PHONE_NUMBER]')} • {header.get('email', '[USERNAME]@mpthaker.xyz')} • {header.get('linkedin', 'linkedin.com/in/[USERNAME]')}")
        resume_lines.append("")
        
        # Title - use company-specific if available
        if company_variant:
            resume_lines.append(f"**{company_variant.get('role', kit.get('header', {}).get('title', ''))}**")
        else:
            resume_lines.append(f"**{kit.get('header', {}).get('title', '')}**")
        
        # Summary - use company-specific if available
        if company_variant:
            resume_lines.append(company_variant.get('summary', kit.get('summary', '')))
        else:
            resume_lines.append(kit.get('summary', ''))
        resume_lines.append("")
        
        # Executive Summary (for director variant) or Signature Outcomes (for senior)
        if variant_level == 'director':
            resume_lines.append("**executive summary (what you get)**")
            for point in kit.get('executive_summary', []):
                resume_lines.append(f"- {point}")
            resume_lines.append("")
            
            resume_lines.append("**select portfolio outcomes**")
            for outcome in kit.get('portfolio_outcomes', []):
                resume_lines.append(f"- {outcome}")
        else:
            resume_lines.append("**signature outcomes**")
            # Add company-specific bullets first if available
            if company_variant:
                for bullet in company_variant.get('top_bullets', []):
                    resume_lines.append(f"- {bullet}")
            
            # Then add general signature outcomes
            for outcome in kit.get('signature_outcomes', [])[:5]:
                resume_lines.append(f"- {outcome}")
        resume_lines.append("")
        
        # Core Skills/Capabilities
        if variant_level == 'director':
            resume_lines.append("**core capabilities**")
            capabilities = kit.get('core_capabilities', {})
            for category, items in capabilities.items():
                resume_lines.append(f"- **{category}:** {items}")
        else:
            resume_lines.append("**core skills**")
            skills = kit.get('core_skills', {})
            for category, items in skills.items():
                resume_lines.append(f"- {category}: {items}")
        resume_lines.append("")
        
        resume_lines.append("---")
        resume_lines.append("")
        
        # Experience section
        resume_lines.append("## experience")
        resume_lines.append("")
        
        experiences = kit.get('experience', [])
        for exp in experiences:
            # Format company and title
            if variant_level == 'director' and exp.get('scope'):
                resume_lines.append(f"**{exp['company']} — {exp['title']}** *{exp['scope']}* ({exp['dates']})")
            else:
                resume_lines.append(f"**{exp['company']} — {exp['title']}** ({exp['dates']})")
            
            # Select relevant bullets based on job description
            job_description = job_data.get('description', '').lower()
            
            # Use selected achievements if matching the current role
            if 'lovingly' in exp['company'].lower():
                selected_achievements = self.parser.select_achievements(job_description, count=6)
                for achievement in selected_achievements:
                    resume_lines.append(f"- {achievement}")
            else:
                # Use existing bullets
                for bullet in exp['bullets'][:4]:  # Limit bullets for brevity
                    resume_lines.append(f"- {bullet}")
            resume_lines.append("")
        
        # Education
        resume_lines.append("**education**")
        resume_lines.append(kit.get('education', 'Pace University — BA, English Language & Literature'))
        resume_lines.append("")
        
        # Selected projects (for senior) or Speaking & Media (for director)
        if variant_level == 'director':
            resume_lines.append("**speaking & media**")
            for item in kit.get('speaking_media', []):
                resume_lines.append(item)
        else:
            resume_lines.append("**selected projects & ip**")
            for project in kit.get('selected_projects', []):
                resume_lines.append(f"- {project}")
        resume_lines.append("")
        
        # Keywords
        if variant_level == 'director':
            resume_lines.append("**keywords for ats**")
            resume_lines.append(kit.get('director_keywords', ''))
        else:
            resume_lines.append("**keywords for ats**")
            resume_lines.append(kit.get('ats_keywords', ''))
        
        return '\n'.join(resume_lines)
    
    def render_cover_letter(self, job_data: Dict[str, Any]) -> str:
        """Generate personalized cover letter for a specific job."""
        
        company = job_data.get('company', 'Your Company')
        position = job_data.get('title', 'the position')
        
        # Get the cover letter template
        template = self.senior_kit.get('cover_letter_template', '')
        
        if not template:
            # Fallback template
            template = """Dear Hiring Manager,

You're looking for a product leader who can turn an AI roadmap into shipped outcomes. That's where I do my best work. I operate end-to-end: clarify the problem, design the workflow, ship with guardrails, and measure adoption and ROI.

**Why [Company], why me**  
• **Roadmap → results:** I translate strategy into user stories, acceptance criteria, and weekly releases.  
• **Hands-on:** I build and ship AI-assisted workflows (agents, evals, guardrails) — not slideware.  
• **Governed speed:** I partner early with Security/Legal so we move fast without risking compliance.

**90-day plan**  
1) **Assess & align** current tools, datasets, and use cases; define success metrics (adoption, cycle time, quality).  
2) **Pilot with proof**: 1–2 high-leverage pilots with weekly evals and clear decision gates.  
3) **Operationalize** with playbooks and enablement; ramp shadow-mode → production.  
4) **Govern** via lightweight review and audit trails.

I'd love to share shipped examples and discuss where we can deliver impact in quarter one.

Sincerely,  
[YOUR_NAME]"""
        
        # Replace placeholders
        letter = template.replace('[Company]', company)
        letter = letter.replace('[Hiring Manager]', 'Hiring Manager')
        
        # Check for company-specific intro
        company_lower = company.lower()
        intros = self.senior_kit.get('cover_letter_intros', {})
        
        # Find matching intro
        company_intro = None
        if 'sparkplug' in company_lower:
            company_intro = intros.get('sparkplug')
        elif 'zillow' in company_lower:
            company_intro = intros.get('zillow')
        elif 'crowdstrike' in company_lower:
            company_intro = intros.get('crowdstrike')
        elif 'nextera' in company_lower:
            company_intro = intros.get('nextera')
        
        # Insert company-specific intro if available
        if company_intro:
            # Find the position after the first paragraph
            first_para_end = letter.find('\n\n', letter.find('That\'s where I do my best work.'))
            if first_para_end != -1:
                # Insert the company-specific intro after the first paragraph
                letter = (letter[:first_para_end + 2] + 
                         company_intro + '\n\n' + 
                         letter[first_para_end + 2:])
        
        # Add position-specific customization
        job_description = job_data.get('description', '').lower()
        
        # Customize the 90-day plan based on job focus
        if 'platform' in job_description:
            letter = letter.replace(
                '1–2 high-leverage pilots',
                'platform capabilities that enable multiple teams'
            )
        elif 'data' in job_description:
            letter = letter.replace(
                '1–2 high-leverage pilots',
                'data ingestion and quality pilots with measurable SLAs'
            )
        elif 'revenue' in job_description or 'growth' in job_description:
            letter = letter.replace(
                'adoption, cycle time, quality',
                'adoption, revenue impact, retention'
            )
        
        return letter
    
    def extract_template_variables(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract variables for template rendering (backwards compatibility)."""
        
        # Determine variant level
        variant_level = self.parser.get_variant_for_role(job_data.get('title', ''))
        
        # Get company variant if available
        company_variant = self.parser.get_company_variant(job_data.get('company', ''))
        
        variables = {
            'variant_level': variant_level,
            'has_company_variant': company_variant is not None,
            'company': job_data.get('company', ''),
            'position': job_data.get('title', ''),
            'location': job_data.get('location', ''),
            'salary': job_data.get('salary', ''),
            'match_score': job_data.get('match_score', 0),
            'job_url': job_data.get('url', ''),
            'selected_achievements': self.parser.select_achievements(
                job_data.get('description', ''), 
                count=5
            )
        }
        
        # Add company stage detection
        variables['company_stage'] = self._determine_company_stage(job_data)
        
        # Add technical focus
        variables['technical_focus'] = self._extract_technical_focus(job_data)
        
        return variables
    
    def _determine_company_stage(self, job_data: Dict[str, Any]) -> str:
        """Determine company stage from job data."""
        company = job_data.get('company', '').lower()
        description = job_data.get('description', '').lower()
        
        # Check for enterprise indicators
        enterprise_indicators = [
            'fortune', 'public company', 'nasdaq', 'nyse', 'enterprise',
            'global leader', 'industry leader', 'established'
        ]
        
        if any(indicator in description or indicator in company for indicator in enterprise_indicators):
            return 'enterprise'
        
        # Check for growth stage
        growth_indicators = [
            'series c', 'series d', 'series e', 'pre-ipo', 'unicorn',
            'scaling', 'rapid growth'
        ]
        
        if any(indicator in description for indicator in growth_indicators):
            return 'growth'
        
        # Default
        return 'startup'
    
    def _extract_technical_focus(self, job_data: Dict[str, Any]) -> str:
        """Extract the primary technical focus from job data."""
        description = job_data.get('description', '').lower()
        title = job_data.get('title', '').lower()
        
        # Check for different focus areas
        if 'platform' in title or 'platform' in description:
            return 'AI platforms and infrastructure'
        elif 'data' in title or 'data product' in description:
            return 'Data products and ingestion'
        elif 'growth' in title or 'revenue' in description:
            return 'Growth and revenue optimization'
        elif 'genai' in title or 'generative' in description:
            return 'Generative AI and LLM applications'
        else:
            return 'AI product development'