# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Run development server: `python run.py` or `flask run`
- Create database: `flask create-db`
- Create super user: `flask create-super-user`
- Production server: `gunicorn -w 4 -b 127.0.0.1:8000 "run:app"`
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
- Run tests: `python -m pytest`
- Single test: `python -m pytest tests/path/to/test.py::test_function_name`

## Code Style Guidelines
- Python: Follow PEP 8 guidelines
- Indentation: 4 spaces
- Line length: 88 characters max
- Quotes: Single quotes preferred
- Docstrings: Use triple double quotes
- Imports: Group stdlib, third-party, and local imports
- Flask: Use Blueprint architecture
- Models: Use SQLAlchemy ORM patterns
- Error handling: Use try/except with appropriate error logging
- Templates: Follow Jinja2 conventions
- Type hints: Use for function parameters and return values
- Variable names: Use snake_case for variables and functions