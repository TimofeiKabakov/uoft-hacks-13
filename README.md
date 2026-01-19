<div align="center">

# Trajectory - AI-Powered Loan Assessment Platform

**Intelligent multi-agent system for small business loan eligibility assessment**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.1-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#features) • [Demo](#demo) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Overview

**Trajectory** is an intelligent loan assessment platform that leverages a multi-agent AI system to evaluate small business loan applications. By combining real-time financial data analysis, market viability research, and AI-powered risk assessment, Trajectory provides comprehensive, explainable loan decisions with personalized improvement recommendations.

### Key Highlights

- **Multi-Agent AI System** - Specialized AI agents work in parallel to analyze financial health, market conditions, and risk factors
- **Real-Time Financial Analysis** - Direct integration with Plaid API for instant banking data retrieval and analysis
- **Market Intelligence** - Google Maps/Places API integration for competitive landscape and location viability assessment
- **Personalized Recommendations** - AI-powered coach agent provides actionable insights to improve loan eligibility
- **Enterprise-Grade Security** - Encrypted token storage and secure data handling
- **High Performance** - Parallel agent execution reduces processing time by ~50%

---

## Features

### Core Capabilities

- **Multi-Step Application Wizard** - Intuitive guided flow for loan application submission
- **Real-Time Financial Analysis** - Automatic calculation of debt-to-income ratio, savings rate, income stability, and more
- **Market Research** - Competitive analysis and market density assessment based on business location
- **Risk Assessment** - AI-powered eligibility determination with confidence scoring
- **Personalized Recommendations** - Actionable insights and 30-day improvement plans
- **Interactive Dashboard** - Beautiful visualizations of financial metrics, trends, and recommendations
- **Evidence-Based Insights** - Detailed explanations for each recommendation with supporting data

### User Experience

- **Modern UI** - Built with Tailwind CSS and shadcn/ui components
- **Smooth Animations** - Framer Motion powered transitions and interactions
- **Responsive Design** - Fully optimized for desktop, tablet, and mobile devices
- **Dark Mode** - Complete theme support with seamless switching
- **Fast Performance** - Optimized React components and efficient state management

---

## Demo

<div align="center">

### Demo Video

