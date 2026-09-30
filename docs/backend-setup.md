
# RetainIQ Backend Setup Guide

## Overview

This document explains how to set up and run the RetainIQ backend.

**Backend Stack:**
- Python
- FastAPI
- Uvicorn
- Virtual Environment (venv)

## 1. Navigate to the Backend Directory

Run this command from the RetainIQ project root:

```bash
cd backend
```

## 2. Create a Virtual Environment

Run this command only when creating the environment for the first time:

```bash
python3 -m venv .venv
```

The `.venv` directory keeps project dependencies separate from other Python projects.

## 3. Activate the Virtual Environment

On macOS/Linux:

```bash
source .venv/bin/activate
```

After activation, your terminal should usually show `(.venv)`.

## 4. Install Project Dependencies

```bash
python -m pip install -r requirements.txt
```

This installs the packages listed in `requirements.txt`.

You normally need to run this after creating the environment or when project dependencies change.

## 5. Start the Backend Server

```bash
uvicorn app.main:app --reload
```

The `--reload` option automatically restarts the development server when you change Python code.

## 6. Verify the Backend

Open these URLs in your browser:

- Application: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs

The application must be running to access these pages.

## 7. Restart the Backend Later

When the virtual environment already exists, you do not need to create it again.

Open a terminal and run:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

If dependencies have changed, run this before starting the server:

```bash
python -m pip install -r requirements.txt
```

## 8. Stop the Backend

Press:

```text
Ctrl + C
```

in the terminal running Uvicorn.

To deactivate the virtual environment, run:

```bash
deactivate
```

## Important Notes

- Create `.venv` only once unless you need to recreate the environment.
- Activate `.venv` whenever you open a new terminal to work on the backend.
- Run backend commands from the `backend` directory.
- Keep `.venv` out of Git by adding it to `.gitignore`.
- Never commit passwords or secret keys to Git.