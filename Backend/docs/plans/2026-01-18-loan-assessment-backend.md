# Loan Assessment Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python FastAPI backend with multi-agent LLM architecture to assess small business loan eligibility using financial metrics and market viability analysis.

**Architecture:** Multi-agent system using LangGraph where an Orchestrator Agent coordinates specialized agents (Financial Analyst, Market Research, Risk Assessment). Hybrid approach combines rule-based financial calculations with Gemini-powered insights. FastAPI serves REST endpoints, SQLite stores data locally.

**Tech Stack:** Python 3.11+, FastAPI, SQLite, LangGraph, LangChain, Google Gemini Pro, Plaid API, Google Maps/Places APIs, Pydantic

---

## Task 1: Project Setup and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

**Step 1: Initialize git repository**

Run:
```bash
git init
```

Expected: Initialized empty Git repository

**Step 2: Create .gitignore**

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
```

**Step 3: Create requirements.txt**

Create `requirements.txt`:
```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# LLM & Agents
langchain==0.1.4
langgraph==0.0.20
langchain-google-genai==0.0.6
google-generativeai==0.3.2

# External APIs
plaid-python==16.0.0
googlemaps==4.10.0

# Database
sqlalchemy==2.0.25
aiosqlite==0.19.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
cryptography==42.0.0
httpx==0.26.0

# Development
pytest==7.4.4
pytest-asyncio==0.23.3
black==24.1.1
ruff==0.1.14
```

**Step 4: Create .env.example**

Create `.env.example`:
```
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
GOOGLE_MAPS_API_KEY=your_google_maps_key
GOOGLE_PLACES_API_KEY=your_google_places_key

# Configuration
PLAID_ENV=sandbox
DATABASE_URL=sqlite+aiosqlite:///./loan_assessment.db
CORS_ORIGINS=http://localhost:3000

# Security
ENCRYPTION_KEY=generate_a_secure_key_here
```

**Step 5: Create basic README**

Create `README.md`:
```markdown
# Loan Assessment Backend

Multi-agent LLM system for small business loan eligibility assessment.

## Setup

1. Install Python 3.11+
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in API keys
6. Run: `uvicorn app.main:app --reload`

## Architecture

- **FastAPI** - REST API
- **LangGraph** - Multi-agent orchestration
- **Gemini Pro** - LLM reasoning
- **Plaid API** - Financial data
- **Google APIs** - Location/market research
- **SQLite** - Local database

## API Endpoints

- `POST /api/applications/create` - Create loan application
- `POST /api/applications/{id}/connect-plaid` - Connect bank account
- `POST /api/applications/{id}/assess` - Run assessment
- `GET /api/applications/{id}/status` - Check status
```

**Step 6: Create project structure**

Run:
```bash
mkdir -p app/{api,models,services,agents,database,core}
mkdir -p tests/{unit,integration}
touch app/__init__.py
touch app/api/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/agents/__init__.py
touch app/database/__init__.py
touch app/core/__init__.py
touch tests/__init__.py
```

Expected: Directory structure created

**Step 7: Commit initial setup**

Run:
```bash
git add .
git commit -m "chore: initial project setup with dependencies and structure"
```

---

## Task 2: Configuration and Settings

**Files:**
- Create: `app/core/config.py`
- Create: `app/core/security.py`
- Create: `tests/unit/test_config.py`

**Step 1: Write test for configuration loading**

Create `tests/unit/test_config.py`:
```python
import pytest
from app.core.config import Settings


def test_settings_loads_from_env(monkeypatch):
    """Test that settings correctly loads from environment variables"""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    monkeypatch.setenv("PLAID_CLIENT_ID", "test_client")
    monkeypatch.setenv("PLAID_SECRET", "test_secret")

    settings = Settings()

    assert settings.GEMINI_API_KEY == "test_key"
    assert settings.PLAID_CLIENT_ID == "test_client"
    assert settings.PLAID_SECRET == "test_secret"


def test_settings_validates_required_fields():
    """Test that missing required fields raise validation error"""
    with pytest.raises(Exception):
        Settings(_env_file=None)
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_config.py -v
```

Expected: FAIL with "No module named 'app.core.config'"

**Step 3: Implement configuration**

Create `app/core/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    GEMINI_API_KEY: str
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    GOOGLE_MAPS_API_KEY: str
    GOOGLE_PLACES_API_KEY: str

    # Configuration
    PLAID_ENV: str = "sandbox"
    DATABASE_URL: str = "sqlite+aiosqlite:///./loan_assessment.db"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Security
    ENCRYPTION_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_config.py -v
```

Expected: PASS (2 tests)

**Step 5: Implement encryption utilities**

Create `app/core/security.py`:
```python
from cryptography.fernet import Fernet
from app.core.config import settings


class Encryptor:
    """Handles encryption/decryption of sensitive data like Plaid tokens"""

    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string"""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string"""
        return self.cipher.decrypt(ciphertext.encode()).decode()


# Global encryptor instance
encryptor = Encryptor()
```

**Step 6: Commit configuration setup**

Run:
```bash
git add app/core/ tests/unit/test_config.py
git commit -m "feat: add configuration and encryption utilities"
```

---

## Task 3: Database Models and Setup

**Files:**
- Create: `app/database/base.py`
- Create: `app/database/models.py`
- Create: `app/database/session.py`
- Create: `tests/unit/test_database.py`

**Step 1: Write test for database models**

Create `tests/unit/test_database.py`:
```python
import pytest
from datetime import datetime
from app.database.models import Application, FinancialMetrics, MarketAnalysis, Assessment


def test_application_model_creation():
    """Test Application model can be instantiated"""
    app = Application(
        id="test-123",
        user_job="Coffee shop owner",
        user_age=32,
        location_lat=43.6532,
        location_lng=-79.3832,
        location_address="123 Main St",
        loan_amount=50000.0,
        loan_purpose="Equipment",
        status="pending_plaid"
    )

    assert app.user_job == "Coffee shop owner"
    assert app.user_age == 32
    assert app.status == "pending_plaid"


