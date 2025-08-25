# 📋 Complete Setup Guide

This guide will walk you through setting up CareerCompanion AI from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Google Cloud Setup](#google-cloud-setup)
5. [API Keys Setup](#api-keys-setup)
6. [Personalization](#personalization)
7. [First Run](#first-run)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Stable connection for web scraping

### Software Requirements
- **Python**: Version 3.8 or higher
- **Git**: For cloning the repository
- **Chrome/Chromium**: Required for Playwright

### Check Your Setup
```bash
# Check Python version
python3 --version  # Should show 3.8+

# Check pip
pip3 --version

# Check git
git --version
```

---

## Installation

### Step 1: Clone the Repository
```bash
# Clone via HTTPS
git clone https://github.com/manavpthaker/career-companion-ai.git

# Or clone via SSH (if you have SSH keys set up)
git clone [EMAIL]:manavpthaker/career-companion-ai.git

# Navigate to project directory
cd career-companion-ai
```

### Step 2: Run Setup Script
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (creates venv, installs dependencies)
./setup.sh
```

### Step 3: Manual Installation (if setup.sh fails)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps  # Install system dependencies
```

---

## Configuration

### Step 1: Create Your Configuration File
```bash
# Copy the example configuration
cp config/config.example.yaml config/job_search_config.yaml

# Edit with your preferences
nano config/job_search_config.yaml  # Or use your preferred editor
```

### Step 2: Key Configuration Sections

#### Job Titles
```yaml
job_titles:
  primary:
    - "Senior Product Manager"
    - "Director of Product"
    - "VP Product Management"
```

#### Location Preferences
```yaml
location:
  preferred:
    - "San Francisco, CA"
    - "Remote"
    - "Hybrid - Bay Area"
  home_base: "Berkeley, CA"  # Your actual location
```

#### Compensation
```yaml
compensation:
  minimum_base: 120000  # Your minimum
  target_base: 180000   # Your target
```

#### Company Preferences
```yaml
company_criteria:
  stage:
    required: ["Series C+", "Public Company"]
    avoid: ["Seed", "Series A"]
  industry_preference:
    tier1: ["FinTech", "Enterprise SaaS"]
    avoid: ["Crypto", "Gaming"]
```

---

## Google Cloud Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select existing project
3. Name it (e.g., "job-search-automation")

### Step 2: Enable Required APIs

1. In Cloud Console, go to "APIs & Services" > "Library"
2. Search and enable these APIs:
   - **Google Drive API**
   - **Google Sheets API**
   - **Google Docs API**

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure consent screen (if first time):
   - User type: External
   - App name: "Job Search Automation"
   - User support email: Your email
   - Developer contact: Your email
   - Add scopes:
     - `../auth/drive.file`
     - `../auth/spreadsheets`
     - `../auth/documents`
   - Add your email as test user

4. Create OAuth client:
   - Application type: "Desktop app"
   - Name: "Job Search CLI"
   - Download JSON file

5. Save credentials:
```bash
# Save the downloaded JSON as:
mv ~/Downloads/client_secret*.json config/google_credentials.json
```

### Step 4: First Authentication

```bash
# Test Google authentication
python test_google_auth.py

# Browser will open - sign in and grant permissions
# Token will be saved for future use
```

---

## API Keys Setup

### Option 1: Anthropic Claude (Recommended)

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Add to environment:

```bash
# Create .env file
cat > config/.env << EOF
ANTHROPIC_API_KEY=your_key_here
EOF
```

### Option 2: OpenAI GPT-4

1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Create API key
3. Add to environment:

```bash
# Add to .env file
echo "OPENAI_API_KEY=your_key_here" >> config/.env
```

### Option 3: Local LLM (No API needed)

```bash
# Install Ollama (for local models)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Configure in job_search_config.yaml
echo "llm_provider: ollama" >> config/job_search_config.yaml
```

---

## Personalization

### Step 1: Add Your Resume

```bash
# Copy your resume to templates
cp ~/path/to/your/resume.txt templates/resume.txt

# Or create from template
cp templates/resume.example.txt templates/resume.txt
nano templates/resume.txt
```

### Step 2: Customize Cover Letter Template

```bash
# Copy and edit cover letter template
cp templates/cover_letter.example.txt templates/cover_letter_template.txt
nano templates/cover_letter_template.txt
```

### Step 3: Add Target Companies

Edit `config/job_search_config.yaml`:

```yaml
job_boards:
  company_specific:
    - "https://careers.stripe.com"
    - "https://jobs.netflix.com"
    - "https://careers.google.com"
```

---

## First Run

### Step 1: Activate Environment
```bash
# Always activate venv first
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Test the System
```bash
# Check all APIs are working
python check_apis.py

# Run a test search (limited to 5 jobs)
python job_search_cli.py search --test --limit 5
```

### Step 3: Run Your First Real Search
```bash
# Run full pipeline
python job_search_cli.py search

# With specific parameters
python job_search_cli.py search --boards linkedin indeed --max 20
```

### Step 4: Review Applications
```bash
# Check generated applications
ls data/applications/

# View in Google Drive (URL will be displayed)
python job_search_cli.py status
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Playwright Browser Issues
```bash
# Error: Browser not found
playwright install chromium --with-deps

# On Linux, may need:
sudo apt-get install libnss3 libatk-bridge2.0-0
```

#### 2. Google Authentication Errors
```bash
# Delete token and re-authenticate
rm config/google_token.pickle
python test_google_auth.py
```

#### 3. Rate Limiting (429 errors)
```yaml
# Increase delays in config/job_search_config.yaml
rate_limits:
  pause_between_requests_seconds: 20  # Increase from 12
  requests_per_minute: 3  # Decrease from 5
```

#### 4. Import Errors
```bash
# Ensure venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### 5. Database Lock Errors
```bash
# Ensure only one instance running
pkill -f job_search_cli.py

# Reset database if corrupted
mv data/applications.db data/applications.db.backup
python job_search_cli.py init  # Recreate database
```

### Debug Mode
```bash
# Run with debug logging
python job_search_cli.py search --debug

# Check logs
tail -f logs/job_search_*.log
```

### Getting Help

1. Check logs: `logs/job_search_[timestamp].log`
2. Review config: Ensure all required fields are set
3. Test components individually:
   ```bash
   python -m agents.scraper_agent test
   python -m agents.filter_agent test
   ```
4. Open an issue: [GitHub Issues](https://github.com/[username]/job-search-automation/issues)

---

## Next Steps

### Daily Workflow
```bash
# Morning: Run search
python job_search_cli.py search

# Review in Google Sheets
# Make customizations as needed

# Evening: Check status
python job_search_cli.py status

# Weekly: Generate report
python scripts/track_progress.py dashboard
```

### Advanced Configuration

- **Custom Scoring**: Edit weights in `config/job_search_config.yaml`
- **Add Job Boards**: Extend `agents/scraper_agent.py`
- **Custom Templates**: Create multiple templates in `templates/`
- **Automation**: Set up cron job for daily runs

### Cron Setup (Optional)
```bash
# Edit crontab
crontab -e

# Add daily job search at 9 AM
0 9 * * * cd /path/to/job-search-automation && venv/bin/python job_search_cli.py search

# Add weekly report on Sundays
0 18 * * 0 cd /path/to/job-search-automation && venv/bin/python scripts/track_progress.py dashboard
```

---

## Security Best Practices

1. **Never commit credentials**:
   - Keep `.env` in `.gitignore`
   - Don't commit `google_credentials.json`
   - Use environment variables

2. **Rotate API keys regularly**:
   ```bash
   # Regenerate keys monthly
   # Update in config/.env
   ```

3. **Limit permissions**:
   - Google: Only grant necessary scopes
   - API keys: Set usage limits

4. **Secure your data**:
   ```bash
   # Encrypt sensitive data
   chmod 600 config/.env
   chmod 600 config/google_credentials.json
   ```

---

## Support

- 📧 **Email**: [[EMAIL]](mailto:[EMAIL])
- 💬 **Discord**: [Join our community](#)
- 🐛 **Issues**: [GitHub Issues](https://github.com/[username]/job-search-automation/issues)
- 📚 **Wiki**: [GitHub Wiki](https://github.com/[username]/job-search-automation/wiki)

---

*Happy job hunting! May your search be swift and your offers plentiful.* 🚀