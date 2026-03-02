# 🤖 Agentic Research Paper Analyzer

A production-ready multi-agent AI system for comprehensive analysis of arXiv research papers using **LangGraph** and **Google Gemini**. The system employs five specialized AI agents working in parallel to evaluate papers across multiple dimensions: consistency, grammar, novelty, fact-checking, and authenticity.

## 📺 Demo Video

A complete demonstration of the system is available at:
```
[demo/take-home demo.mov](https://drive.google.com/file/d/1Pe63PJfpb4wZZfiU2Cz7cBirp6cavbxj/view?usp=sharing)
```

The demo showcases:
- Interactive CLI with real-time streaming updates
- Multi-agent parallel execution
- Complete analysis workflow from paper fetching to report generation
- FastAPI REST API endpoints

---

## 🎯 Key Features

### Multi-Agent Architecture
- **5 Specialized Agents** running in parallel:
  - **Consistency Agent**: Validates logical coherence and argument flow
  - **Grammar Agent**: Evaluates writing quality and style
  - **Novelty Agent**: Assesses research originality and contributions
  - **Fact-Check Agent**: Verifies claims and citations
  - **Authenticity Agent**: Detects potential AI-generated content
- **Aggregator Agent**: Synthesizes findings into comprehensive reports

### LangGraph Orchestration
- Graph-based workflow with state management
- Checkpointing for fault tolerance and resumability
- Parallel agent execution for optimal performance
- Structured state transitions with type safety

### Production-Ready Features
- **FastAPI REST API** with OpenAPI documentation
- **Interactive CLI** with rich terminal UI and streaming updates
- **Token Management**: Automatic content truncation for LLM limits (16k tokens)
- **Structured Outputs**: Type-safe Pydantic models for all agent responses
- **ArXiv Integration**: Automatic paper fetching with math-preserving markdown conversion
- **Intelligent Chunking**: Section-based text processing with metadata extraction

---

## 🏗️ Architecture

The system follows **Clean Architecture** principles with clear separation of concerns:

```
backend/
├── app/
│   ├── agents/          # AI Agent implementations
│   │   ├── base.py              # Base agent class
│   │   ├── specialized.py       # 5 specialized agents
│   │   ├── aggregator.py        # Report aggregation agent
│   │   └── runner.py            # Agent execution logic
│   ├── api/             # FastAPI REST endpoints
│   │   └── endpoints.py         # Analysis API routes
│   ├── core/            # Business logic & orchestration
│   │   ├── config.py            # LLM configuration
│   │   └── workflow.py          # LangGraph workflow definition
│   ├── schemas/         # Data models & state definitions
│   │   ├── state.py             # Workflow state schema
│   │   └── responses.py         # API response models
│   ├── services/        # External integrations
│   │   ├── arxiv_service.py     # ArXiv paper fetching
│   │   └── chunking_service.py  # Text processing
│   ├── utils/           # Utilities
│   │   └── token_manager.py     # Token counting & truncation
│   ├── data/            # Generated data storage
│   └── main.py          # FastAPI application entry point
├── cli.py               # Interactive CLI interface
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
└── README.md            # Backend documentation
```

### Design Patterns

- **Strategy Pattern**: Pluggable agent implementations
- **State Pattern**: LangGraph state management
- **Factory Pattern**: Agent instantiation and configuration
- **Repository Pattern**: Data persistence layer
- **Dependency Injection**: Service composition

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google AI Studio API Key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AgenticAI - take home"
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

### Running the Application

#### Option 1: Interactive CLI (Recommended for first-time users)

```bash
python cli.py
```

Features:
- Rich terminal UI with colors and formatting
- Real-time streaming updates as agents complete
- Interactive prompts for paper URLs
- Automatic report preview and saving
- Continuous analysis mode

**CLI Usage:**
```bash
# Interactive mode
python cli.py

# With URL argument
python cli.py --url https://arxiv.org/abs/2310.11511
```

#### Option 2: REST API Server

```bash
uvicorn app.main:app --reload
```

Access the API:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Analysis Endpoint**: `POST /api/v1/analyze`

---

## 📡 API Reference

### Analyze Paper

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
    "paper_metadata": {
      "title": "Paper Title",
      "total_sections": 8,
      "total_word_count": 5432,
      "total_char_count": 32145
    },
    "final_report": "# Research Paper Evaluation Report\n\n...",
    "analyses": {
      "consistency": {
        "status": "Pass",
        "score": 8.5,
        "summary": "...",
        "details": "..."
      },
      "grammar": { ... },
      "novelty": { ... },
      "fact_check": { ... },
      "authenticity": { ... }
    }
  }
}
```

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

---

## 🧪 Example Usage

### CLI Example

```bash
$ python cli.py

🤖 RESEARCH PAPER ANALYSER
┌─────────────────────────────────────┐
│  Agentic AI System                  │
└─────────────────────────────────────┘

📝 Input Required
Please enter an arXiv paper URL or ID

Examples:
• https://arxiv.org/abs/2301.12345
• https://arxiv.org/pdf/2301.12345.pdf
• 2301.12345

arXiv URL or ID: 2310.11511

✅ Detected paper ID: 2310.11511
📥 Fetching paper from arXiv...
✅ Paper downloaded successfully
✂️ Processing paper sections...
✅ Paper chunked successfully

🚀 Starting agent analysis...

Multi-Agent Analysis Pipeline Starting...
  ✅ Consistency Analysis Completed (Score: 8.5)
  ✅ Grammar & Style Completed (Score: 9.0)
  ✅ Novelty Assessment Completed (Rating: High)
  ✅ Fact Verification Completed (Score: 8.0)
  ✅ Authenticity Check Completed (Score: 7.5)
  📊 Report Generation Compiling Report...

