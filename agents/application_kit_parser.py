"""Parser for [YOUR_NAME]'s application kit markdown files."""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class ApplicationKitParser:
    """Parse and structure [FIRST_NAME]'s personalized application materials."""
    
    def __init__(self, logger=None):
        """Initialize the parser."""
        self.logger = logger or logging.getLogger(__name__)
        self.senior_kit_path = Path("/Users/[USERNAME]thaker/brownmanbeard/05-professional/job_application_kit_[USERNAME]_thaker_aug_19_2025.md")
        self.director_kit_path = Path("/Users/[USERNAME]thaker/brownmanbeard/05-professional/director_variant_resume_portfolio_site_prompt_[USERNAME]_thaker_aug_21_2025.md")
        
        # Parse both kits on initialization
        self.senior_kit = self._parse_senior_kit()
        self.director_kit = self._parse_director_kit()
        
    def _parse_senior_kit(self) -> Dict[str, Any]:
        """Parse the senior PM application kit."""
        if not self.senior_kit_path.exists():
            self.logger.warning(f"Senior kit not found at {self.senior_kit_path}")
            return {}
            
        with open(self.senior_kit_path, 'r') as f:
            content = f.read()
        
        kit = {
            'level': 'senior',
            'header': self._extract_header(content),
            'summary': self._extract_summary(content),
            'signature_outcomes': self._extract_signature_outcomes(content),
            'core_skills': self._extract_core_skills(content),
            'experience': self._extract_experience(content),
            'education': self._extract_education(content),
            'selected_projects': self._extract_selected_projects(content),
            'ats_keywords': self._extract_ats_keywords(content),
            'role_variants': self._extract_role_variants(content),
            'achievements_bank': self._extract_achievements_bank(content),
            'cover_letter_template': self._extract_cover_letter_template(content),
            'cover_letter_intros': self._extract_cover_letter_intros(content)
        }
        
        return kit
    
    def _parse_director_kit(self) -> Dict[str, Any]:
        """Parse the director-level application kit."""
        if not self.director_kit_path.exists():
            self.logger.warning(f"Director kit not found at {self.director_kit_path}")
            return {}
            
        with open(self.director_kit_path, 'r') as f:
            content = f.read()
        
        kit = {
            'level': 'director',
            'header': self._extract_director_header(content),
            'summary': self._extract_director_summary(content),
            'executive_summary': self._extract_executive_summary(content),
            'portfolio_outcomes': self._extract_portfolio_outcomes(content),
            'core_capabilities': self._extract_core_capabilities(content),
            'experience': self._extract_director_experience(content),
            'education': self._extract_education(content),
            'speaking_media': self._extract_speaking_media(content),
            'director_keywords': self._extract_director_keywords(content),
            'org_design': self._extract_org_design(content),
            'stakeholder_governance': self._extract_stakeholder_governance(content),
            'roi_instrumentation': self._extract_roi_instrumentation(content)
        }
        
        return kit
    
    def _extract_header(self, content: str) -> Dict[str, str]:
        """Extract header information."""
        header = {}
        
        # Extract name
        name_match = re.search(r'\*\*[YOUR_NAME]\*\*', content)
        if name_match:
            header['name'] = '[YOUR_NAME]'
        
        # Extract contact info
        contact_match = re.search(r'[CITY], [STATE_ABBR] • ([\d‑-]+) • ([^\s]+) • ([^\s]+)', content)
        if contact_match:
            header['location'] = '[CITY], [STATE_ABBR]'
            header['phone'] = contact_match.group(1)
            header['email'] = '[USERNAME]@mpthaker.xyz'  # Use updated email
            header['linkedin'] = 'linkedin.com/in/[USERNAME]'  # Use updated LinkedIn
        
        # Extract title
        title_match = re.search(r'\*\*senior product manager — (.*?)\*\*', content)
        if title_match:
            header['title'] = f"senior product manager — {title_match.group(1)}"
        
        return header
    
    def _extract_summary(self, content: str) -> str:
        """Extract professional summary."""
        summary_match = re.search(
            r'Builder–operator with.*?Calm in chaos, crisp in comms, and biased to ship\.',
            content,
            re.DOTALL
        )
        if summary_match:
            return summary_match.group(0).strip()
        return ""
    
    def _extract_signature_outcomes(self, content: str) -> List[str]:
        """Extract signature outcomes with metrics."""
        outcomes = []
        
        # Find the signature outcomes section
        section_match = re.search(
            r'\*\*signature outcomes\*\*.*?\n(.*?)(?=\*\*core skills\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    # Clean up the line and preserve the ⚠︎ markers
                    outcome = line[2:].strip()
                    outcomes.append(outcome)
        
        return outcomes
    
    def _extract_core_skills(self, content: str) -> Dict[str, str]:
        """Extract core skills section."""
        skills = {}
        
        section_match = re.search(
            r'\*\*core skills\*\*.*?\n(.*?)(?=---|\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- ') and ':' in line:
                    parts = line[2:].split(':', 1)
                    if len(parts) == 2:
                        category = parts[0].strip()
                        items = parts[1].strip()
                        skills[category] = items
        
        return skills
    
    def _extract_experience(self, content: str) -> List[Dict[str, Any]]:
        """Extract experience section."""
        experiences = []
        
        # Find experience section
        section_match = re.search(
            r'## experience\n\n(.*?)(?=\*\*education\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            exp_text = section_match.group(1)
            
            # Parse each job
            job_pattern = r'\*\*(.*?) — (.*?)\*\* \((.*?)\)\n((?:- .*?\n)*)'
            
            for match in re.finditer(job_pattern, exp_text):
                job = {
                    'company': match.group(1),
                    'title': match.group(2),
                    'dates': match.group(3),
                    'bullets': []
                }
                
                # Extract bullets
                bullets_text = match.group(4)
                for line in bullets_text.split('\n'):
                    if line.startswith('- '):
                        job['bullets'].append(line[2:].strip())
                
                experiences.append(job)
        
        return experiences
    
    def _extract_education(self, content: str) -> str:
        """Extract education information."""
        edu_match = re.search(
            r'\*\*education\*\*.*?\n(.*?)(?=\n\*\*|$)',
            content,
            re.DOTALL
        )
        if edu_match:
            return edu_match.group(1).strip()
        return ""
    
    def _extract_selected_projects(self, content: str) -> List[str]:
        """Extract selected projects and IP."""
        projects = []
        
        section_match = re.search(
            r'\*\*selected projects & ip\*\*.*?\n(.*?)(?=\*\*keywords|$)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    projects.append(line[2:].strip())
        
        return projects
    
    def _extract_ats_keywords(self, content: str) -> str:
        """Extract ATS keywords."""
        keywords_match = re.search(
            r'\*\*keywords for ats\*\*.*?\n(.*?)(?=---|\n#|$)',
            content,
            re.DOTALL
        )
        if keywords_match:
            return keywords_match.group(1).strip()
        return ""
    
    def _extract_role_variants(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Extract role-specific variants."""
        variants = {}
        
        # Find targeted variants section
        section_match = re.search(
            r'# targeted variants.*?\n\n(.*?)(?=# achievements bank|$)',
            content,
            re.DOTALL
        )
        
        if section_match:
            variants_text = section_match.group(1)
            
            # Parse each variant
            variant_pattern = r'### (.*?)\n\*\*summary for .*?\*\*: (.*?)\n\*\*top bullets to add at top\*\*\n((?:- .*?\n)*)'
            
            for match in re.finditer(variant_pattern, variants_text):
                company_key = match.group(1).split(' — ')[0].lower().replace(' ', '_')
                variants[company_key] = {
                    'role': match.group(1),
                    'summary': match.group(2),
                    'top_bullets': []
                }
                
                # Extract bullets
                bullets_text = match.group(3)
                for line in bullets_text.split('\n'):
                    if line.startswith('- '):
                        variants[company_key]['top_bullets'].append(line[2:].strip())
        
        return variants
    
    def _extract_achievements_bank(self, content: str) -> List[str]:
        """Extract achievements bank."""
        achievements = []
        
        section_match = re.search(
            r'# achievements bank.*?\n\n(.*?)(?=---|\n#|$)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    # Clean and format achievement
                    achievement = line[2:].strip()
                    # Remove the bold formatting but keep the structure
                    achievement = re.sub(r'\*\*(.*?)\*\*', r'\1', achievement)
                    achievements.append(achievement)
        
        return achievements
    
    def _extract_cover_letter_template(self, content: str) -> str:
        """Extract master cover letter template."""
        template_match = re.search(
            r'\*\*master template.*?\*\*\n\n(Dear.*?[YOUR_NAME])',
            content,
            re.DOTALL
        )
        if template_match:
            return template_match.group(1).strip()
        return ""
    
    def _extract_cover_letter_intros(self, content: str) -> Dict[str, str]:
        """Extract role-specific cover letter intros."""
        intros = {}
        
        section_match = re.search(
            r'\*\*role‑specific intros.*?\*\*\n(.*?)(?=---|\n#|$)',
            content,
            re.DOTALL
        )
        
        if section_match:
            intros_text = section_match.group(1)
            
            # Parse each intro
            for line in intros_text.split('\n'):
                if line.startswith('- '):
                    # Extract company and intro
                    match = re.match(r'- \*\*(.*?):\*\* (.*)', line)
                    if match:
                        company = match.group(1).lower().replace(' ', '_')
                        intro = match.group(2)
                        intros[company] = intro
        
        return intros
    
    # Director-specific extraction methods
    def _extract_director_header(self, content: str) -> Dict[str, str]:
        """Extract director-level header."""
        header = {}
        
        # Similar to senior but with director title
        header['name'] = '[YOUR_NAME]'
        
        contact_match = re.search(r'[CITY], [STATE_ABBR] • ([\d‑-]+) • ([^\s]+) • ([^\s]+)', content)
        if contact_match:
            header['location'] = '[CITY], [STATE_ABBR]'
            header['phone'] = contact_match.group(1)
            header['email'] = '[USERNAME]@mpthaker.xyz'  # Use updated email
            header['linkedin'] = 'linkedin.com/in/[USERNAME]'  # Use updated LinkedIn
        
        header['title'] = 'director‑track product leader — ai platforms, data products, and go‑to‑market'
        
        return header
    
    def _extract_director_summary(self, content: str) -> str:
        """Extract director-level summary."""
        summary_match = re.search(
            r'Builder–operator with.*?accountable to adoption, cycle time, quality, and ROI\.',
            content,
            re.DOTALL
        )
        if summary_match:
            return summary_match.group(0).strip()
        return ""
    
    def _extract_executive_summary(self, content: str) -> List[str]:
        """Extract executive summary points."""
        points = []
        
        section_match = re.search(
            r'\*\*executive summary \(what you get\)\*\*.*?\n(.*?)(?=\*\*select portfolio outcomes\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    points.append(line[2:].strip())
        
        return points
    
    def _extract_portfolio_outcomes(self, content: str) -> List[str]:
        """Extract portfolio outcomes."""
        outcomes = []
        
        section_match = re.search(
            r'\*\*select portfolio outcomes\*\*.*?\n(.*?)(?=\*\*core capabilities\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    outcomes.append(line[2:].strip())
        
        return outcomes
    
    def _extract_core_capabilities(self, content: str) -> Dict[str, str]:
        """Extract core capabilities for director level."""
        capabilities = {}
        
        section_match = re.search(
            r'\*\*core capabilities\*\*.*?\n(.*?)(?=---|\n##)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- ') and ':' in line:
                    parts = line[2:].split(':', 1)
                    if len(parts) == 2:
                        category = parts[0].strip().replace('**', '')
                        items = parts[1].strip()
                        capabilities[category] = items
        
        return capabilities
    
    def _extract_director_experience(self, content: str) -> List[Dict[str, Any]]:
        """Extract director-level experience."""
        experiences = []
        
        section_match = re.search(
            r'## experience\n\n(.*?)(?=\*\*education\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            exp_text = section_match.group(1)
            
            # Parse each job with director-level formatting
            job_pattern = r'\*\*(.*?) — (.*?)\*\*(?:\s*\*(.*?)\*)?\s*\((.*?)\)\n((?:- .*?\n)*)'
            
            for match in re.finditer(job_pattern, exp_text):
                job = {
                    'company': match.group(1),
                    'title': match.group(2),
                    'scope': match.group(3) if match.group(3) else None,
                    'dates': match.group(4),
                    'bullets': []
                }
                
                bullets_text = match.group(5)
                for line in bullets_text.split('\n'):
                    if line.startswith('- '):
                        # Clean director-level bullets with bold verbs
                        bullet = re.sub(r'\*\*(.*?)\*\*', r'\1', line[2:].strip())
                        job['bullets'].append(bullet)
                
                experiences.append(job)
        
        return experiences
    
    def _extract_speaking_media(self, content: str) -> List[str]:
        """Extract speaking and media section."""
        media = []
        
        section_match = re.search(
            r'\*\*speaking & media\*\*.*?\n(.*?)(?=\*\*director‑track keywords\*\*)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.strip():
                    media.append(line.strip())
        
        return media
    
    def _extract_director_keywords(self, content: str) -> str:
        """Extract director-track keywords."""
        keywords_match = re.search(
            r'\*\*director‑track keywords\*\*.*?\n(.*?)(?=---|\n#|$)',
            content,
            re.DOTALL
        )
        if keywords_match:
            return keywords_match.group(1).strip()
        return ""
    
    def _extract_org_design(self, content: str) -> List[str]:
        """Extract org design and operating rhythms."""
        design = []
        
        section_match = re.search(
            r'\*\*org design & operating rhythms\*\*.*?\n(.*?)(?=\*\*stakeholder)',
            content,
            re.DOTALL
        )
        
        if section_match:
            lines = section_match.group(1).strip().split('\n')
            for line in lines:
                if line.startswith('- '):
                    design.append(line[2:].strip())
        
        return design
    
    def _extract_stakeholder_governance(self, content: str) -> str:
        """Extract stakeholder and governance model."""
        gov_match = re.search(
            r'\*\*stakeholder & governance model\*\*.*?\n(.*?)(?=\*\*ROI)',
            content,
            re.DOTALL
        )
        if gov_match:
            return gov_match.group(1).strip()[2:] if gov_match.group(1).strip().startswith('- ') else gov_match.group(1).strip()
        return ""
    
    def _extract_roi_instrumentation(self, content: str) -> str:
        """Extract ROI instrumentation."""
        roi_match = re.search(
            r'\*\*ROI instrumentation\*\*.*?\n(.*?)(?=\*\*tooling\*\*)',
            content,
            re.DOTALL
        )
        if roi_match:
            return roi_match.group(1).strip()[2:] if roi_match.group(1).strip().startswith('- ') else roi_match.group(1).strip()
        return ""
    
    def get_variant_for_role(self, job_title: str, company: str = None) -> str:
        """Determine which variant to use based on job title and company."""
        title_lower = job_title.lower()
        
        # Check for director-level indicators
        director_indicators = ['director', 'principal', 'staff', 'head of', 'vp', 'vice president']
        if any(indicator in title_lower for indicator in director_indicators):
            return 'director'
        
        # Default to senior for IC roles
        return 'senior'
    
    def get_company_variant(self, company: str) -> Optional[Dict[str, Any]]:
        """Get company-specific variant if available."""
        company_lower = company.lower()
        
        # Check for known company variants
        if 'sparkplug' in company_lower:
            return self.senior_kit.get('role_variants', {}).get('sparkplug')
        elif 'zillow' in company_lower:
            return self.senior_kit.get('role_variants', {}).get('zillow')
        elif 'crowdstrike' in company_lower:
            return self.senior_kit.get('role_variants', {}).get('crowdstrike')
        elif 'nextera' in company_lower:
            return self.senior_kit.get('role_variants', {}).get('nextera')
        
        return None
    
    def select_achievements(self, job_description: str, count: int = 5) -> List[str]:
        """Select most relevant achievements based on job description."""
        achievements = self.senior_kit.get('achievements_bank', [])
        
        if not achievements:
            return []
        
        # Keywords to look for and their associated achievements
        keyword_mapping = {
            'automation': ['multi‑agent', 'reduced PM busywork', 'prototype cycle'],
            'revenue': ['$6M ARR', '$400K', 'churn', 'retention'],
            'data': ['data‑health', 'anomaly detection', 'entity resolution'],
            'platform': ['LLM experimentation', 'notebook', 'guardrails'],
            'scale': ['20,000+ users', 'CAC', 'LTV'],
            'governance': ['responsible‑AI', 'audit trails', 'Security/Legal']
        }
        
        description_lower = job_description.lower()
        selected = []
        
        # Score achievements based on keyword matches
        for achievement in achievements:
            score = [STREET_ADDRESS], indicators in keyword_mapping.items():
                if keyword in description_lower:
                    for indicator in indicators:
                        if indicator.lower() in achievement.lower():
                            score += 1
            
            selected.append((score, achievement))
        
        # Sort by score and return top achievements
        selected.sort(key=lambda x: x[0], reverse=True)
        return [achievement for score, achievement in selected[:count]]