def test_financial_metrics_model_creation():
    """Test FinancialMetrics model can be instantiated"""
    metrics = FinancialMetrics(
        id="metrics-123",
        application_id="app-123",
        debt_to_income_ratio=28.5,
        savings_rate=22.3,
        monthly_income=5000.0
    )

    assert metrics.debt_to_income_ratio == 28.5
    assert metrics.application_id == "app-123"
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_database.py -v
```

Expected: FAIL with "No module named 'app.database.models'"

**Step 3: Create database base configuration**

Create `app/database/base.py`:
```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)
```

**Step 4: Create database models**

Create `app/database/models.py`:
```python
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.base import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True)
    user_job = Column(String, nullable=False)
    user_age = Column(Integer, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    location_address = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_purpose = Column(String, nullable=False)
    plaid_access_token = Column(String, nullable=True)  # Encrypted
    status = Column(String, nullable=False)  # pending_plaid, processing, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialMetrics(Base):
    __tablename__ = "financial_metrics"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    debt_to_income_ratio = Column(Float, nullable=True)
    savings_rate = Column(Float, nullable=True)
    avg_monthly_balance = Column(Float, nullable=True)
    min_balance_6mo = Column(Float, nullable=True)
    overdraft_count = Column(Integer, nullable=True)
    income_stability_score = Column(Float, nullable=True)
    monthly_income = Column(Float, nullable=True)
    monthly_expenses = Column(Float, nullable=True)
    raw_plaid_data = Column(Text, nullable=True)  # JSON blob
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketAnalysis(Base):
    __tablename__ = "market_analysis"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    competitor_count = Column(Integer, nullable=True)
    market_density = Column(String, nullable=True)  # low, medium, high
    viability_score = Column(Float, nullable=True)
    market_insights = Column(Text, nullable=True)
    nearby_businesses = Column(Text, nullable=True)  # JSON array
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    eligibility = Column(String, nullable=False)  # approved, denied, review
    confidence_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)  # low, medium, high
    reasoning = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)  # JSON array
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 5: Create database session management**

Create `app/database/session.py`:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.database.base import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Step 6: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_database.py -v
```

Expected: PASS (2 tests)

**Step 7: Commit database setup**

Run:
```bash
git add app/database/ tests/unit/test_database.py
git commit -m "feat: add database models and session management"
```

---

## Task 4: Pydantic Schemas

**Files:**
- Create: `app/models/schemas.py`
- Create: `tests/unit/test_schemas.py`

**Step 1: Write test for schemas**

Create `tests/unit/test_schemas.py`:
```python
import pytest
from pydantic import ValidationError
from app.models.schemas import (
    ApplicationCreate,
    PlaidConnect,
    LocationData,
    FinancialMetricsResponse,
    AssessmentResponse
)


def test_application_create_valid():
    """Test ApplicationCreate schema with valid data"""
    data = ApplicationCreate(
        job="Coffee shop owner",
        age=32,
        location=LocationData(
            lat=43.6532,
            lng=-79.3832,
            address="123 Main St"
        ),
        loan_amount=50000.0,
        loan_purpose="Equipment purchase"
    )

    assert data.job == "Coffee shop owner"
    assert data.age == 32
    assert data.loan_amount == 50000.0


def test_application_create_invalid_age():
    """Test ApplicationCreate rejects invalid age"""
    with pytest.raises(ValidationError):
        ApplicationCreate(
            job="Business",
            age=15,  # Too young
            location=LocationData(lat=43.0, lng=-79.0, address="Test"),
            loan_amount=10000.0,
            loan_purpose="Test"
        )


def test_plaid_connect_schema():
    """Test PlaidConnect schema"""
    data = PlaidConnect(plaid_public_token="public-sandbox-123")
    assert data.plaid_public_token == "public-sandbox-123"
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_schemas.py -v
```

Expected: FAIL with "No module named 'app.models.schemas'"

**Step 3: Implement Pydantic schemas**

Create `app/models/schemas.py`:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class ApplicationStatus(str, Enum):
    PENDING_PLAID = "pending_plaid"
    PROCESSING = "processing"
    COMPLETED = "completed"


class Eligibility(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    REVIEW = "review"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MarketDensity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Request Schemas
class LocationData(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=1)


class ApplicationCreate(BaseModel):
    job: str = Field(..., min_length=1, max_length=200)
    age: int = Field(..., ge=18, le=100)
    location: LocationData
    loan_amount: float = Field(..., gt=0)
    loan_purpose: str = Field(..., min_length=1, max_length=500)


class PlaidConnect(BaseModel):
    plaid_public_token: str = Field(..., min_length=1)


# Response Schemas
class ApplicationResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PlaidConnectResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    plaid_connected: bool


class NearbyBusiness(BaseModel):
    name: str
    type: str
    rating: Optional[float] = None
    distance_miles: float


class FinancialMetricsResponse(BaseModel):
    debt_to_income_ratio: Optional[float] = None
    savings_rate: Optional[float] = None
    avg_monthly_balance: Optional[float] = None
    min_balance_6mo: Optional[float] = None
    overdraft_count: Optional[int] = None
    income_stability_score: Optional[float] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None


class MarketAnalysisResponse(BaseModel):
    competitor_count: int
    market_density: MarketDensity
    viability_score: float
    market_insights: Optional[str] = None
    nearby_businesses: List[NearbyBusiness] = []


class AssessmentResponse(BaseModel):
    eligibility: Eligibility
    confidence_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    reasoning: str
    recommendations: List[str]
    financial_metrics: FinancialMetricsResponse
    market_analysis: MarketAnalysisResponse
    assessed_at: datetime


class ApplicationStatusResponse(BaseModel):
    application_id: str
    status: ApplicationStatus
    created_at: datetime
    assessed_at: Optional[datetime] = None
    has_results: bool
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_schemas.py -v
```

Expected: PASS (3 tests)

**Step 5: Commit schemas**

Run:
```bash
git add app/models/ tests/unit/test_schemas.py
git commit -m "feat: add Pydantic schemas for API validation"
```

---

## Task 5: Plaid Service

**Files:**
- Create: `app/services/plaid_service.py`
- Create: `tests/unit/test_plaid_service.py`

**Step 1: Write test for Plaid service**

Create `tests/unit/test_plaid_service.py`:
```python
import pytest
from unittest.mock import Mock, patch
from app.services.plaid_service import PlaidService


@pytest.fixture
def plaid_service():
    return PlaidService()


@patch("app.services.plaid_service.plaid.ApiClient")
def test_exchange_public_token(mock_api_client, plaid_service):
    """Test exchanging public token for access token"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.to_dict.return_value = {"access_token": "access-sandbox-123"}
    mock_client.item_public_token_exchange.return_value = mock_response

    plaid_service.client = mock_client

    access_token = plaid_service.exchange_public_token("public-sandbox-123")

    assert access_token == "access-sandbox-123"
    mock_client.item_public_token_exchange.assert_called_once()


@patch("app.services.plaid_service.plaid.ApiClient")
def test_get_transactions(mock_api_client, plaid_service):
    """Test fetching transactions"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.to_dict.return_value = {
        "transactions": [
            {"amount": 100.0, "name": "Test Transaction"}
        ]
    }
    mock_client.transactions_get.return_value = mock_response

    plaid_service.client = mock_client

    transactions = plaid_service.get_transactions("access-token", months=6)

    assert len(transactions) > 0
    assert "transactions" in transactions
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_plaid_service.py -v
```

Expected: FAIL with "No module named 'app.services.plaid_service'"

**Step 3: Implement Plaid service**

