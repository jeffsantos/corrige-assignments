# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

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

## Common Development Commands

### Most Important Command - Complete Processing

**This is the primary command for processing a turma:**

```bash
# Complete processing (correction + reports + thumbnails + CSV)
python -m src.main correct-all-with-visual --turma <turma-name>

# Process only one assignment
python -m src.main correct-all-with-visual --turma <turma-name> --assignment <assignment-name>

# Process specific submission
python -m src.main correct-all-with-visual --turma <turma-name> --assignment <assignment-name> --submissao <student-login>

# With detailed debug logs
python -m src.main correct-all-with-visual --turma <turma-name> --verbose
```

**What it does:**
1. Executes tests and AI analysis for all assignments
2. Generates reports in all formats (HTML/Markdown/JSON)
3. Creates visual reports with thumbnails (when applicable)
4. Exports results to CSV for analysis

### Other Correction Commands
```bash
# Basic correction - tests and AI analysis only
python -m src.main correct --assignment <assignment-name> --turma <turma-name>

# Correct specific submission
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --submissao <student-login>

# Correct with visual reports
python -m src.main correct --assignment <assignment-name> --turma <turma-name> --with-visual-reports
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

## Specification-Driven Development Workflow

This project uses a **specification-driven approach** for all new implementations, bug fixes, and refactorings. Before implementing any feature or change:

### Specification Files (specs/)

All new work items are documented in the `specs/` directory with the following structure:

**File Naming Convention:**
```
YYYYMMDD-NN-brief-description.md
```
- `YYYYMMDD` - Creation date (e.g., 20251018)
- `NN` - Sequential number for the day (01, 02, 03, etc.)
- `brief-description` - Short, hyphenated description

**File Content Structure:**
```markdown
Tarefa: [Complete Title of Implementation/Fix/Refactoring]

Descrição:

[Detailed description of what needs to be done, including:
- Context and motivation
- Specific requirements
- Files affected
- Expected outcomes
- Any relevant technical considerations]
```

### Development Workflow

1. **Read the specification** - Always start by reading the corresponding spec file in `specs/`
2. **Understand requirements** - Ensure full understanding of the task before implementation
3. **Implement systematically** - Follow the specification details precisely
4. **Update documentation** - Keep docs synchronized with code changes
5. **Reference the spec** - When committing, reference the spec file if applicable

**Important:** Specification files in `specs/` take precedence over ad-hoc requests. Always check for existing specs before starting work on a feature or fix.

## Documentation Standards

### Documentation Update Policy

**Rule:** Always verify and update documentation after any functional change.

After any change that affects functionality, interface, or system behavior, **always check** if these files need updates:

1. **`README.md`**:
   - New commands or options
   - Changes in usage examples
   - New features
   - Configuration changes
   - Troubleshooting updates

2. **`example_usage.py`**:
   - New usage examples
   - Updates to existing examples
   - Demonstration of new flags (e.g., `--verbose`)
   - New feature demonstrations

### Documentation Checklist

Execute this checklist after changes:

- [ ] **README.md**: New commands/options documented?
- [ ] **README.md**: Examples updated?
- [ ] **README.md**: Troubleshooting updated?
- [ ] **example_usage.py**: New examples added?
- [ ] **example_usage.py**: Existing examples updated?
- [ ] **example_usage.py**: New flags demonstrated?

### When to Update Documentation

**Always update when:**
- Adding new commands or options
- Changing CLI interface
- Adding new features
- Modifying configurations
- Fixing bugs that affect existing examples

**Skip updates when:**
- Only changing tests
- Internal refactoring that doesn't affect interface
- Bug fixes that don't change visible behavior
- Changes only in logs or debug output

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