# 💼 Community Spark - Loan Advisory Dashboard

<div align="center">

![Community Spark](https://img.shields.io/badge/UofT%20Hacks-2026-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=for-the-badge&logo=streamlit)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal?style=for-the-badge&logo=fastapi)

**A modern, AI-powered loan evaluation platform with community impact focus**

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Architecture](#-architecture)

</div>

---

## 🎯 Overview

Community Spark is an intelligent loan advisory platform that combines multi-agent AI decision-making with a premium financial dashboard interface. Built for UofT Hacks 13, it evaluates business loan applications through:

- **Multi-Agent AI System** - Specialized agents for financial auditing, community impact analysis, and compliance
- **Modern Dashboard UI** - Adicap-inspired interface with real-time metrics and interactive charts
- **WebAuthn Security** - Passwordless authentication with biometric passkeys
- **Plaid Integration** - Real-time financial data analysis

## ✨ Features

### 🎨 Modern Financial Dashboard

- **Professional Sidebar Navigation** with dark gradient theme
- **Real-time Metric Cards** displaying balance, spending, savings, and active loans
- **Interactive Plotly Charts** for profit and investment visualization
- **Card History Visual** with premium credit card mockup
- **Recent Activity Feed** with color-coded transaction icons
- **Saving Overview Table** with progress tracking
- **Responsive Design** optimized for desktop, tablet, and mobile

### 🤖 Multi-Agent AI System

- **Auditor Agent** - Analyzes financial data and generates baseline scores
- **Impact Analyst** - Evaluates community impact with multiplier boosts (up to 1.6x)
- **Compliance Sentry** - Applies policy guardrails and makes final decisions
- **Conditional Routing** - Smart workflow based on financial scores

### 🔐 Security & Compliance

- **WebAuthn Passkeys** - FIDO2-compliant passwordless authentication
- **1Password Integration** - Secret management via `op run`
- **HMAC Token Signing** - Secure session management
- **Audit Trails** - Complete reasoning logs for every decision

### 📊 Data Integration

- **Plaid API** - Real-time transaction data from sandbox environment
- **Feature Extraction** - Automated financial metrics calculation
- **LangGraph Workflow** - Orchestrated agent pipeline
- **FastAPI Backend** - High-performance REST API

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- 1Password CLI (`op`)
- Node.js (optional, for development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/uoft-hacks-13.git
cd uoft-hacks-13
```

2. **Set up Python environment**
```bash
cd community-spark
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure secrets** (via 1Password)
```bash
# Set up your 1Password secret references
# Required: PLAID_CLIENT_ID, PLAID_SECRET, PASSKEY_HMAC_SECRET
# Optional: OPENAI_API_KEY (for enhanced AI reasoning)
```

4. **Start the backend**
```bash
cd community-spark
op run -- uvicorn app.main:app --reload
```

5. **Start the dashboard** (new terminal)
```bash
# From project root
op run -- streamlit run streamlit_app.py
```

6. **Access the application**
- Dashboard: http://localhost:8501
- API: http://localhost:8000
- Passkeys: http://localhost:8000/passkeys

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
- **[UI_GUIDE.md](UI_GUIDE.md)** - Complete UI customization guide
- **[community-spark/README.md](community-spark/README.md)** - Backend API documentation
- **[community-spark/SETUP_GUIDE.md](community-spark/SETUP_GUIDE.md)** - Detailed setup instructions

## 🏗️ Architecture

### Frontend Stack
- **Streamlit** - Modern Python web framework
- **Plotly** - Interactive data visualization
- **Custom CSS** - Premium financial dashboard styling
- **Inter Font** - Clean, professional typography

### Backend Stack
- **FastAPI** - High-performance async API framework
- **LangGraph** - Multi-agent workflow orchestration
- **Plaid API** - Financial data integration
- **WebAuthn** - Passwordless authentication
- **OpenAI** (optional) - Enhanced AI reasoning

### Agent Workflow

```
START → Auditor Agent → [Score < 60?] → Impact Analyst → Compliance Sentry → DECISION
                    ↓
                [Score ≥ 60?]
                    ↓
            Compliance Sentry → DECISION
```

## 🎨 UI Screenshots

### Dashboard Overview
- Modern sidebar with navigation
- Real-time metric cards
- Interactive charts
- Recent activity feed

### Loan Evaluation
- Business profile form
- Instant AI evaluation
- Decision badges (APPROVE/DENY/REFER)
- Detailed reasoning logs

### Analytics & Reports
- User statistics visualization
- Profit vs. investment comparison
- Saving overview table
- Card history display

## 🔧 Customization

### Change Primary Color

Edit `streamlit_app.py`:
```python
# Find #0066FF and replace with your brand color
background-color: #YOUR_COLOR;
```

### Modify Metric Cards

Update values in the Dashboard section:
```python
st.markdown("""
<div class="metric-card">
    <div class="metric-card-title">💰 Total Balance</div>
    <div class="metric-card-value">$XX,XXX</div>
</div>
""", unsafe_allow_html=True)
```

### Add Navigation Pages

Update the sidebar navigation:
```python
pages = {
    "📊 Dashboard": "Dashboard",
    "🆕 Your Page": "YourPage",  # Add here
}
```

## 🧪 Testing

### Test Plaid Integration
```bash
cd community-spark
op run -- python test_plaid.py
```

### Test Evaluation Endpoint
```bash
op run -- python test_plaid_endpoint.py
```

### Test Community Data
```bash
op run -- python test_community_data.py
```

## 🚀 Deployment

### Streamlit Cloud
```bash
# Push to GitHub
# Connect to Streamlit Cloud
# Add secrets in Streamlit Cloud dashboard
```

### Docker (Coming Soon)
```bash
docker-compose up
```

## 📊 Sample Use Cases

### High-Growth Business
- **Scenario**: Grocery store in food desert, strong financials
- **Expected**: APPROVE with high score + community boost

### Community Impact Focus
- **Scenario**: New pharmacy, moderate financials, underserved area
- **Expected**: APPROVE with significant community multiplier (1.4x-1.6x)

### Policy Guardrail
- **Scenario**: Retail business with NSF flags
- **Expected**: DENY or REFER despite community impact

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- **UofT Hacks 13** - Hackathon host
- **Streamlit** - Amazing Python web framework
- **FastAPI** - High-performance backend framework
- **LangGraph** - Agent orchestration platform
- **Plaid** - Financial data API

## 🔗 Links

- [Streamlit Documentation](https://docs.streamlit.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Plaid Documentation](https://plaid.com/docs/)
- [WebAuthn Guide](https://webauthn.guide/)

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

<div align="center">

**Built with ❤️ for UofT Hacks 13**

⭐ Star this repo if you find it helpful!

</div>