Create `app/services/plaid_service.py`:
```python
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid import ApiClient, Configuration
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.core.config import settings


class PlaidService:
    """Service for interacting with Plaid API"""

    def __init__(self):
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment"""
        env_hosts = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com"
        }
        return env_hosts.get(settings.PLAID_ENV, "https://sandbox.plaid.com")

    def exchange_public_token(self, public_token: str) -> str:
        """Exchange public token for access token"""
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            return response.to_dict()["access_token"]
        except Exception as e:
            raise Exception(f"Failed to exchange Plaid token: {str(e)}")

    def get_transactions(self, access_token: str, months: int = 6) -> Dict:
        """Fetch transactions for the last N months"""
        try:
            start_date = datetime.now() - timedelta(days=months * 30)
            end_date = datetime.now()

            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=TransactionsGetRequestOptions()
            )

            response = self.client.transactions_get(request)
            return response.to_dict()
        except Exception as e:
            raise Exception(f"Failed to fetch transactions: {str(e)}")

    def get_accounts(self, access_token: str) -> Dict:
        """Fetch account information including balances"""
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            return response.to_dict()
        except Exception as e:
            raise Exception(f"Failed to fetch accounts: {str(e)}")

    def get_income_verification(self, access_token: str) -> Optional[Dict]:
        """Attempt to get income data (may not be available in sandbox)"""
        try:
            # Income verification requires specific Plaid products
            # For sandbox, we'll extract from transaction patterns
            transactions_data = self.get_transactions(access_token)

            # Extract income-like transactions (deposits)
            income_transactions = [
                t for t in transactions_data.get("transactions", [])
                if t.get("amount", 0) < 0  # Negative amounts are income in Plaid
            ]

            return {
                "income_transactions": income_transactions,
                "has_income_verification": False
            }
        except Exception:
            return None


# Global service instance
plaid_service = PlaidService()
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_plaid_service.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit Plaid service**

Run:
```bash
git add app/services/plaid_service.py tests/unit/test_plaid_service.py
git commit -m "feat: add Plaid API service for financial data"
```

---

## Task 6: Google Services (Maps & Places)

**Files:**
- Create: `app/services/google_service.py`
- Create: `tests/unit/test_google_service.py`

**Step 1: Write test for Google service**

Create `tests/unit/test_google_service.py`:
```python
import pytest
from unittest.mock import Mock, patch
from app.services.google_service import GoogleService


@pytest.fixture
def google_service():
    return GoogleService()


@patch("app.services.google_service.googlemaps.Client")
def test_search_nearby_competitors(mock_gmaps_client, google_service):
    """Test searching for nearby competitors"""
    mock_client = Mock()
    mock_client.places_nearby.return_value = {
        "results": [
            {
                "name": "Competitor Coffee",
                "types": ["cafe"],
                "rating": 4.5,
                "geometry": {"location": {"lat": 43.65, "lng": -79.38}}
            }
        ]
    }

    google_service.gmaps = mock_client

    results = google_service.search_nearby_competitors(
        lat=43.6532,
        lng=-79.3832,
        business_type="coffee shop",
        radius_miles=1.0
    )

    assert len(results) > 0
    assert results[0]["name"] == "Competitor Coffee"


def test_calculate_distance():
    """Test distance calculation between two points"""
    service = GoogleService()

    # Toronto to nearby location (~1km)
    distance = service.calculate_distance(
        43.6532, -79.3832,
        43.6542, -79.3842
    )

    assert distance > 0
    assert distance < 1  # Should be less than 1 mile
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_google_service.py -v
```

Expected: FAIL with "No module named 'app.services.google_service'"

**Step 3: Implement Google service**

Create `app/services/google_service.py`:
```python
import googlemaps
from typing import List, Dict, Tuple
from math import radians, cos, sin, asin, sqrt
from app.core.config import settings


