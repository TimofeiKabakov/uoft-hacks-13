# Community Spark

Community impact analysis and compliance monitoring platform built with FastAPI and LangGraph.

## Overview

Community Spark is an intelligent platform that analyzes community projects through automated auditing, impact assessment, and compliance monitoring. The system uses a multi-agent architecture orchestrated via LangGraph to provide comprehensive project analysis.

## Architecture

- **FastAPI**: REST API framework for serving endpoints
- **LangGraph**: Workflow orchestration for multi-agent processing
- **Agent System**: Specialized agents for different analysis tasks:
  - **Auditor**: Code quality, documentation, and security reviews
  - **Impact Analyst**: Community reach and social impact assessment
  - **Compliance Sentry**: Regulatory and policy compliance validation

## Project Structure

```
community-spark/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application entry point
│   ├── state.py             # LangGraph state schema
│   ├── graph.py             # LangGraph workflow definition
│   └── agents/
│       ├── __init__.py      # Agents package
│       ├── auditor.py       # Audit agent implementation
│       ├── impact_analyst.py # Impact analysis agent
│       └── compliance_sentry.py # Compliance checking agent
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore patterns
└── README.md               # This file
```

## Secrets Required

This project uses **1Password Secret References** for secure credential management. **Do not use `.env` files.**

Required secrets (set via 1Password):

- `OPENAI_API_KEY` - **Optional but recommended** for LLM-enhanced agent reasoning (uses GPT-4o-mini)
  - If not set, agents will use basic deterministic summaries
  - Get your key from: https://platform.openai.com/api-keys
- `PLAID_CLIENT_ID` - Required for Plaid integration
  - Get from: https://dashboard.plaid.com/team/keys (Sandbox)
- `PLAID_SECRET` - Required for Plaid integration
  - Get from: https://dashboard.plaid.com/team/keys (Sandbox)
- `PLAID_ENV` - Optional, defaults to "sandbox"
- `PASSKEY_HMAC_SECRET` - Required for WebAuthn token signing
  - Can be any secure random string for development

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. **Set up 1Password Secret References:**
   - Store your secrets in 1Password
   - Reference them using 1Password Secret References format
   - Use `op run` to inject secrets at runtime

4. Run the backend with 1Password:
```bash
cd community-spark
op run -- uvicorn app.main:app --reload
```

5. Run the Streamlit UI (in a separate terminal):
```bash
cd ..  # Back to repo root
op run -- streamlit run streamlit_app.py
```

**Important:** Always use `op run` to execute commands that require secrets. Never commit `.env` files or hardcode secrets.

## Visualization

Generate a visual diagram of the agent workflow:

```bash
cd community-spark
python scripts/render_graph.py
```

This creates `artifacts/graph.png` showing:
- Agent nodes (auditor, impact analyst, compliance sentry)
- Conditional routing logic (based on auditor_score)
- Decision flow from start to end

**Requirements:** Install graphviz system package if not already installed:
- macOS: `brew install graphviz`
- Ubuntu: `sudo apt-get install graphviz`
- Windows: Download from https://graphviz.org/download/

## User Interfaces

### Streamlit App (Recommended)
Modern web UI for loan evaluation:
- **URL:** http://localhost:8501
- Business profile form with instant evaluation
- Visual decision display with reasoning log
- Security transparency panel
- Passkey integration via /passkeys page

### API Endpoints (Backend)

#### Core Endpoints
- `GET /`: Root endpoint - API health check
- `GET /health`: Health check endpoint
- `GET /secrets-check`: Check if required secrets are configured (demo-only)
- `GET /passkeys`: WebAuthn passkey authentication page

#### Evaluation Endpoints
- `POST /evaluate`: Evaluate loan application with manual bank_data
- `POST /evaluate/plaid`: Evaluate loan application using Plaid transaction data
- `POST /finalize`: Finalize evaluation with passkey signature

#### WebAuthn Endpoints
- `POST /webauthn/register/options`: Generate registration options for new passkey
- `POST /webauthn/register/verify`: Verify and store new passkey credential
- `POST /webauthn/authenticate/options`: Generate authentication challenge
- `POST /webauthn/authenticate/verify`: Verify authentication and return token

## Development

### Running the Application

**Backend API:**
```bash
cd community-spark
op run -- uvicorn app.main:app --reload
```

**Streamlit UI:**
```bash
# From repo root
op run -- streamlit run streamlit_app.py
```

Open http://localhost:8501 for the Streamlit interface.

### Testing

Test the Plaid integration:
```bash
op run -- python test_plaid.py
```

Test the evaluation endpoint:
```bash
op run -- python test_plaid_endpoint.py
```

### Security Notes

- **Never commit `.env` files** - they are in `.gitignore`
- **Always use `op run`** to inject secrets at runtime
- Secrets are loaded from 1Password Secret References, not from files
- The application uses `python-dotenv` for compatibility but expects secrets via environment variables from `op run`

## License

[Add your license here]

