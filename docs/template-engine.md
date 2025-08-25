# 📝 Template Engine Documentation

## Overview

The Template Engine generates personalized cover letters and resumes by matching your experience to job requirements. It uses LLMs to create tailored application materials while maintaining authenticity.

## Architecture

### Content Parsing

The system parses structured resume content from markdown files:

```python
class ApplicationKitParser:
    """Parse resume content from markdown format."""
    
    def __init__(self):
        self.content_extractors = {
            'experience': ExperienceExtractor(),
            'achievements': AchievementExtractor(),  
            'skills': SkillsExtractor(),
            'projects': ProjectExtractor()
        }
        
    def parse_application_kit(self, markdown_content):
        """Extract structured data from markdown resume."""
        
        parsed_data = {}
        
        for section_type, extractor in self.content_extractors.items():
            try:
                parsed_data[section_type] = extractor.extract(markdown_content)
            except Exception as e:
                self.logger.warning(f"Failed to parse {section_type}: {e}")
                parsed_data[section_type] = []
        
        return ApplicationKit(parsed_data)
```

### Experience Matching

Map your experiences to job requirements:

```python
class PersonalContextManager:
    """Match personal experiences to job requirements."""
    
    def __init__(self):
        self.experience_database = {
            'project_management': {
                'description': 'Led cross-functional teams',
                'keywords': ['pm', 'product', 'management', 'team'],
                'talking_point': 'Experience leading product initiatives'
            },
            # Add more experiences...
        }
    
    def find_relevant_experiences(self, job_title, job_description):
        """Find experiences matching the job."""
        
        job_text = f"{job_title} {job_description}".lower()
        relevant = []
        
        for exp_key, experience in self.experience_database.items():
            # Simple keyword matching
            matches = sum(1 for keyword in experience['keywords'] 
                         if keyword in job_text)
            
            if matches > 0:
                relevant.append({
                    'experience': experience,
                    'relevance_score': matches
                })
        
        # Return top matches
        return sorted(relevant, key=lambda x: x['relevance_score'], 
                     reverse=True)[:3]
```

## Resume Generation

### Basic Resume Builder

Generate targeted resumes based on job requirements:

```python
class EnhancedTemplateEngine:
    """Generate personalized application materials."""
    
    def __init__(self):
        self.parser = ApplicationKitParser()
        self.context_manager = PersonalContextManager()
        
    def render_targeted_resume(self, job_data, application_kit):
        """Generate resume for specific job."""
        
        # Determine role level
        role_level = self._analyze_role_level(job_data['title'])
        
        # Find relevant experiences
        relevant_experiences = self.context_manager.find_relevant_experiences(
            job_data['title'], 
            job_data['description']
        )
        
        # Build resume sections
        resume = {
            'header': self._build_header(application_kit),
            'summary': self._build_summary(job_data),
            'experience': self._format_experiences(relevant_experiences),
            'skills': self._extract_skills(application_kit)
        }
        
        return self._compile_resume(resume)
```

## Cover Letter Generation

### Template-Based Generation

Create cover letters using templates and job-specific content:

```python
class CoverLetterEngine:
    """Generate personalized cover letters."""
    
    def __init__(self):
        self.template = """
        Dear Hiring Manager,
        
        I am writing to express my interest in the {role} position at {company}.
        
        {relevant_experience}
        
        {why_interested}
        
        Best regards,
        {name}
        """
        
    def generate_cover_letter(self, job_data, personal_context):
        """Create cover letter for specific job."""
        
        # Find relevant experiences
        experiences = personal_context.find_relevant_experiences(
            job_data['title'], job_data['description']
        )
        
        # Format experiences
        exp_text = self._format_experiences(experiences)
        
        # Fill template
        cover_letter = self.template.format(
            role=job_data['title'],
            company=job_data['company'],
            relevant_experience=exp_text,
            why_interested=f"I am particularly interested in {job_data['company']}'s work.",
            name="[Your Name]"
        )
        
        return cover_letter
```

## Quality Checks

### Basic Validation

Simple checks to ensure quality:

```python
class ApplicationQualityAssurance:
    """Basic quality checks for generated content."""
    
    def evaluate_application(self, resume, cover_letter, job_data):
        """Run basic quality checks."""
        
        checks = {
            'has_company_name': job_data['company'] in cover_letter,
            'has_role_title': job_data['title'] in resume,
            'reasonable_length': 100 < len(cover_letter.split()) < 500,
            'no_placeholders': '[' not in resume and '[' not in cover_letter
        }
        
        return checks
```

## Usage Examples

### Generate Resume

```python
# Initialize engine
engine = EnhancedTemplateEngine()

# Job data
job_data = {
    'title': 'Senior Product Manager',
    'company': 'Tech Company', 
    'description': 'Lead product development...'
}

# Generate resume
resume = engine.render_targeted_resume(job_data, your_application_kit)
```

### Generate Cover Letter

```python
# Initialize cover letter engine
cl_engine = CoverLetterEngine()

# Generate cover letter
cover_letter = cl_engine.generate_cover_letter(job_data, personal_context)

# Quality check
qa = ApplicationQualityAssurance()
checks = qa.evaluate_application(resume, cover_letter, job_data)
```

## Configuration

### Setting Up Your Content

1. Create your resume in markdown format
2. Add to `templates/resume.txt`
3. Include sections for experience, skills, projects
4. Run the parser to verify it works

### Customizing Templates

Edit the cover letter template in your config:
```yaml
cover_letter_template: |
  Your custom template here
  with {placeholders} for dynamic content
```

## Current Limitations

- Basic keyword matching (not semantic)
- Template-based generation (may sound generic)
- No A/B testing of different approaches
- Limited personalization depth
- Requires manual review and editing

## Best Practices

1. **Always Review Generated Content** - AI can make mistakes
2. **Customize Templates** - Add your voice and style
3. **Update Experience Database** - Keep your experiences current
4. **Test Different Keywords** - See what matches best
5. **Quality Over Quantity** - Better to send fewer, better applications

## Future Improvements

- Semantic matching using embeddings
- Multiple template variations
- Better company research integration
- Performance tracking
- User feedback incorporation

---

*This documentation describes the current state of the template engine. Features and performance may vary.*