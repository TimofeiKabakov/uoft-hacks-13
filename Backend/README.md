# Loan Assessment Backend

AI-powered loan assessment platform using multi-agent LLM system for evaluating small business loan applications.

## Features

- Multi-agent AI system for comprehensive loan assessment
- Real-time financial analysis via Plaid API integration
- Market viability analysis using Google Maps/Places API
- Automated risk scoring and eligibility determination
- RESTful API with async processing
- Encrypted storage of sensitive financial data

## Architecture

### Technology Stack

- **FastAPI** - High-performance async web framework
- **LangGraph** - Multi-agent workflow orchestration
- **Gemini Pro** - LLM-powered decision making
- **Plaid API** - Bank account and transaction data
- **Google Maps/Places** - Location and market research
- **SQLAlchemy** - Async ORM with SQLite
- **Pydantic** - Data validation and serialization
- **Cryptography** - Secure token encryption

### Multi-Agent System

1. **Financial Agent** - Analyzes banking data and calculates metrics
2. **Market Agent** - Evaluates business location and competition
3. **Decision Agent** - Synthesizes data and makes final assessment

## Quick Start

### Automated Setup

```bash
# Run the setup script (recommended)
./scripts/setup.sh
```

### Manual Setup

1. **Install Python 3.11+**
   ```bash
   python3 --version  # Verify installation
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Mac/Linux
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   python3 scripts/generate_encryption_key.py
   # Copy the generated key to .env
   ```

5. **Add API Keys to .env**
   ```
   GEMINI_API_KEY=your_gemini_api_key
   PLAID_CLIENT_ID=your_plaid_client_id
   PLAID_SECRET=your_plaid_secret
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   GOOGLE_PLACES_API_KEY=your_google_places_key
   ```

6. **Run the server**
   ```bash
   python3 app/main.py
   # Or: uvicorn app.main:app --reload
   ```

7. **Access API Documentation**
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Reference

### Endpoints

#### Create Application
```
POST /api/v1/applications
```

**Request Body:**
```json
{
  "job": "Coffee shop owner",
  "age": 32,
  "location": {
    "lat": 43.6532,
    "lng": -79.3832,
    "address": "123 Main St, Toronto"
  },
  "loan_amount": 50000.0,
  "loan_purpose": "Equipment purchase"
}
```

**Response:**
```json
{
  "application_id": "uuid",
  "status": "pending_plaid",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### Connect Plaid Account
```
POST /api/v1/applications/{application_id}/plaid-connect
```

**Request Body:**
```json
{
  "plaid_public_token": "public-sandbox-xxx"
}
```

**Response:**
```json
{
  "application_id": "uuid",
  "status": "processing",
  "plaid_connected": true
}
```

#### Get Application Status
```
GET /api/v1/applications/{application_id}/status
```

**Response:**
```json
{
  "application_id": "uuid",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00Z",
  "assessed_at": "2024-01-01T12:05:00Z",
  "has_results": true
}
```

#### Get Assessment Results
```
GET /api/v1/applications/{application_id}/assessment
```

**Response:**
```json
{
  "eligibility": "approved",
  "confidence_score": 85.5,
  "risk_level": "low",
  "reasoning": "Strong financial metrics...",
  "recommendations": ["Maintain current cash flow..."],
  "financial_metrics": {
    "monthly_income": 8500.0,
    "monthly_expenses": 5200.0,
    "debt_to_income_ratio": 15.5,
    "savings_rate": 38.8,
    "income_stability_score": 92.0
  },
  "market_analysis": {
    "competitor_count": 8,
    "market_density": "medium",
    "viability_score": 72.0,
    "market_insights": "Found 8 competitors..."
  },
  "assessed_at": "2024-01-01T12:05:00Z"
}
```

#### Health Check
```
GET /api/v1/health
```

## Development

### Running Tests

```bash
# Run all tests
python3 -m pytest

# Run with coverage
python3 -m pytest --cov=app tests/

# Run specific test file
python3 -m pytest tests/unit/test_schemas.py -v
```

### Project Structure

```
Backend/
├── app/
│   ├── agents/          # Multi-agent system
│   │   ├── graph.py     # LangGraph workflow
│   │   └── tools.py     # LangChain tools
│   ├── api/             # API routes
│   │   └── routes.py    # FastAPI endpoints
│   ├── core/            # Core utilities
│   │   ├── config.py    # Settings management
│   │   └── security.py  # Encryption
│   ├── database/        # Database layer
│   │   ├── models.py    # SQLAlchemy models
│   │   └── session.py   # DB session management
│   ├── models/          # Data models
│   │   └── schemas.py   # Pydantic schemas
│   ├── services/        # External services
│   │   ├── plaid_service.py
│   │   ├── google_service.py
│   │   └── financial_calculator.py
│   └── main.py          # FastAPI application
├── scripts/             # Utility scripts
│   ├── setup.sh
│   └── generate_encryption_key.py
├── tests/               # Test suite
│   └── unit/            # Unit tests
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── README.md
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `PLAID_CLIENT_ID` | Plaid client ID | Yes |
| `PLAID_SECRET` | Plaid secret key | Yes |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Yes |
| `GOOGLE_PLACES_API_KEY` | Google Places API key | Yes |
| `ENCRYPTION_KEY` | Fernet encryption key | Yes |
| `PLAID_ENV` | Plaid environment (sandbox/production) | No |
| `DATABASE_URL` | Database connection URL | No |
| `CORS_ORIGINS` | Allowed CORS origins | No |

## Security

- All Plaid access tokens are encrypted at rest using Fernet encryption
- API keys are loaded from environment variables only
- Never commit `.env` file to version control
- Use Plaid sandbox environment for development

## Obtaining API Keys

### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create or select a project
3. Generate API key

### Plaid API Credentials
1. Sign up at [Plaid Dashboard](https://dashboard.plaid.com/)
2. Get sandbox credentials from Keys section
3. For production, complete verification process

### Google Maps/Places API
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Maps and Places APIs
3. Create credentials (API Key)
4. Restrict key to Maps/Places APIs

## License

MIT

## Support

For issues and questions, please open a GitHub issue.
