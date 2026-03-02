# Agentic Research Paper Analyzer

A professional, microservice-ready backend for analyzing arXiv research papers using Multi-Agent AI (LangGraph + Google Gemini).

## Architecture

The system is built with a **Clean Architecture** approach:

- **`app/api`**: FastAPI endpoints (Interface Layer).
- **`app/core`**: Core business logic and workflow orchestration (LangGraph).
- **`app/agents`**: Specialized AI agents (Domain Logic).
- **`app/services`**: External services (arXiv scraping, Text Chunking).
- **`app/schemas`**: Pydantic models and State definitions (Data Layer).
- **`app/utils`**: Utilities (Token Management).

## Features

- **Multi-Agent Workflow**: Parallel execution of specialized agents (Consistency, Grammar, Novelty, Fact Check, Authenticity).
- **LangGraph Orchestration**: Robust state management and graph-based execution.
- **Token Management**: Automatic truncation to ensure LLM calls stay within the 16k token limit.
- **Structured Outputs**: All agents return strict JSON structured data using Pydantic models.
- **FastAPI Backend**: Ready-to-deploy REST API.
- **ArXiv Integration**: Automatic fetching and math-preserving markdown conversion.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Copy `.env.example` to `.env` and set your Google API Key:
   ```bash
   cp .env.example .env
   # Edit .env and set GOOGLE_API_KEY=...
   ```

3. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Usage

### Analyze a Paper

**Endpoint:** `POST /api/v1/analyze`

**Request:**
```json
{
  "paper_url": "https://arxiv.org/abs/2310.11511"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Analysis complete",
  "data": {
    "paper_metadata": { ... },
    "final_report": "# Research Paper Evaluation Report ...",
    "analyses": {
      "consistency": { ... },
      "grammar": { ... },
      ...
    }
  }
}
```

## Project Structure

```
backend/
├── app/
│   ├── agents/         # AI Agent implementations (Classes)
│   ├── api/            # API Routes
│   ├── core/           # Workflow definitions
│   ├── schemas/        # Pydantic models & State
│   ├── services/       # ArXiv & Chunking services
│   ├── utils/          # Token manager & helpers
│   └── main.py         # App entrypoint
├── legacy/             # Old procedural code (archived)
├── requirements.txt
└── README.md
```
