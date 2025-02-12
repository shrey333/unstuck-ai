# Backend

This is the backend service for the project, providing API endpoints for document processing and querying.

## Setup

1. Install dependencies:

```bash
poetry install
```

2. Set up environment variables:
   Copy `.env.example` to `.env` and configure the required variables.
3. Run the development server:

```bash
poetry run uvicorn src.main:app --reload
```

## Project Structure

- `src/`: Main application code
  - `api/`: API routes and handlers
  - `main.py`: Application entry point

## Development

This project uses Poetry for dependency management and packaging. Make sure to run tests and format code before committing:

```bash
poetry run pytest
poetry run black .
```
