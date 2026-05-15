# AI Worker

This is the Celery worker service for AI background tasks in the Gallery project.

## Virtual Environment Setup

**Mandatory**: You must use a local virtual environment (`.venv`) for this project.

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
This project relies on the root `.env` file for its configuration. 
If you need to override any variables locally, you can use the `.env.local` file in this directory.