[![Demo Video](https://img.shields.io/badge/Watch-Demo_Video-red?style=for-the-badge&logo=youtube)](YOUR_DEMO_VIDEO_URL_HERE)

</div>

### Screenshots

<div align="center">

#### Landing Page
![Landing Page](docs/images/landing-page.png)

#### Application Wizard
![Application Wizard](docs/images/application-wizard.png)

#### Dashboard & Results
![Dashboard](docs/images/dashboard.png)

#### Recommendations View
![Recommendations](docs/images/recommendations.png)

#### Financial Charts
![Financial Charts](docs/images/financial-charts.png)

</div>

---

## Architecture

### System Overview

Trajectory follows a modern microservices-inspired architecture with a clear separation between frontend and backend:

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Landing    │  │  Evaluation  │  │ Recommendations │   │
│  │    Page      │  │    Wizard     │  │    Dashboard    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────────┐
│              FastAPI Backend (Python)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Multi-Agent Orchestration Layer                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │  │
│  │  │  Financial    │  │    Market     │  │   Risk   │  │  │
│  │  │   Analyst     │  │  Researcher   │  │ Assessor │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │  │
│  │         │                │                │          │  │
│  │         └────────────────┴────────────────┘          │  │
│  │                        │                              │  │
│  │                  ┌─────▼─────┐                        │  │
│  │                  │   Coach   │                        │  │
│  │                  │   Agent   │                        │  │
│  │                  └───────────┘                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              External Services                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  Plaid   │  │  Google  │  │  Gemini  │          │  │
│  │  │   API    │  │   APIs   │  │   1.5    │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Database Layer (SQLite)                  │  │
│  │  Applications • Metrics • Assessments • Plans         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Agent Workflow

The system uses an **Orchestrator Pattern** with specialized AI agents:

1. **Financial Analyst Agent**
   - Retrieves banking data via Plaid API
   - Calculates comprehensive financial metrics
   - Identifies financial strengths and concerns

2. **Market Researcher Agent**
   - Analyzes business location using Google Maps/Places
   - Assesses competitive landscape and market density
   - Evaluates market viability and opportunities

3. **Risk Assessor Agent**
   - Synthesizes financial and market analysis
   - Applies business rules for risk validation
   - Generates final eligibility decision with confidence score

4. **Coach Agent**
   - Generates personalized recommendations
   - Creates actionable improvement plans
   - Provides evidence-based insights

**Performance Optimization**: Financial Analyst and Market Researcher run in **parallel**, reducing total processing time by approximately 50%.

---

## Tech Stack

### Backend

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | FastAPI | 0.109.0 |
| **Language** | Python | 3.11+ |
| **ORM** | SQLAlchemy | 2.0.25 (async) |
| **Database** | SQLite | (dev) / PostgreSQL (prod) |
| **AI/LLM** | Google Gemini | 1.5 Pro |
| **AI Framework** | LangChain | 0.1.4 |
| **Validation** | Pydantic | 2.5.3 |
| **Security** | Cryptography (Fernet) | 42.0.0 |
| **Testing** | pytest | 7.4.4 |

### Frontend

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | React | 18.3.1 |
| **Language** | TypeScript | 5.8.3 |
| **Build Tool** | Vite | 5.4.19 |
| **Styling** | Tailwind CSS | 3.4.17 |
| **UI Components** | shadcn/ui | Latest |
| **Animations** | Framer Motion | 12.26.2 |
| **State Management** | React Query | 5.83.0 |
| **Routing** | React Router | 6.30.1 |
| **Charts** | Recharts | 2.15.4 |
| **Forms** | React Hook Form | 7.61.1 |

### External APIs

- **Plaid API** - Banking data and transaction retrieval
- **Google Maps API** - Location services and geocoding
- **Google Places API** - Business search and market research
- **Google Gemini API** - LLM-powered analysis and recommendations

---

## Quick Start

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18+ and npm/yarn
- **API Keys**:
  - Google Gemini API key
  - Plaid API credentials (Client ID & Secret)
  - Google Maps API key
  - Google Places API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/uoft-hacks-13.git
   cd uoft-hacks-13/Backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   python3 scripts/generate_encryption_key.py
   # Copy the generated key to .env
   ```

5. **Add API keys to `.env`**
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   PLAID_CLIENT_ID=your_plaid_client_id
   PLAID_SECRET=your_plaid_secret
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   GOOGLE_PLACES_API_KEY=your_google_places_key
   ENCRYPTION_KEY=your_generated_encryption_key
   PLAID_ENV=sandbox
   DATABASE_URL=sqlite+aiosqlite:///./loan_assessment.db
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

6. **Run the backend server**
   ```bash
   python3 app/main.py
   # Or: uvicorn app.main:app --reload
   ```

   Backend will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../Front-End
   ```

2. **Install dependencies**
   ```bash
   npm install
   # Or: yarn install / bun install
   ```

3. **Configure environment**
   ```bash
   # Create .env file
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   ```

4. **Start development server**
   ```bash
   npm run dev
   # Or: yarn dev / bun dev
   ```

   Frontend will be available at `http://localhost:5173`

### Quick Test

1. Open `http://localhost:5173` in your browser
2. Navigate to the Evaluation page
3. Complete the application wizard
4. Connect a Plaid sandbox account
5. View your assessment results!

---

## Project Structure

```
uoft-hacks-13/
├── Backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── agents/            # Multi-agent AI system
│   │   │   ├── orchestrator/ # Orchestration logic
│   │   │   ├── financial_analyst/
│   │   │   ├── market_researcher/
│   │   │   ├── risk_assessor/
│   │   │   └── coach/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core utilities (config, security)
│   │   ├── database/          # Database models and session
│   │   ├── models/            # Pydantic schemas
│   │   ├── services/          # External service integrations
│   │   └── main.py            # FastAPI application entry
│   ├── tests/                 # Test suite
│   ├── scripts/                # Utility scripts
│   └── requirements.txt       # Python dependencies
│
├── Front-End/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── wizard/       # Application wizard steps
│   │   │   ├── results/      # Results display
│   │   │   ├── recommendations/ # Recommendations dashboard
│   │   │   └── ui/           # shadcn/ui components
│   │   ├── pages/            # Page components
│   │   ├── api/              # API client
│   │   ├── hooks/            # Custom React hooks
│   │   └── types/            # TypeScript types
│   ├── public/               # Static assets
│   └── package.json          # Node dependencies
│
└── README.md                  # This file
```

---

## API Documentation

### Core Endpoints

#### Create Application
```http
POST /api/v1/applications
Content-Type: application/json

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

#### Connect Plaid Account
```http
POST /api/v1/applications/{application_id}/plaid-connect
Content-Type: application/json

{
  "plaid_public_token": "public-sandbox-xxx"
}
```

#### Get Assessment Results
```http
GET /api/v1/applications/{application_id}/assessment
```

#### Get Recommendations
```http
GET /api/v1/applications/{application_id}/recommendations
```

### Interactive API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

For detailed API documentation, see [Backend/README.md](Backend/README.md).

---

## Development

### Backend Development

```bash
# Run tests
cd Backend
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black app/
ruff check app/

# Run specific test file
pytest tests/unit/test_api.py -v
```

### Frontend Development

```bash
# Run development server
cd Front-End
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Environment Variables

#### Backend (.env)
```env
# Required
GEMINI_API_KEY=your_key
PLAID_CLIENT_ID=your_id
PLAID_SECRET=your_secret
GOOGLE_MAPS_API_KEY=your_key
GOOGLE_PLACES_API_KEY=your_key
ENCRYPTION_KEY=your_key

# Optional
PLAID_ENV=sandbox
DATABASE_URL=sqlite+aiosqlite:///./loan_assessment.db
CORS_ORIGINS=http://localhost:5173
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Testing

### Backend Tests

```bash
cd Backend
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov=app tests/         # With coverage
pytest tests/unit/test_api.py   # Specific test file
```

**Test Coverage**: All major components are covered with unit tests:
- API endpoints
- Agent orchestration
- Financial calculations
- Service integrations
- Data validation

### Frontend Tests

```bash
cd Front-End
npm test              # Run tests
npm test:watch        # Watch mode
```

---

## Deployment

### Backend Deployment

1. **Set up production environment**
   ```bash
   export PLAID_ENV=production
   export DATABASE_URL=postgresql://user:pass@host/db
   ```

2. **Run migrations** (if using PostgreSQL)
   ```bash
   alembic upgrade head
   ```

3. **Start with production server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Deployment

1. **Build for production**
   ```bash
   npm run build
   ```

2. **Deploy `dist/` folder** to your hosting service:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - GitHub Pages

3. **Update API base URL** in production environment

---

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Write/update tests** for your changes
5. **Ensure all tests pass**
   ```bash
   # Backend
   cd Backend && pytest
   
   # Frontend
   cd Front-End && npm test
   ```
6. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
7. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

### Development Guidelines

- Follow existing code style and conventions
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure backward compatibility

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

### Getting Help

- **Documentation**: Check the [Backend README](Backend/README.md) and [Frontend README](Front-End/README.md)
- **Bug Reports**: Open an issue on [GitHub Issues](https://github.com/YOUR_USERNAME/uoft-hacks-13/issues)
- **Discussions**: Join our [GitHub Discussions](https://github.com/YOUR_USERNAME/uoft-hacks-13/discussions)
- **Email**: [YOUR_EMAIL@example.com](mailto:YOUR_EMAIL@example.com)

### Common Issues

**Backend won't start**
- Check that all API keys are set in `.env`
- Verify Python version is 3.11+
- Ensure all dependencies are installed

**Frontend can't connect to backend**
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings in backend
- Ensure backend is running on the correct port

**Plaid connection fails**
- Verify Plaid credentials are correct
- Check that `PLAID_ENV` matches your Plaid account
- Ensure you're using sandbox credentials for development

---

## Acknowledgments

- **Google Gemini** for powerful LLM capabilities
- **Plaid** for seamless banking data integration
- **Google Maps/Places** for location services
- **FastAPI** team for the excellent framework
- **React** and **Vite** communities
- **shadcn/ui** for beautiful components
- All contributors and open-source maintainers

---

<div align="center">

**Built for UofT Hacks 13**

[Back to Top](#trajectory---ai-powered-loan-assessment-platform)

</div>