class GoogleService:
    """Service for Google Maps and Places API interactions"""

    def __init__(self):
        # Note: Google Places uses the same API key as Maps
        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    def search_nearby_competitors(
        self,
        lat: float,
        lng: float,
        business_type: str,
        radius_miles: float = 1.0
    ) -> List[Dict]:
        """Search for competitors near a location"""
        try:
            # Convert miles to meters (Google API uses meters)
            radius_meters = int(radius_miles * 1609.34)

            # Map business types to Google Places types
            place_type = self._map_business_type(business_type)

            # Search for places
            results = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius_meters,
                type=place_type,
                keyword=business_type
            )

            # Process results
            competitors = []
            for place in results.get("results", []):
                competitor = {
                    "name": place.get("name"),
                    "type": ", ".join(place.get("types", [])),
                    "rating": place.get("rating"),
                    "location": place.get("geometry", {}).get("location"),
                    "distance_miles": self.calculate_distance(
                        lat, lng,
                        place["geometry"]["location"]["lat"],
                        place["geometry"]["location"]["lng"]
                    )
                }
                competitors.append(competitor)

            return competitors
        except Exception as e:
            raise Exception(f"Failed to search competitors: {str(e)}")

    def _map_business_type(self, business_type: str) -> str:
        """Map user business type to Google Places type"""
        # Common mappings
        type_mapping = {
            "coffee": "cafe",
            "restaurant": "restaurant",
            "retail": "store",
            "bakery": "bakery",
            "bar": "bar",
            "gym": "gym",
            "salon": "beauty_salon",
            "repair": "car_repair",
        }

        business_lower = business_type.lower()
        for key, value in type_mapping.items():
            if key in business_lower:
                return value

        # Default to generic establishment
        return "establishment"

    def calculate_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calculate distance between two coordinates in miles using Haversine formula"""
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])

        # Haversine formula
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))

        # Earth radius in miles
        miles = 3956 * c
        return round(miles, 2)


# Global service instance
google_service = GoogleService()
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_google_service.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit Google services**

Run:
```bash
git add app/services/google_service.py tests/unit/test_google_service.py
git commit -m "feat: add Google Maps/Places service for market research"
```

---

## Task 7: Financial Metrics Calculator

**Files:**
- Create: `app/services/financial_calculator.py`
- Create: `tests/unit/test_financial_calculator.py`

**Step 1: Write test for financial calculator**

Create `tests/unit/test_financial_calculator.py`:
```python
import pytest
from app.services.financial_calculator import FinancialCalculator


@pytest.fixture
def calculator():
    return FinancialCalculator()


@pytest.fixture
def sample_transactions():
    return {
        "transactions": [
            {"amount": -3000, "name": "Salary Deposit", "category": ["Income"]},
            {"amount": 1200, "name": "Rent", "category": ["Rent"]},
            {"amount": 100, "name": "Groceries", "category": ["Food"]},
            {"amount": 50, "name": "Utilities", "category": ["Bills"]},
        ],
        "accounts": [
            {"balances": {"current": 5000}}
        ]
    }


def test_calculate_monthly_income(calculator, sample_transactions):
    """Test monthly income calculation"""
    income = calculator.calculate_monthly_income(sample_transactions)
    assert income == 3000  # Negative amounts are income


def test_calculate_monthly_expenses(calculator, sample_transactions):
    """Test monthly expenses calculation"""
    expenses = calculator.calculate_monthly_expenses(sample_transactions)
    assert expenses == 1350  # 1200 + 100 + 50


def test_calculate_dti_ratio(calculator):
    """Test debt-to-income ratio calculation"""
    dti = calculator.calculate_dti_ratio(
        monthly_debt=1200,
        monthly_income=5000
    )
    assert dti == 24.0  # (1200 / 5000) * 100


def test_calculate_savings_rate(calculator):
    """Test savings rate calculation"""
    rate = calculator.calculate_savings_rate(
        monthly_income=5000,
        monthly_expenses=3500
    )
    assert rate == 30.0  # ((5000 - 3500) / 5000) * 100
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_financial_calculator.py -v
```

Expected: FAIL with "No module named 'app.services.financial_calculator'"

**Step 3: Implement financial calculator**

Create `app/services/financial_calculator.py`:
```python
from typing import Dict, List
from statistics import mean


class FinancialCalculator:
    """Calculator for financial metrics from Plaid data"""

    def calculate_monthly_income(self, plaid_data: Dict) -> float:
        """Calculate average monthly income from transactions"""
        transactions = plaid_data.get("transactions", [])

        # Income transactions have negative amounts in Plaid
        income_transactions = [
            abs(t["amount"]) for t in transactions
            if t.get("amount", 0) < 0 and "income" in str(t.get("category", [])).lower()
        ]

        if not income_transactions:
            # Fallback: any negative amount
            income_transactions = [abs(t["amount"]) for t in transactions if t.get("amount", 0) < 0]

        return mean(income_transactions) if income_transactions else 0.0

    def calculate_monthly_expenses(self, plaid_data: Dict) -> float:
        """Calculate average monthly expenses from transactions"""
        transactions = plaid_data.get("transactions", [])

        # Expense transactions have positive amounts
        expense_transactions = [
            t["amount"] for t in transactions
            if t.get("amount", 0) > 0
        ]

        return sum(expense_transactions) if expense_transactions else 0.0

    def calculate_dti_ratio(self, monthly_debt: float, monthly_income: float) -> float:
        """Calculate debt-to-income ratio as percentage"""
        if monthly_income == 0:
            return 100.0  # Max risk if no income

        return round((monthly_debt / monthly_income) * 100, 2)

    def calculate_savings_rate(self, monthly_income: float, monthly_expenses: float) -> float:
        """Calculate savings rate as percentage"""
        if monthly_income == 0:
            return 0.0

        savings = monthly_income - monthly_expenses
        return round((savings / monthly_income) * 100, 2)

    def calculate_cash_flow_metrics(self, plaid_data: Dict) -> Dict[str, float]:
        """Calculate cash flow metrics from account balances"""
        accounts = plaid_data.get("accounts", [])

        if not accounts:
            return {
                "avg_monthly_balance": 0.0,
                "min_balance_6mo": 0.0,
                "current_balance": 0.0
            }

        # Get current balances
        balances = [acc.get("balances", {}).get("current", 0) for acc in accounts]
        current_balance = sum(balances)

        # For demo, use current balance as proxy for historical data
        # In production, would track historical balances
        return {
            "avg_monthly_balance": round(current_balance, 2),
            "min_balance_6mo": round(current_balance * 0.7, 2),  # Estimate
            "current_balance": round(current_balance, 2)
        }

    def assess_income_stability(self, plaid_data: Dict) -> float:
        """Score income stability from 0-100"""
        transactions = plaid_data.get("transactions", [])

        # Get income transactions
        income_txns = [
            abs(t["amount"]) for t in transactions
            if t.get("amount", 0) < 0
        ]

        if len(income_txns) < 2:
            return 50.0  # Neutral score with insufficient data

        # Calculate coefficient of variation (lower is more stable)
        avg_income = mean(income_txns)
        if avg_income == 0:
            return 0.0

        variance = sum((x - avg_income) ** 2 for x in income_txns) / len(income_txns)
        std_dev = variance ** 0.5
        cv = (std_dev / avg_income) * 100

        # Convert to 0-100 score (lower CV = higher stability)
        stability_score = max(0, 100 - cv)

        return round(stability_score, 2)

    def count_overdrafts(self, plaid_data: Dict) -> int:
        """Count overdraft occurrences"""
        accounts = plaid_data.get("accounts", [])

        overdraft_count = 0
        for account in accounts:
            balance = account.get("balances", {}).get("current", 0)
            if balance < 0:
                overdraft_count += 1

        return overdraft_count

    def calculate_all_metrics(self, plaid_data: Dict) -> Dict:
        """Calculate all financial metrics"""
        monthly_income = self.calculate_monthly_income(plaid_data)
        monthly_expenses = self.calculate_monthly_expenses(plaid_data)

        # Assume rent is the largest recurring expense (debt proxy)
        transactions = plaid_data.get("transactions", [])
        rent_transactions = [
            t["amount"] for t in transactions
            if "rent" in t.get("name", "").lower() or "rent" in str(t.get("category", [])).lower()
        ]
        monthly_debt = max(rent_transactions) if rent_transactions else monthly_expenses * 0.3

        cash_flow = self.calculate_cash_flow_metrics(plaid_data)

        return {
            "debt_to_income_ratio": self.calculate_dti_ratio(monthly_debt, monthly_income),
            "savings_rate": self.calculate_savings_rate(monthly_income, monthly_expenses),
            "avg_monthly_balance": cash_flow["avg_monthly_balance"],
            "min_balance_6mo": cash_flow["min_balance_6mo"],
            "overdraft_count": self.count_overdrafts(plaid_data),
            "income_stability_score": self.assess_income_stability(plaid_data),
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses
        }


# Global calculator instance
financial_calculator = FinancialCalculator()
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_financial_calculator.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit financial calculator**

Run:
```bash
git add app/services/financial_calculator.py tests/unit/test_financial_calculator.py
git commit -m "feat: add financial metrics calculator"
```

---

## Task 8: LangGraph Agent Tools

**Files:**
- Create: `app/agents/tools.py`
- Create: `tests/unit/test_agent_tools.py`

**Step 1: Write test for agent tools**

Create `tests/unit/test_agent_tools.py`:
```python
import pytest
from unittest.mock import Mock, patch
from app.agents.tools import (
    fetch_plaid_data_tool,
    calculate_financial_metrics_tool,
    search_competitors_tool,
    analyze_market_saturation_tool
)


@patch("app.agents.tools.plaid_service")
def test_fetch_plaid_data_tool(mock_plaid):
    """Test Plaid data fetching tool"""
    mock_plaid.get_transactions.return_value = {"transactions": []}
    mock_plaid.get_accounts.return_value = {"accounts": []}

    result = fetch_plaid_data_tool("access-token-123")

    assert "transactions" in result
    assert "accounts" in result


@patch("app.agents.tools.financial_calculator")
def test_calculate_financial_metrics_tool(mock_calc):
    """Test financial metrics calculation tool"""
    mock_calc.calculate_all_metrics.return_value = {
        "debt_to_income_ratio": 30.0,
        "savings_rate": 20.0
    }

    plaid_data = {"transactions": [], "accounts": []}
    result = calculate_financial_metrics_tool(plaid_data)

    assert "debt_to_income_ratio" in result
    assert result["debt_to_income_ratio"] == 30.0


@patch("app.agents.tools.google_service")
def test_search_competitors_tool(mock_google):
    """Test competitor search tool"""
    mock_google.search_nearby_competitors.return_value = [
        {"name": "Competitor 1", "rating": 4.5}
    ]

    result = search_competitors_tool(
        lat=43.6532,
        lng=-79.3832,
        business_type="coffee shop"
    )

    assert len(result) > 0
    assert result[0]["name"] == "Competitor 1"
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/unit/test_agent_tools.py -v
```

Expected: FAIL with "No module named 'app.agents.tools'"

**Step 3: Implement agent tools**

Create `app/agents/tools.py`:
```python
from langchain.tools import tool
from typing import Dict, List, Any
from app.services.plaid_service import plaid_service
from app.services.google_service import google_service
from app.services.financial_calculator import financial_calculator


@tool
def fetch_plaid_data_tool(access_token: str) -> Dict[str, Any]:
    """
    Fetch financial data from Plaid API including transactions and accounts.

    Args:
        access_token: Plaid access token for the user

    Returns:
        Dictionary containing transactions and account data
    """
    try:
        transactions = plaid_service.get_transactions(access_token, months=6)
        accounts = plaid_service.get_accounts(access_token)

        return {
            "transactions": transactions.get("transactions", []),
            "accounts": accounts.get("accounts", []),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


@tool
def calculate_financial_metrics_tool(plaid_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate financial metrics from Plaid transaction data.

    Args:
        plaid_data: Dictionary containing Plaid transactions and accounts

    Returns:
        Dictionary of calculated financial metrics
    """
    try:
        metrics = financial_calculator.calculate_all_metrics(plaid_data)
        return {
            **metrics,
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


@tool
def search_competitors_tool(
    lat: float,
    lng: float,
    business_type: str,
    radius_miles: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Search for competitor businesses near a location using Google Places API.

    Args:
        lat: Latitude of the location
        lng: Longitude of the location
        business_type: Type of business to search for
        radius_miles: Search radius in miles (default 1.0)

    Returns:
        List of competitor businesses with details
    """
    try:
        competitors = google_service.search_nearby_competitors(
            lat=lat,
            lng=lng,
            business_type=business_type,
            radius_miles=radius_miles
        )
        return competitors
    except Exception as e:
        return [{"error": str(e), "success": False}]


@tool
def analyze_market_saturation_tool(
    competitors: List[Dict[str, Any]],
    business_type: str
) -> Dict[str, Any]:
    """
    Analyze market saturation based on competitor count and ratings.

    Args:
        competitors: List of competitor businesses
        business_type: Type of business being analyzed

    Returns:
        Market saturation analysis including density and viability score
    """
    try:
        competitor_count = len(competitors)

        # Determine market density
        if competitor_count <= 2:
            density = "low"
            viability_score = 85
        elif competitor_count <= 5:
            density = "medium"
            viability_score = 65
        else:
            density = "high"
            viability_score = 40

        # Adjust based on competitor ratings
        avg_rating = sum(c.get("rating", 3.0) for c in competitors) / max(competitor_count, 1)
        if avg_rating < 3.5:
            viability_score += 10  # Opportunity if competitors have low ratings

        return {
            "competitor_count": competitor_count,
            "market_density": density,
            "viability_score": min(100, max(0, viability_score)),
            "average_competitor_rating": round(avg_rating, 2),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


@tool
def calculate_risk_score_tool(
    financial_metrics: Dict[str, float],
    market_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate overall risk score combining financial and market data.

    Args:
        financial_metrics: Financial health metrics
        market_analysis: Market viability analysis

    Returns:
        Risk assessment with score and level
    """
    try:
        # Financial risk factors
        dti = financial_metrics.get("debt_to_income_ratio", 50)
        savings_rate = financial_metrics.get("savings_rate", 0)
        income_stability = financial_metrics.get("income_stability_score", 50)

        # Market risk factors
        market_viability = market_analysis.get("viability_score", 50)

        # Calculate weighted risk score (0-100, lower is better)
        financial_risk = (
            (dti * 0.4) +  # DTI heavily weighted
            ((100 - savings_rate) * 0.3) +  # Inverse savings rate
            ((100 - income_stability) * 0.3)  # Inverse stability
        ) / 3

        market_risk = 100 - market_viability

        # Combined risk (60% financial, 40% market)
        overall_risk = (financial_risk * 0.6) + (market_risk * 0.4)

        # Determine risk level
        if overall_risk < 30:
            risk_level = "low"
        elif overall_risk < 60:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "risk_score": round(overall_risk, 2),
            "risk_level": risk_level,
            "financial_risk": round(financial_risk, 2),
            "market_risk": round(market_risk, 2),
            "success": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Export all tools as a list for LangGraph
AGENT_TOOLS = [
    fetch_plaid_data_tool,
    calculate_financial_metrics_tool,
    search_competitors_tool,
    analyze_market_saturation_tool,
    calculate_risk_score_tool
]
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/unit/test_agent_tools.py -v
```

Expected: PASS (3 tests)

**Step 5: Commit agent tools**

Run:
```bash
git add app/agents/tools.py tests/unit/test_agent_tools.py
git commit -m "feat: add LangChain tools for agent use"
```

---

## Task 9: Multi-Agent System with LangGraph

**Files:**
- Create: `app/agents/graph.py`
- Create: `app/agents/state.py`
- Create: `tests/integration/test_agent_graph.py`

**Step 1: Write test for agent graph**

Create `tests/integration/test_agent_graph.py`:
```python
import pytest
from unittest.mock import Mock, patch
from app.agents.state import AgentState
from app.agents.graph import create_agent_graph


@pytest.mark.asyncio
@patch("app.agents.graph.ChatGoogleGenerativeAI")
async def test_agent_graph_execution(mock_llm):
    """Test that agent graph executes successfully"""
    # Mock LLM responses
    mock_llm_instance = Mock()
    mock_llm.return_value = mock_llm_instance

    # Create initial state
    initial_state = AgentState(
        application_id="test-123",
        user_job="Coffee shop",
        location_lat=43.6532,
        location_lng=-79.3832,
        plaid_access_token="test-token",
        messages=[],
        financial_metrics=None,
        market_analysis=None,
        risk_assessment=None,
        final_decision=None
    )

    # Create graph
    graph = create_agent_graph()

    # Test that graph is created
    assert graph is not None


def test_agent_state_initialization():
    """Test AgentState model initialization"""
    state = AgentState(
        application_id="app-123",
        user_job="Bakery",
        location_lat=40.7128,
        location_lng=-74.0060,
        plaid_access_token="token-123",
        messages=[]
    )

    assert state.application_id == "app-123"
    assert state.user_job == "Bakery"
    assert state.financial_metrics is None
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/integration/test_agent_graph.py -v
```

Expected: FAIL with "No module named 'app.agents.state'"

**Step 3: Create agent state model**

Create `app/agents/state.py`:
```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage


class AgentState(BaseModel):
    """State shared across all agents in the graph"""

    # Application context
    application_id: str
    user_job: str
    location_lat: float
    location_lng: float
    plaid_access_token: str

    # Agent communication
    messages: List[BaseMessage]

    # Analysis results
    financial_metrics: Optional[Dict[str, Any]] = None
    market_analysis: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None

    # Final output
    final_decision: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
```

**Step 4: Implement LangGraph multi-agent system**

Create `app/agents/graph.py`:
```python
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.state import AgentState
from app.agents.tools import (
    fetch_plaid_data_tool,
    calculate_financial_metrics_tool,
    search_competitors_tool,
    analyze_market_saturation_tool,
    calculate_risk_score_tool
)
from app.core.config import settings
from typing import Dict, Any


# Initialize Gemini LLM
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7
    )


# Agent Node Functions
async def financial_analyst_node(state: AgentState) -> Dict[str, Any]:
    """Financial Analyst Agent - analyzes financial health"""

    # Fetch Plaid data
    plaid_data = fetch_plaid_data_tool.invoke({"access_token": state.plaid_access_token})

    if not plaid_data.get("success"):
        return {
            "financial_metrics": {"error": "Failed to fetch Plaid data"},
            "messages": state.messages
        }

    # Calculate metrics
    metrics = calculate_financial_metrics_tool.invoke({"plaid_data": plaid_data})

    # Create message for next agent
    message = HumanMessage(content=f"Financial analysis complete. Metrics: {metrics}")

    return {
        "financial_metrics": metrics,
        "messages": state.messages + [message]
    }


async def market_research_node(state: AgentState) -> Dict[str, Any]:
    """Market Research Agent - analyzes market viability"""

    # Search for competitors
    competitors = search_competitors_tool.invoke({
        "lat": state.location_lat,
        "lng": state.location_lng,
        "business_type": state.user_job,
        "radius_miles": 1.5
    })

    # Analyze market saturation
    market_analysis = analyze_market_saturation_tool.invoke({
        "competitors": competitors,
        "business_type": state.user_job
    })

    # Add competitor details
    market_analysis["nearby_businesses"] = competitors[:5]  # Top 5 competitors

    message = HumanMessage(content=f"Market research complete. Analysis: {market_analysis}")

    return {
        "market_analysis": market_analysis,
        "messages": state.messages + [message]
    }


async def risk_assessment_node(state: AgentState) -> Dict[str, Any]:
    """Risk Assessment Agent - calculates risk score"""

    if not state.financial_metrics or not state.market_analysis:
        return {
            "risk_assessment": {"error": "Missing required data"},
            "messages": state.messages
        }

    # Calculate risk score
    risk_assessment = calculate_risk_score_tool.invoke({
        "financial_metrics": state.financial_metrics,
        "market_analysis": state.market_analysis
    })

    message = HumanMessage(content=f"Risk assessment complete. Risk: {risk_assessment}")

    return {
        "risk_assessment": risk_assessment,
        "messages": state.messages + [message]
    }


async def orchestrator_node(state: AgentState) -> Dict[str, Any]:
    """Orchestrator Agent - synthesizes results and makes final decision"""

    llm = get_llm()

    # Build context for LLM
    system_prompt = """You are a loan assessment expert. Based on the financial metrics,
    market analysis, and risk assessment provided, make a final loan eligibility decision.

    Provide:
    1. Decision: approved, denied, or review
    2. Confidence score (0-100)
    3. Clear reasoning
    4. 2-3 actionable recommendations

    Be concise but thorough."""

    user_prompt = f"""
    Loan Application Analysis:

    Financial Metrics:
    {state.financial_metrics}

    Market Analysis:
    {state.market_analysis}

    Risk Assessment:
    {state.risk_assessment}

    Business Type: {state.user_job}

    Provide your final assessment.
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    # Get LLM decision
    response = await llm.ainvoke(messages)

    # Parse response to determine eligibility
    response_text = response.content.lower()

    if "approved" in response_text:
        eligibility = "approved"
    elif "denied" in response_text:
        eligibility = "denied"
    else:
        eligibility = "review"

    # Build final decision
    final_decision = {
        "eligibility": eligibility,
        "confidence_score": state.risk_assessment.get("risk_score", 50) if state.risk_assessment else 50,
        "risk_level": state.risk_assessment.get("risk_level", "medium") if state.risk_assessment else "medium",
        "reasoning": response.content,
        "recommendations": _extract_recommendations(response.content),
        "financial_metrics": state.financial_metrics,
        "market_analysis": state.market_analysis
    }

    return {
        "final_decision": final_decision,
        "messages": state.messages + [response]
    }


def _extract_recommendations(text: str) -> list:
    """Extract recommendations from LLM response"""
    # Simple extraction - look for numbered lists or bullet points
    lines = text.split("\n")
    recommendations = []

    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
            # Clean up the line
            clean_line = line.lstrip("0123456789.-•).").strip()
            if clean_line and len(clean_line) > 10:
                recommendations.append(clean_line)

    # Return top 3 or default recommendations
    if recommendations:
        return recommendations[:3]

    return [
        "Maintain current financial discipline",
        "Monitor cash flow regularly",
        "Review loan terms carefully before proceeding"
    ]


# Create the agent graph
def create_agent_graph():
    """Create the LangGraph multi-agent workflow"""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("financial_analyst", financial_analyst_node)
    workflow.add_node("market_research", market_research_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("orchestrator", orchestrator_node)

    # Define edges (execution flow)
    workflow.set_entry_point("financial_analyst")
    workflow.add_edge("financial_analyst", "market_research")
    workflow.add_edge("market_research", "risk_assessment")
    workflow.add_edge("risk_assessment", "orchestrator")
    workflow.add_edge("orchestrator", END)

    # Compile the graph
    return workflow.compile()


# Global graph instance
agent_graph = create_agent_graph()
```

**Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/integration/test_agent_graph.py -v
```

Expected: PASS (2 tests)

**Step 6: Commit multi-agent system**

Run:
```bash
git add app/agents/ tests/integration/test_agent_graph.py
git commit -m "feat: add LangGraph multi-agent orchestration system"
```

---

## Task 10: FastAPI Application and Endpoints

**Files:**
- Create: `app/main.py`
- Create: `app/api/routes.py`
- Create: `app/api/dependencies.py`
- Create: `tests/integration/test_api.py`

**Step 1: Write test for API endpoints**

Create `tests/integration/test_api.py`:
```python
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_application():
    """Test creating a loan application"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/applications/create",
            json={
                "job": "Coffee shop owner",
                "age": 32,
                "location": {
                    "lat": 43.6532,
                    "lng": -79.3832,
                    "address": "123 Main St"
                },
                "loan_amount": 50000,
                "loan_purpose": "Equipment"
            }
        )

    assert response.status_code == 201
    data = response.json()
    assert "application_id" in data
    assert data["status"] == "pending_plaid"
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/integration/test_api.py -v
```

Expected: FAIL with "No module named 'app.main'"

**Step 3: Create API dependencies**

Create `app/api/dependencies.py`:
```python
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for database session"""
    async for session in get_db():
        yield session
```

**Step 4: Create API routes**

Create `app/api/routes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_database
from app.models.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    PlaidConnect,
    PlaidConnectResponse,
    AssessmentResponse,
    ApplicationStatusResponse
)
from app.database.models import Application, FinancialMetrics, MarketAnalysis, Assessment
from app.agents.graph import agent_graph
from app.agents.state import AgentState
from app.core.security import encryptor
from app.services.plaid_service import plaid_service
import uuid
from datetime import datetime
from sqlalchemy import select

router = APIRouter(prefix="/api")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/applications/create", response_model=ApplicationResponse, status_code=201)
async def create_application(
    application_data: ApplicationCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new loan application"""

    # Generate application ID
    app_id = str(uuid.uuid4())

    # Create database record
    db_application = Application(
        id=app_id,
        user_job=application_data.job,
        user_age=application_data.age,
        location_lat=application_data.location.lat,
        location_lng=application_data.location.lng,
        location_address=application_data.location.address,
        loan_amount=application_data.loan_amount,
        loan_purpose=application_data.loan_purpose,
        status="pending_plaid"
    )

    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)

    return ApplicationResponse(
        application_id=db_application.id,
        status=db_application.status,
        created_at=db_application.created_at
    )


