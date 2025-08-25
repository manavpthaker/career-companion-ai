"""Personal Context Manager for mapping experiences to opportunities."""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class PersonalContextManager:
    """Manage personal experiences, values, and connections for job applications."""
    
    def __init__(self, logger=None):
        """Initialize with [FIRST_NAME]'s personal context."""
        self.logger = logger or logging.getLogger(__name__)
        
        # Core experiences mapped to industries/companies
        self.experiences = {
            'gaming_retention': {
                'description': 'Scaled e-grocery to 20K+ users with gamified engagement achieving 70% cohort retention',
                'metrics': '<$10 CAC, LTV >$1,000',
                'relevance_keywords': ['gaming', 'retention', 'engagement', 'monetization', 'economy'],
                'companies': ['Scopely', 'Epic Games', 'Roblox', 'Unity'],
                'talking_point': 'I understand the delicate balance of engagement and monetization from scaling Subziwalla with gamified retention mechanics'
            },
            'ai_transformation': {
                'description': 'Reduced PM overhead by 80% through multi-agent AI systems at [CURRENT_COMPANY]',
                'metrics': 'Prevented $400K churn, identified $6M ARR opportunities',
                'relevance_keywords': ['ai', 'llm', 'genai', 'automation', 'agent', 'ml'],
                'companies': ['OpenAI', 'Anthropic', 'Meta', 'Google', 'Microsoft'],
                'talking_point': 'Built production multi-agent systems achieving 80% efficiency gains with evaluation frameworks and guardrails'
            },
            'platform_building': {
                'description': 'Architected reusable LLM platform with 50+ prompt templates and evaluation harnesses',
                'metrics': 'Cut prototype cycles from days to hours',
                'relevance_keywords': ['platform', 'infrastructure', 'developer', 'api', 'framework'],
                'companies': ['ClickUp', 'Stripe', 'Twilio', 'Datadog'],
                'talking_point': 'I build platforms that enable other teams to ship faster - like our prompt library that cut prototyping from days to hours'
            },
            'edtech_learning': {
                'description': 'Parent perspective on EdTech + AI-assisted learning systems',
                'metrics': '27% productivity lift across teams through AI enablement',
                'relevance_keywords': ['education', 'learning', 'edtech', 'training', 'curriculum'],
                'companies': ['Committee for Children', 'Nerdy', 'Duolingo', 'Coursera'],
                'talking_point': 'As a parent using EdTech tools daily, I bring both user empathy and technical expertise to learning products'
            },
            'b2b_saas': {
                'description': 'Scaled PropTech SaaS from concept to enterprise pilots as CPO at [PREVIOUS_COMPANY]',
                'metrics': '12% MoM active-use growth during rollout',
                'relevance_keywords': ['b2b', 'saas', 'enterprise', 'sales', 'gtm'],
                'companies': ['Salesforce', 'HubSpot', 'ClickUp', 'Monday.com'],
                'talking_point': 'Led 0→1 to enterprise pilots, understanding both startup velocity and enterprise governance needs'
            },
            'healthcare_regulated': {
                'description': 'Navigated regulated environments with HIPAA compliance and security reviews',
                'metrics': 'Maintained velocity while meeting compliance requirements',
                'relevance_keywords': ['healthcare', 'hipaa', 'compliance', 'regulation', 'security'],
                'companies': ['Bicycle Health', 'Oscar Health', 'One Medical'],
                'talking_point': 'I\'ve successfully balanced innovation speed with regulatory compliance in sensitive data environments'
            },
            'martech_growth': {
                'description': 'Achieved 40% targeted-campaign conversion with personalization at Subziwalla',
                'metrics': 'Built retention programs yielding 70% cohort retention',
                'relevance_keywords': ['marketing', 'martech', 'growth', 'conversion', 'personalization'],
                'companies': ['NBCUniversal', 'Adobe', 'Mailchimp', 'Klaviyo'],
                'talking_point': 'I\'ve built personalization engines that achieved 40% conversion rates through data-driven segmentation'
            },
            'data_products': {
                'description': 'Built data ingestion pipelines with anomaly detection and entity resolution',
                'metrics': 'Reduced downstream incidents by 40%',
                'relevance_keywords': ['data', 'analytics', 'pipeline', 'quality', 'ingestion'],
                'companies': ['Databricks', 'Snowflake', 'Palantir', 'Tableau'],
                'talking_point': 'Implemented data health SLAs and anomaly detection reducing incidents by 40%'
            }
        }
        
        # Side projects and thought leadership
        self.side_projects = {
            'pm_podcast': {
                'name': 'PM in the PM',
                'description': 'Host practitioner podcast on shipping GenAI responsibly',
                'relevance': 'Demonstrates thought leadership and commitment to responsible AI',
                'url': 'Coming soon'
            },
            'weather_threads': {
                'name': 'WeatherThreads',
                'description': 'Built AI fashion recommendation app with personalized comfort settings',
                'relevance': 'Shows hands-on technical skills and consumer product thinking',
                'technologies': ['LLM', 'personalization', 'rules engine']
            },
            'job_automation': {
                'name': 'Job Search Automation',
                'description': 'Open-source job search system with AI personalization',
                'relevance': 'Demonstrates building in public and automation expertise',
                'github': 'github.com/[USERNAME]'
            }
        }
        
        # Personal values and preferences
        self.values = {
            'family_first': {
                'description': 'Sustainable work-life integration, no hustle culture',
                'relevance': 'Seeking companies with healthy culture and work-life balance',
                'anti_patterns': ['24/7 availability', 'weekend work expected', 'unlimited PTO (but never taken)']
            },
            'building_in_public': {
                'description': 'Open source contributor, transparent about successes and failures',
                'relevance': 'Prefer companies that value transparency and knowledge sharing',
                'examples': ['Open source projects', 'Public speaking', 'Blog posts']
            },
            'ethical_ai': {
                'description': 'Committed to responsible AI with governance and safety',
                'relevance': 'Align with companies prioritizing AI safety and ethics',
                'practices': ['Evaluation frameworks', 'Bias testing', 'Guardrails', 'Audit trails']
            },
            'calm_leadership': {
                'description': 'Calm in chaos, crisp in comms, biased to ship',
                'relevance': 'Thrive in fast-paced environments while maintaining composure',
                'style': 'Servant leadership with high accountability'
            }
        }
        
        # Location and logistics
        self.logistics = {
            'location': '[CITY], [STATE_ABBR]',
            'remote_preference': 'Strongly prefer remote, proven track record',
            'nyc_commute': 'Easy 35-minute train to NYC when needed',
            'west_coast': 'Open to occasional travel, not relocation',
            'time_zones': 'Experienced working across time zones',
            'travel': 'Open to 10-20% travel for strategic meetings'
        }
        
        # Success stories bank
        self.success_stories = {
            'scaled_ecommerce': {
                'story': 'Founded and scaled Subziwalla from idea to 20,000+ users over 5 years',
                'challenge': 'Competing with established grocery delivery giants',
                'solution': 'Built personalized retention programs and gamified engagement',
                'outcome': 'Achieved <$10 CAC with LTV >$1,000 in top cohorts',
                'learning': 'Small teams can compete through focus and personalization'
            },
            'ai_transformation': {
                'story': 'Led AI transformation at [CURRENT_COMPANY] reducing PM overhead by 80%',
                'challenge': 'Team drowning in manual tasks, missing deadlines',
                'solution': 'Built multi-agent system for sprint planning and QA',
                'outcome': 'Improved on-time delivery and prevented $400K churn',
                'learning': 'AI augmentation > AI replacement for knowledge work'
            },
            'enterprise_pivot': {
                'story': 'Pivoted [PREVIOUS_COMPANY] from SMB to enterprise during market downturn',
                'challenge': 'SMB customers churning, needed enterprise validation',
                'solution': 'Rebuilt product for compliance and enterprise workflows',
                'outcome': 'Secured enterprise pilots and improved unit economics',
                'learning': 'Sometimes you need to move upmarket to survive'
            },
            'team_scaling': {
                'story': 'Scaled team from 5 to 30 people at Subziwalla',
                'challenge': 'Maintaining culture and velocity during rapid growth',
                'solution': 'Implemented ops playbooks and clear SLAs',
                'outcome': 'Maintained quality while 6x-ing team size',
                'learning': 'Process enables creativity, not constrains it'
            }
        }
        
        # Conversation starters for different company types
        self.conversation_starters = {
            'high_growth': "I saw your recent funding round - exciting times! How are you thinking about scaling the product org?",
            'enterprise': "Working with Fortune [STREET_ADDRESS] present unique challenges - how do you balance innovation with governance?",
            'startup': "The 0→1 phase is my favorite - what's the biggest unknown you're trying to validate right now?",
            'turnaround': "I've navigated similar transitions - what's the team's morale like during this transformation?",
            'ai_focused': "Your approach to {specific_ai_tech} is interesting - how are you thinking about evaluation and safety?",
            'consumer': "20K users taught me that retention > acquisition - what's your north star metric?",
            'b2b': "I've found that the best B2B products feel like B2C - how do you think about end-user experience?",
            'platform': "Platform teams are force multipliers - how do you measure internal developer satisfaction?"
        }
    
    def find_connections(self, company_name: str, job_title: str, job_description: str) -> Dict[str, Any]:
        """Find personal connections to a company and role."""
        
        connections = {
            'relevant_experiences': [],
            'applicable_projects': [],
            'shared_values': [],
            'conversation_starters': [],
            'unique_angle': '',
            'why_interested': '',
            'what_i_bring': []
        }
        
        # Match experiences
        job_text = f"{job_title} {job_description} {company_name}".lower()
        
        for exp_key, experience in self.experiences.items():
            relevance_score = sum([STREET_ADDRESS] in experience['relevance_keywords'] if keyword in job_text)
            
            # Check if company is specifically mentioned
            company_match = any(comp.lower() in company_name.lower() for comp in experience.get('companies', []))
            
            if relevance_score > 0 or company_match:
                connections['relevant_experiences'].append({
                    'type': exp_key,
                    'description': experience['description'],
                    'metrics': experience['metrics'],
                    'talking_point': experience['talking_point'],
                    'relevance_score': relevance_score + (2 if company_match else 0)
                })
        
        # Sort by relevance
        connections['relevant_experiences'].sort(key=lambda x: x['relevance_score'], reverse=True)
        connections['relevant_experiences'] = connections['relevant_experiences'][:3]  # Top 3
        
        # Match side projects
        for proj_key, project in self.side_projects.items():
            if any(tech in job_text for tech in project.get('technologies', [])):
                connections['applicable_projects'].append(project)
        
        # Match values
        if 'remote' in job_text or 'flexible' in job_text:
            connections['shared_values'].append(self.values['family_first'])
        
        if 'open source' in job_text or 'transparency' in job_text:
            connections['shared_values'].append(self.values['building_in_public'])
        
        if 'responsible' in job_text or 'ethical' in job_text or 'safety' in job_text:
            connections['shared_values'].append(self.values['ethical_ai'])
        
        # Generate unique angle
        if connections['relevant_experiences']:
            top_exp = connections['relevant_experiences'][0]
            connections['unique_angle'] = f"Unlike typical PMs, I've actually {top_exp['description'].lower()}"
        
        # Generate why interested
        connections['why_interested'] = self._generate_why_interested(company_name, job_title, connections)
        
        # What I bring
        connections['what_i_bring'] = self._generate_what_i_bring(connections)
        
        # Add conversation starters
        connections['conversation_starters'] = self._select_conversation_starters(company_name, job_text)
        
        return connections
    
    def _generate_why_interested(self, company: str, role: str, connections: Dict) -> str:
        """Generate a personalized 'why interested' statement."""
        
        reasons = []
        
        if connections['relevant_experiences']:
            exp = connections['relevant_experiences'][0]
            reasons.append(f"My experience with {exp['type'].replace('_', ' ')} directly applies")
        
        if connections['shared_values']:
            reasons.append(f"Your commitment to {connections['shared_values'][0]['description'].split(',')[0]} resonates with me")
        
        if connections['applicable_projects']:
            reasons.append(f"I've been exploring similar problems with my {connections['applicable_projects'][0]['name']} project")
        
        if not reasons:
            reasons.append(f"The opportunity to shape {role} at {company} aligns perfectly with my experience")
        
        return " and ".join(reasons[:2])
    
    def _generate_what_i_bring(self, connections: Dict) -> List[str]:
        """Generate list of unique value propositions."""
        
        value_props = []
        
        # Add top experiences
        for exp in connections['relevant_experiences'][:2]:
            value_props.append(f"{exp['metrics']} from {exp['type'].replace('_', ' ')}")
        
        # Add leadership style
        value_props.append("Calm leadership that ships weekly while maintaining quality")
        
        # Add technical depth if relevant
        if any('ai' in str(exp) for exp in connections['relevant_experiences']):
            value_props.append("Hands-on AI expertise from prompt engineering to production deployment")
        
        return value_props[:3]
    
    def _select_conversation_starters(self, company: str, job_text: str) -> List[str]:
        """Select appropriate conversation starters."""
        
        starters = []
        
        # Determine company stage
        if any(term in job_text for term in ['series a', 'series b', 'seed', 'startup']):
            starters.append(self.conversation_starters['startup'])
        elif any(term in job_text for term in ['enterprise', 'fortune', 'global']):
            starters.append(self.conversation_starters['enterprise'])
        
        # Add AI-specific if relevant
        if 'ai' in job_text or 'ml' in job_text:
            starter = self.conversation_starters['ai_focused']
            # Try to make it specific
            if 'llm' in job_text:
                starter = starter.replace('{specific_ai_tech}', 'LLM orchestration')
            elif 'agent' in job_text:
                starter = starter.replace('{specific_ai_tech}', 'agent systems')
            else:
                starter = starter.replace('{specific_ai_tech}', 'AI')
            starters.append(starter)
        
        # Add platform-specific if relevant
        if 'platform' in job_text:
            starters.append(self.conversation_starters['platform'])
        
        return starters[:2]
    
    def get_location_preference(self, location: str) -> Dict[str, str]:
        """Get location-specific preferences and talking points."""
        
        location_lower = location.lower()
        
        if 'remote' in location_lower:
            return {
                'preference': 'Perfect fit - proven remote collaboration across time zones',
                'talking_point': self.logistics['remote_preference']
            }
        elif 'new york' in location_lower or 'nyc' in location_lower:
            return {
                'preference': 'Great location - easy 35-min train commute from [CITY]',
                'talking_point': self.logistics['nyc_commute']
            }
        elif 'san francisco' in location_lower or 'bay area' in location_lower:
            return {
                'preference': 'Open to occasional travel for strategic meetings',
                'talking_point': self.logistics['west_coast']
            }
        else:
            return {
                'preference': 'Flexible on location with preference for remote',
                'talking_point': self.logistics['remote_preference']
            }