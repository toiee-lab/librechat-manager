# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
LibreChat User Management System (LFT) - A Flask web application for managing LibreChat user accounts in educational/workshop settings. The system allows administrators to create teacher accounts, and teachers to manage student accounts through a web interface.

## Build/Lint/Test Commands
- Run development server: `python run.py` or `flask run`
- Create database: `flask create-db`
- Create super user: `flask create-super-user`
- Production server: `gunicorn -w 4 -b 127.0.0.1:8000 "run:app"`
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
- Run tests: `python -m pytest`
- Single test: `python -m pytest tests/path/to/test.py::test_function_name`

## Architecture Overview

### Application Structure
- **Flask App Factory**: App initialization in `app/__init__.py`
- **Blueprint Architecture**: Routes organized by functionality
  - `auth.py`: Authentication routes
  - `super_user.py`: Admin functionality
  - `teacher.py`: Teacher functionality
  - `system.py`: System management
- **Service Layer**: Business logic separated in `app/services/`
- **Models**: SQLAlchemy models in `app/models/`

### User Hierarchy
- **SuperUser**: System administrators (manage teachers)
- **Teacher**: Instructors (manage students)
- **Student**: End users (managed by teachers)

### Key Components
- **LibreChatService**: Handles Docker command execution for LibreChat integration
- **CustomUserMixin**: Extended Flask-Login UserMixin for role-based authentication
- **SystemLog**: Comprehensive audit logging for all operations

### Database Models
- Uses SQLAlchemy ORM with SQLite3
- Student passwords stored unhashed for LibreChat integration
- All system operations logged in SystemLog table

### LibreChat Integration
- Executes Docker commands to create/delete LibreChat users
- Multiple command execution strategies for reliability
- Configurable container names and paths via environment variables
- Comprehensive error handling and logging

## Configuration
- Environment variables in `.env` file (copy from `.env.example`)
- Key settings: `LIBRECHAT_ROOT`, `LIBRECHAT_CONTAINER`, `DOCKER_PATH`
- Supports subpath deployment with `APPLICATION_ROOT`

## Security Features
- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Command injection prevention using shlex.quote
- Session management with Flask-Login
- Role-based access control

## Frontend
- TailwindCSS for styling (Apple-inspired design)
- Jinja2 templates with responsive design
- Custom CSS in `app/static/css/style.css`

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

## Docker で動作する LibreChat のユーザーを操作するためのコマンド

必ず、以下の形式を使うこと。これ以外の方法は、動かない。

- DOCKER_PAHT: dockerコマンドのパス。環境変数に格納。
- LIBRECHAT_CONTAINER: LibreChatが動作しているコンテナ名。環境変数に格納
- LIBRECHAT_WORK_DIR: docker内で package.json がある場所（カレントディレクトリか、親ディレクトリ）。環境変数に格納
### ユーザーの追加

```bash
DOCKER_PATH_PATH exec -it LIBRECHAT_CONTAINER /bin/sh -c "cd LIBRECHAT_WORK_DIR && echo y | npm run create-user <email> <username> <name> <password> --email-verified=true"
```

**実行結果サンプル:**
```
? Are you sure you want to create a user? (y/N) 
User created successfully:
  ID: 65e8f2b7a8c9d1e2f3g4h5i6
  Email: student@example.com
  Username: student001
  Name: Student User
  Email verified: true
  Created at: 2024-07-05T12:34:56.789Z
```

### ユーザーの削除

```bash
DOCKER_PATH exec -it LIBRECHAT_CONTAINER /bin/sh -c "cd LIBRECHAT_WORK_DIR && echo y | npm run delete-user <email>"
```

**実行結果サンプル:**
```
Found user: student@example.com
? Are you sure you want to delete this user? (y/N) 
User deleted successfully: student@example.com
```

### ユーザーの一覧

```bash
DOCKER_PATH exec -it LIBRECHAT_CONTAINER /bin/sh -c "cd LIBRECHAT_WORK_DIR && npm run list-users"
```

**実行結果サンプル:**
```
Total users: 3

ID                       | Email               | Username    | Name          | Verified | Created
65e8f2b7a8c9d1e2f3g4h5i6 | admin@example.com   | admin       | Admin User    | true     | 2024-07-01T10:00:00.000Z
65e8f2b7a8c9d1e2f3g4h5i7 | teacher@example.com | teacher001  | Teacher User  | true     | 2024-07-02T14:30:00.000Z
65e8f2b7a8c9d1e2f3g4h5i8 | student@example.com | student001  | Student User  | true     | 2024-07-05T12:34:56.789Z
```

### ユーザーのパスワード変更

```bash
DOCKER_PATH exec -it LIBRECHAT_CONTAINER /bin/sh -c "cd LIBRECHAT_WORK_DIR && npm run reset-password <email>"
```

**実行結果サンプル:**
```
Found user: student@example.com
Enter new password: 
Confirm new password: 
Password reset successfully for user: student@example.com
```