All agents completed.
✅ Report saved to: app/data/2310.11511_report_20260302_114530.md
```

### API Example (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"paper_url": "https://arxiv.org/abs/2310.11511"}'
```

### API Example (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"paper_url": "https://arxiv.org/abs/2310.11511"}
)

result = response.json()
print(result["data"]["final_report"])
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required
GOOGLE_API_KEY=your-google-ai-studio-api-key

# Optional (defaults shown)
LLM_MODEL=gemini-1.5-flash
LLM_TEMPERATURE=0.3
MAX_TOKENS=16000
```

### LLM Configuration

Modify `app/core/config.py` to adjust:
- Model selection (gemini-1.5-flash, gemini-1.5-pro)
- Temperature and creativity settings
- Token limits and truncation behavior
- Retry logic and timeout settings

---

## 📊 Agent Details

### 1. Consistency Agent
- **Purpose**: Validates logical flow and argument coherence
- **Output**: Score (0-10), status (Pass/Fail), detailed analysis
- **Criteria**: Logical structure, claim support, contradiction detection

### 2. Grammar Agent
- **Purpose**: Evaluates writing quality and academic style
- **Output**: Score (0-10), status, improvement suggestions
- **Criteria**: Grammar, clarity, academic tone, readability

### 3. Novelty Agent
- **Purpose**: Assesses research originality and contributions
- **Output**: Rating (Low/Medium/High), status, innovation analysis
- **Criteria**: Unique contributions, methodology innovation, impact potential

### 4. Fact-Check Agent
- **Purpose**: Verifies claims, citations, and data accuracy
- **Output**: Score (0-10), status, verification details
- **Criteria**: Citation accuracy, data validity, claim verification

### 5. Authenticity Agent
- **Purpose**: Detects potential AI-generated content
- **Output**: Score (0-10), status, authenticity indicators
- **Criteria**: Writing patterns, depth of analysis, human characteristics

### 6. Aggregator Agent
- **Purpose**: Synthesizes all analyses into comprehensive report
- **Output**: Markdown-formatted executive summary and detailed report
- **Includes**: Overall assessment, strengths, weaknesses, recommendations

---

## 🛠️ Technical Stack

- **Framework**: LangGraph (graph-based agent orchestration)
- **LLM**: Google Gemini 1.5 Flash via LangChain
- **API**: FastAPI with async support
- **CLI**: Rich (terminal UI) + Click (argument parsing)
- **Data Models**: Pydantic v2 with strict validation
- **Text Processing**: BeautifulSoup4, Markdownify
- **Token Management**: tiktoken (OpenAI tokenizer)

---

## 📁 Data Flow

1. **Input**: ArXiv paper URL or ID
2. **Fetching**: Download paper content via ArXiv API
3. **Conversion**: Convert PDF/HTML to markdown (preserving math)
4. **Chunking**: Split into sections with metadata extraction
5. **Token Management**: Truncate content to fit LLM limits
6. **Parallel Execution**: Run 5 specialized agents simultaneously
7. **Aggregation**: Combine results into unified report
8. **Output**: Structured JSON + Markdown report

---

## 🧩 Extending the System

### Adding a New Agent

1. Create agent class in `app/agents/specialized.py`:
```python
class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my_new_agent",
            system_prompt="Your specialized prompt here"
        )
    
    async def analyze(self, state: dict) -> dict:
        # Your analysis logic
        return {"my_new_agent": {"status": "Pass", ...}}
```

2. Add to workflow in `app/core/workflow.py`:
```python
workflow.add_node("my_new_agent", MyNewAgent().analyze)
workflow.add_edge("my_new_agent", "aggregator")
```

3. Update state schema in `app/schemas/state.py`

### Customizing Prompts

Edit system prompts in `app/agents/specialized.py` and `app/agents/aggregator.py` to adjust agent behavior and output format.

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `GOOGLE_API_KEY not found`
- **Solution**: Ensure `.env` file exists with valid API key

**Issue**: Token limit exceeded
- **Solution**: Adjust `MAX_TOKENS` in config or improve chunking strategy

**Issue**: ArXiv paper not found
- **Solution**: Verify paper ID is correct and paper exists on ArXiv

**Issue**: Slow analysis
- **Solution**: Use `gemini-1.5-flash` instead of `gemini-1.5-pro` for faster results

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📈 Performance

- **Average Analysis Time**: 30-60 seconds per paper
- **Token Usage**: ~10k-15k tokens per analysis
- **Concurrent Requests**: Supports multiple simultaneous analyses
- **Memory Usage**: ~200-500MB per analysis

---

## 🔒 Security Considerations

- API keys stored in `.env` (never committed to git)
- Input validation on all API endpoints
- Rate limiting recommended for production deployment
- CORS configured (update for production domains)

---

## 📝 License

This project is provided as-is for evaluation purposes.

---

## 🤝 Contributing

This is a take-home assignment project. For questions or issues, please contact the project maintainer.

---

## 🙏 Acknowledgments

- **LangGraph**: For powerful agent orchestration
- **Google Gemini**: For advanced LLM capabilities
- **ArXiv**: For open access to research papers
- **FastAPI**: For modern Python web framework
- **Rich**: For beautiful terminal interfaces

---

## 📞 Support

For issues or questions:
1. Check the demo video in `demo/take-home demo.mov`
2. Review API documentation at `/docs` endpoint
3. Examine example outputs in `backend/app/data/`

---

**Built with ❤️ using LangGraph and Google Gemini**
