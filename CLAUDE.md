# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Main Correction Commands
```bash
# Main entry point - correct assignments using pytest-based tests and AI analysis
python -m src.main correct --assignment <assignment-name> --turma <turma-name>

# Correct specific submission (individual or group)
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --submissao <student-login-or-group-name>

# Correct all assignments for a turma
python -m src.main correct --turma <turma-name> --all-assignments

# Generate with visual reports (thumbnails for Streamlit/HTML)
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --with-visual-reports

# Complete processing (correction + visual reports + CSV export)
python -m src.main correct-all-with-visual --turma <turma-name>
```

### Environment Setup
```bash
# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Run basic tests (excludes integration, thumbnails, slow tests)
pipenv run pytest tests/ -m "not integration and not thumbnails and not slow"

# Run all tests including optional ones
pipenv run pytest tests/
```

### Report Commands
```bash
# Convert existing JSON reports to other formats
python -m src.main convert-report --assignment <assignment-name> --turma <turma-name> --format html
python -m src.main convert-latest --format markdown

# Export results to CSV
python -m src.main export-results --turma <turma-name> --all-assignments

# Generate visual reports without correction
python -m src.main generate-visual-report --assignment <assignment-name> --turma <turma-name>
python -m src.main generate-execution-visual-report --assignment <assignment-name> --turma <turma-name>
```

### Utility Commands
```bash
# List available assignments, turmas, and submissions
python -m src.main list-assignments
python -m src.main list-turmas
python -m src.main list-submissions --turma <turma-name>

# Debug mode for detailed logs
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --verbose
```

## Architecture Overview

### Core Components

**Services Layer** (`src/services/`):
- `correction_service.py` - Main orchestration service that coordinates test execution and AI analysis
- `ai_analyzer.py` - OpenAI GPT integration for code analysis with custom prompts
- `test_executor.py` - Pytest execution with JSON reporting using pytest-json-report
- `prompt_manager.py` - Manages custom AI prompts per assignment
- `streamlit_thumbnail_service.py` - Generates screenshots of Streamlit dashboards using Selenium
- `html_thumbnail_service.py` - Captures HTML page screenshots
- `python_execution_service.py` - Executes Python code and captures output
- `interactive_execution_service.py` - Handles assignments with command-line args and user inputs
- `csv_export_service.py` - Exports results to CSV format

**Domain Layer** (`src/domain/`):
- `models.py` - Core domain models including SubmissionType (INDIVIDUAL/GROUP), test results, AI analysis results

**Repositories** (`src/repositories/`):
- `assignment_repository.py` - Manages assignment definitions and configurations
- `submission_repository.py` - Handles student submission discovery and access

**Utils** (`src/utils/`):
- `report_generator.py` - Generates reports in multiple formats (HTML, Markdown, JSON, Console)
- `visual_report_generator.py` - Creates visual reports with thumbnails organized by grade

### Key Configuration Files

**`config.py`** - Central configuration including:
- Assignment submission types (individual vs group)
- Thumbnail generation settings for Streamlit/HTML assignments
- Interactive assignment configurations (command args, inputs, expected outputs)
- OpenAI API settings and timeouts

### Directory Structure

```
enunciados/           # Assignment definitions (not versioned)
├── assignment-name/
│   ├── README.md     # Assignment description
│   ├── tests/        # Pytest test files
│   └── *.py         # Base code provided to students

prompts/             # Custom AI prompts per assignment (versioned)
├── assignment-name/
│   └── prompt.txt   # Custom evaluation prompt

respostas/           # Student submissions
├── turma-name/
│   └── assignment-submissions/
│       └── student-name/ or group-name/

reports/             # Generated reports
├── *.json          # Raw correction data
├── *.html          # Interactive reports
├── visual/         # Visual reports with thumbnails
└── csv/           # CSV exports
```

### Test Execution System

The system uses **pytest with pytest-json-report** for structured test execution. Tests run directly in student submission directories without copying files. Test results include:
- Individual test status and timing
- Error messages and stack traces
- Overall pass/fail statistics

### AI Analysis System

AI analysis uses **OpenAI GPT models** with:
- **Custom prompts per assignment** from `prompts/{assignment-name}/prompt.txt`
- **Template-based fallbacks** for assignments without custom prompts
- **Assignment README integration** - automatically includes assignment descriptions
- **Structured output parsing** - extracts scores, comments, suggestions, and issues
- **Audit logging** - all AI interactions logged to `logs/` directory

### Multi-Type Assignment Support

**Submission Types**:
- Individual submissions: `{assignment-name}-{student-login}`
- Group submissions: `{assignment-name}-{group-name}`
- Configured per assignment in `config.py`

**Assignment Categories**:
- **Streamlit dashboards** - Generate thumbnails using Selenium + Chrome
- **HTML pages** - Capture static HTML screenshots
- **Python execution** - Capture STDOUT/STDERR from script execution
- **Interactive assignments** - Handle command-line arguments and user inputs

### Visual Reports System

Automatically generates visual reports with:
- **Thumbnail generation** for Streamlit apps and HTML pages using Selenium
- **Python execution capture** showing program outputs
- **Grade-based organization** with color-coded status indicators
- **High-resolution support** optimized for modern displays
- **Error handling** with automatic dependency installation for Streamlit

### Performance Optimizations

- **Parallel processing** for multiple submissions
- **Dependency caching** - Streamlit dependencies installed once per execution
- **Process cleanup** - Automatic removal of orphaned processes
- **Screenshot optimization** - Minimum heights and smart viewport sizing

## Git Commit Guidelines

When creating commits, follow the established commit standards in `docs/commit-standards.md`. For commit attribution:

**Commit Message Format:**
```bash
tipo(escopo): descrição

[corpo opcional]

Generated by Claude (https://claude.ai/code) sob a supervisão humana de <user.name> (<user.email>)
```

**Important:** Always use the configured git user.name and user.email for the attribution line. Retrieve these values using:
```bash
git config user.name
git config user.email
```