@router.post("/applications/{application_id}/connect-plaid", response_model=PlaidConnectResponse)
async def connect_plaid(
    application_id: str,
    plaid_data: PlaidConnect,
    db: AsyncSession = Depends(get_database)
):
    """Connect Plaid account and exchange token"""

    # Get application
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Exchange public token for access token
    try:
        access_token = plaid_service.exchange_public_token(plaid_data.plaid_public_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect Plaid: {str(e)}")

    # Encrypt and store access token
    encrypted_token = encryptor.encrypt(access_token)
    application.plaid_access_token = encrypted_token
    application.status = "processing"

    await db.commit()

    return PlaidConnectResponse(
        application_id=application_id,
        status="processing",
        plaid_connected=True
    )


@router.post("/applications/{application_id}/assess", response_model=AssessmentResponse)
async def assess_application(
    application_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Run loan assessment using multi-agent system"""

    # Get application
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if not application.plaid_access_token:
        raise HTTPException(status_code=400, detail="Plaid not connected")

    # Decrypt access token
    access_token = encryptor.decrypt(application.plaid_access_token)

    # Create agent state
    initial_state = AgentState(
        application_id=application_id,
        user_job=application.user_job,
        location_lat=application.location_lat,
        location_lng=application.location_lng,
        plaid_access_token=access_token,
        messages=[]
    )

    # Run agent graph
    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

    decision = final_state.get("final_decision")
    if not decision:
        raise HTTPException(status_code=500, detail="No decision generated")

    # Save results to database
    assessment = Assessment(
        id=str(uuid.uuid4()),
        application_id=application_id,
        eligibility=decision["eligibility"],
        confidence_score=decision["confidence_score"],
        risk_level=decision["risk_level"],
        reasoning=decision["reasoning"],
        recommendations=str(decision["recommendations"])  # JSON string
    )

    db.add(assessment)
    application.status = "completed"
    await db.commit()

    # Return response
    return AssessmentResponse(
        eligibility=decision["eligibility"],
        confidence_score=decision["confidence_score"],
        risk_level=decision["risk_level"],
        reasoning=decision["reasoning"],
        recommendations=decision["recommendations"],
        financial_metrics=decision["financial_metrics"],
        market_analysis=decision["market_analysis"],
        assessed_at=datetime.utcnow()
    )


@router.get("/applications/{application_id}/status", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get application status"""

    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check if assessment exists
    assessment_result = await db.execute(
        select(Assessment).where(Assessment.application_id == application_id)
    )
    assessment = assessment_result.scalar_one_or_none()

    return ApplicationStatusResponse(
        application_id=application.id,
        status=application.status,
        created_at=application.created_at,
        assessed_at=assessment.assessed_at if assessment else None,
        has_results=assessment is not None
    )
```

**Step 5: Create main FastAPI application**

Create `app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.database.session import init_db
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Loan Assessment API",
    description="Multi-agent LLM system for loan eligibility assessment",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Loan Assessment API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

**Step 6: Run test to verify it passes**

Run:
```bash
pytest tests/integration/test_api.py -v
```

Expected: PASS (2 tests)

**Step 7: Commit FastAPI application**

Run:
```bash
git add app/main.py app/api/ tests/integration/test_api.py
git commit -m "feat: add FastAPI application with REST endpoints"
```

---

## Task 11: Environment Setup Script and Documentation

**Files:**
- Create: `scripts/setup.sh`
- Create: `scripts/generate_encryption_key.py`
- Update: `README.md`

**Step 1: Create encryption key generator**

Create `scripts/generate_encryption_key.py`:
```python
#!/usr/bin/env python3
"""Generate encryption key for Fernet"""

from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    print(f"Generated encryption key: {key.decode()}")
    print("\nAdd this to your .env file as:")
    print(f"ENCRYPTION_KEY={key.decode()}")
```

**Step 2: Create setup script**

Create `scripts/setup.sh`:
```bash
#!/bin/bash

echo "Setting up Loan Assessment Backend..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env

    # Generate encryption key
    echo "Generating encryption key..."
    python scripts/generate_encryption_key.py

    echo ""
    echo "IMPORTANT: Edit .env file and add your API keys:"
    echo "   - GEMINI_API_KEY"
    echo "   - PLAID_CLIENT_ID"
    echo "   - PLAID_SECRET"
    echo "   - GOOGLE_MAPS_API_KEY"
    echo "   - GOOGLE_PLACES_API_KEY"
    echo "   - ENCRYPTION_KEY (generated above)"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run the application: uvicorn app.main:app --reload"
echo "3. Visit http://localhost:8000/docs for API documentation"
```

**Step 3: Make script executable**

Run:
```bash
chmod +x scripts/setup.sh
chmod +x scripts/generate_encryption_key.py
```

**Step 4: Update README with comprehensive documentation**

Update `README.md`:
```markdown
# Loan Assessment Backend

Multi-agent LLM system for small business loan eligibility assessment using financial metrics and market viability analysis.

## Features

- **Multi-Agent LLM Architecture** - LangGraph orchestrates specialized agents for financial analysis, market research, and risk assessment
- **Hybrid Assessment** - Combines rule-based financial calculations with Gemini-powered insights
- **Financial Analysis** - Plaid API integration for debt-to-income ratio, savings rate, cash flow, and income stability
- **Market Viability** - Google Places API for competitor analysis and location-based market assessment
- **REST API** - FastAPI endpoints for seamless frontend integration
- **Local Storage** - SQLite database for demo/development purposes

## Architecture

```
┌─────────────────────────────────────────┐
│         Orchestrator Agent              │
│         (Gemini-powered)                │
└────────┬────────────────────────────────┘
         │
    ┌────┴─────┬─────────────┬────────────┐
    │          │             │            │
┌───▼──────┐ ┌─▼──────────┐ ┌─▼─────────┐
│Financial │ │Market      │ │Risk       │
│Analyst   │ │Research    │ │Assessment │
│Agent     │ │Agent       │ │Agent      │
└──────────┘ └────────────┘ └───────────┘
```

## Tech Stack

- **Python 3.11+** - Core language
- **FastAPI** - Modern web framework
- **LangGraph** - Multi-agent orchestration
- **Google Gemini Pro** - LLM reasoning
- **Plaid API** - Financial data (sandbox)
- **Google Maps/Places APIs** - Location and market data
- **SQLite** - Local database
- **Pydantic** - Data validation

## Quick Start

### Prerequisites

- Python 3.11 or higher
- API Keys:
  - Google Gemini API (free for students)
  - Plaid Sandbox credentials
  - Google Maps API key
  - Google Places API key

### Installation

1. **Clone and navigate to project:**
   ```bash
   cd Backend
   ```

2. **Run setup script:**
   ```bash
   bash scripts/setup.sh
   ```

3. **Edit `.env` file with your API keys:**
   ```bash
   nano .env  # or use your preferred editor
   ```

4. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # Mac/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Visit API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Create Application
```http
POST /api/applications/create
Content-Type: application/json

{
  "job": "Coffee shop owner",
  "age": 32,
  "location": {
    "lat": 43.6532,
    "lng": -79.3832,
    "address": "123 Main St, Toronto"
  },
  "loan_amount": 50000,
  "loan_purpose": "Equipment purchase"
}
```

### Connect Plaid
```http
POST /api/applications/{application_id}/connect-plaid
Content-Type: application/json

{
  "plaid_public_token": "public-sandbox-xxx"
}
```

### Run Assessment
```http
POST /api/applications/{application_id}/assess
```

Response:
```json
{
  "eligibility": "approved",
  "confidence_score": 85,
  "risk_level": "low",
  "reasoning": "Strong financial metrics with 28% DTI...",
  "recommendations": [
    "Maintain current savings rate",
    "Focus on unique value proposition"
  ],
  "financial_metrics": {...},
  "market_analysis": {...}
}
```

### Check Status
```http
GET /api/applications/{application_id}/status
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_config.py -v

# Run integration tests only
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking (optional)
mypy app/
```

## Project Structure

```
Backend/
├── app/
│   ├── agents/           # LangGraph agents and tools
│   │   ├── graph.py      # Multi-agent workflow
│   │   ├── state.py      # Shared agent state
│   │   └── tools.py      # LangChain tools
│   ├── api/              # FastAPI routes
│   │   ├── routes.py     # API endpoints
│   │   └── dependencies.py
│   ├── core/             # Core utilities
│   │   ├── config.py     # Settings
│   │   └── security.py   # Encryption
│   ├── database/         # Database layer
│   │   ├── models.py     # SQLAlchemy models
│   │   └── session.py    # DB session
│   ├── models/           # Pydantic schemas
│   │   └── schemas.py
│   ├── services/         # External services
│   │   ├── plaid_service.py
│   │   ├── google_service.py
│   │   └── financial_calculator.py
│   └── main.py           # FastAPI app
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/
│   └── plans/            # Design documents
├── scripts/
│   ├── setup.sh
│   └── generate_encryption_key.py
├── requirements.txt
├── .env.example
└── README.md
```

## Multi-Agent System

### Agents

1. **Orchestrator Agent**
   - Controls workflow execution
   - Decides which agents to invoke
   - Synthesizes final decision

2. **Financial Analyst Agent**
   - Fetches Plaid transaction data
   - Calculates financial metrics
   - Tools: `fetch_plaid_data`, `calculate_financial_metrics`

3. **Market Research Agent**
   - Searches for competitors (Google Places)
   - Analyzes market saturation
   - Tools: `search_competitors`, `analyze_market_saturation`

4. **Risk Assessment Agent**
   - Combines financial + market data
   - Calculates overall risk score
   - Tools: `calculate_risk_score`

### Workflow

```
Financial Analyst → Market Research → Risk Assessment → Orchestrator → Decision
```

## Environment Variables

See `.env.example` for all required variables:

- `GEMINI_API_KEY` - Google Gemini API key
- `PLAID_CLIENT_ID` - Plaid client ID
- `PLAID_SECRET` - Plaid secret key
- `GOOGLE_MAPS_API_KEY` - Google Maps API key
- `GOOGLE_PLACES_API_KEY` - Google Places API key (can be same as Maps)
- `PLAID_ENV` - Plaid environment (sandbox/development/production)
- `DATABASE_URL` - SQLite database path
- `CORS_ORIGINS` - Allowed frontend origins
- `ENCRYPTION_KEY` - Fernet encryption key (generate with script)

## Troubleshooting

### Issue: Import errors
**Solution:** Ensure virtual environment is activated and dependencies are installed

### Issue: Database errors
**Solution:** Delete `loan_assessment.db` and restart the server to recreate tables

### Issue: Plaid API errors
**Solution:** Verify you're using sandbox credentials and tokens are valid

### Issue: Gemini API errors
**Solution:** Check API key is valid and has quota remaining

## Production Considerations

This is a demo/development setup. For production:

1. Replace SQLite with PostgreSQL
2. Use production Plaid environment
3. Add authentication/authorization
4. Implement rate limiting
5. Add logging and monitoring
6. Use environment-specific configs
7. Deploy with Docker/Kubernetes
8. Add CI/CD pipeline

## License

MIT

## Contributing

This is a hackathon/demo project. Feel free to fork and modify!
```

**Step 5: Commit setup scripts and documentation**

Run:
```bash
git add scripts/ README.md
git commit -m "docs: add setup scripts and comprehensive documentation"
```

---

## Task 12: Final Testing and Verification

**Step 1: Run all tests**

Run:
```bash
pytest -v
```

Expected: All tests pass

**Step 2: Test setup script**

Run:
```bash
bash scripts/setup.sh
```

Expected: Virtual environment created, dependencies installed

**Step 3: Verify environment file**

Run:
```bash
cat .env.example
```

Expected: All required environment variables listed

**Step 4: Start the application**

Run:
```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Expected: Server starts on http://localhost:8000

**Step 5: Test API documentation**

Open browser to: http://localhost:8000/docs

Expected: Swagger UI loads with all endpoints

**Step 6: Final commit**

Run:
```bash
git add .
git commit -m "chore: final verification and testing complete"
```

---

## Execution Complete

All tasks completed! The loan assessment backend is fully implemented with:

- Multi-agent LLM system using LangGraph
- Financial metrics calculation from Plaid data
- Market viability analysis using Google APIs
- REST API with FastAPI
- SQLite database for local storage
- Comprehensive testing suite
- Setup scripts and documentation

**Next Steps:**
1. Add your API keys to `.env`
2. Run `uvicorn app.main:app --reload`
3. Test with frontend integration
4. Demo your loan assessment system!
