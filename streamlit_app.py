"""
Community Spark - Streamlit Application

A user-friendly interface for community loan evaluation with WebAuthn passkey support.
"""

import streamlit as st
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Backend configuration
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Community Spark - Loan Evaluation",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-decision {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .approve { background-color: #d4edda; color: #155724; }
    .deny { background-color: #f8d7da; color: #721c24; }
    .refer { background-color: #fff3cd; color: #856404; }
    .log-entry {
        padding: 10px;
        margin: 5px 0;
        border-left: 3px solid #007bff;
        background-color: #f8f9fa;
        border-radius: 4px;
    }
    .metric-box {
        padding: 15px;
        background-color: #f0f2f6;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'evaluation_id' not in st.session_state:
    st.session_state.evaluation_id = None
if 'assertion_token' not in st.session_state:
    st.session_state.assertion_token = None

# Title
st.title("🏘️ Community Spark")
st.markdown("*Community-focused loan evaluation platform*")

# Create tabs
tab1, tab2 = st.tabs(["📊 Dashboard", "ℹ️ About"])

with tab1:
    # Security Transparency Toggle
    with st.expander("🔐 Security Transparency", expanded=False):
        st.markdown("""
        **Security Best Practices:**
        - Secrets loaded via **1Password `op run`** (no `.env` files)
        - Passkey authentication using WebAuthn standard
        - HMAC-signed tokens for session management
        """)
        
        if st.button("Check Secrets Status"):
            try:
                response = requests.get(f"{BACKEND_URL}/secrets-check")
                if response.ok:
                    secrets = response.json()
                    st.success("✅ Backend is reachable")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        status = "✅" if secrets.get("PLAID_CLIENT_ID") else "❌"
                        st.metric("PLAID_CLIENT_ID", status)
                    with col2:
                        status = "✅" if secrets.get("PLAID_SECRET") else "❌"
                        st.metric("PLAID_SECRET", status)
                    with col3:
                        status = "✅" if secrets.get("OPENAI_API_KEY") else "⚠️ Optional"
                        st.metric("OPENAI_API_KEY", status)
                else:
                    st.error(f"Backend error: {response.status_code}")
            except Exception as e:
                st.error(f"Cannot connect to backend: {e}")

    # Main layout
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.header("📝 Business Profile")
        
        with st.form("business_profile_form"):
            business_name = st.text_input("Business Name", value="Local Community Market")
            
            business_type = st.selectbox(
                "Business Type",
                options=["grocery", "pharmacy", "clinic", "childcare", "retail", "other"],
                index=0
            )
            
            zip_code = st.text_input("ZIP Code", value="10451")
            
            with st.expander("📍 Optional Location Details"):
                col1, col2 = st.columns(2)
                with col1:
                    latitude = st.text_input("Latitude", value="", placeholder="40.7589")
                with col2:
                    longitude = st.text_input("Longitude", value="", placeholder="-73.9851")
            
            with st.expander("🏢 Additional Details (Optional)"):
                hires_locally = st.checkbox("Hires Locally", value=True)
                nearest_competitor_miles = st.number_input(
                    "Distance to Nearest Competitor (miles)",
                    min_value=0.0,
                    max_value=100.0,
                    value=8.0,
                    step=0.5
                )
            
            submitted = st.form_submit_button("🚀 Run Evaluation", use_container_width=True)
        
        if submitted:
            # Build business profile
            business_profile = {
                "name": business_name,
                "type": business_type,
                "zip_code": zip_code,
                "hires_locally": hires_locally,
                "nearest_competitor_miles": nearest_competitor_miles
            }
            
            # Only add lat/lon if they have values
            if latitude and latitude.strip():
                try:
                    business_profile["latitude"] = float(latitude)
                except ValueError:
                    st.warning(f"Invalid latitude value: {latitude}")
            
            if longitude and longitude.strip():
                try:
                    business_profile["longitude"] = float(longitude)
                except ValueError:
                    st.warning(f"Invalid longitude value: {longitude}")
            
            with st.spinner("🔄 Evaluating loan application..."):
                try:
                    # Try /evaluate/plaid first
                    response = requests.post(
                        f"{BACKEND_URL}/evaluate/plaid",
                        json={"business_profile": business_profile},
                        timeout=30
                    )
                    
                    if response.ok:
                        result = response.json()
                        st.session_state.evaluation_result = result
                        st.session_state.evaluation_id = result.get("evaluation_id")
                        st.success("✅ Evaluation complete!")
                    else:
                        st.error(f"Evaluation failed: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")

    with col_right:
        st.header("📊 Evaluation Results")
        
        if st.session_state.evaluation_result:
            result = st.session_state.evaluation_result
            
            # Display decision
            decision = result.get("final_decision", "UNKNOWN")
            decision_class = decision.lower()
            
            st.markdown(f"""
            <div class="big-decision {decision_class}">
                {decision}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Rationale:** {result.get('decision_rationale', 'N/A')}")
            
            # Scores
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Auditor Score", f"{result.get('auditor_score', 0)}/100")
            with col2:
                multiplier = result.get('community_multiplier', 1.0)
                st.metric("Community Multiplier", f"{multiplier}x")
            
            # Loan Terms
            if result.get("loan_terms"):
                st.subheader("💰 Loan Terms")
                terms = result["loan_terms"]
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Loan Amount", f"${terms.get('loan_amount', 0):,}")
                    st.metric("Term", f"{terms.get('term_months', 0)} months")
                with col2:
                    st.metric("Interest Rate", f"{terms.get('interest_rate', 0)}%")
                    st.metric("Monthly Payment", f"${terms.get('monthly_payment', 0):,}")
            
            # Explain object
            if result.get("explain"):
                with st.expander("🔍 Decision Breakdown", expanded=True):
                    explain = result["explain"]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Baseline Score", explain.get("baseline_score", 0))
                    with col2:
                        st.metric("Multiplier", f"{explain.get('community_multiplier', 1.0)}x")
                    with col3:
                        st.metric("Adjusted Score", explain.get("adjusted_score", 0))
                    
                    st.markdown(f"**Decision Path:** `{explain.get('decision_path', 'N/A')}`")
                    
                    # Policy checks
                    st.markdown("**Policy Floor Checks:**")
                    for check in explain.get("policy_floor_checks", []):
                        status = "✅" if check.get("passed") else "❌"
                        reason = check.get("reason", "")
                        st.markdown(f"- {status} **{check.get('check')}**: {check.get('value')} (threshold: {check.get('threshold')}) {reason}")
            
            # Signature requirement
            if result.get("needs_signature"):
                st.warning("⚠️ This evaluation requires passkey signature to finalize")
                
                if st.button("🔐 Sign with Passkey"):
                    st.info("Please use the passkey authentication at /passkeys to sign in and get an assertion token")
                    st.markdown("[Open Passkeys Page](http://localhost:8000/passkeys)")
            
            # Agent Log
            st.subheader("🤖 Agent Reasoning Log")
            logs = result.get("log", [])
            
            if logs:
                for log_entry in logs:
                    agent = log_entry.get("agent", "unknown")
                    message = log_entry.get("message", "")
                    reasoning = log_entry.get("reasoning", "")
                    method = log_entry.get("method", "")
                    step = log_entry.get("step", "")
                    
                    # Build log display
                    log_html = f'<div class="log-entry"><strong>🔹 {agent.upper()}</strong>'
                    
                    # Show method badge if present
                    if method == "hybrid":
                        log_html += ' <span style="background: #2196F3; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 8px;">HYBRID AI</span>'
                    elif method == "hybrid-explanation":
                        log_html += ' <span style="background: #673AB7; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 8px;">RULES + AI EXPLANATION</span>'
                    elif method == "llm":
                        log_html += ' <span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 8px;">AI-POWERED</span>'
                    elif method == "rule-based":
                        log_html += ' <span style="background: #FF9800; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 8px;">RULE-BASED</span>'
                    
                    log_html += f'<br>{message}<br>'
                    
                    # Show detailed reasoning if available
                    if reasoning:
                        log_html += f'<br><em>Reasoning:</em> {reasoning}<br>'
                    
                    log_html += f'<small>Step: {step}</small></div>'
                    
                    st.markdown(log_html, unsafe_allow_html=True)
            else:
                st.info("No log entries available")
            
            # Extracted features (if Plaid was used)
            if result.get("extracted_features"):
                with st.expander("📈 Extracted Financial Features"):
                    features = result["extracted_features"]
                    st.json(features)
        
        else:
            st.info("👈 Enter business profile and click 'Run Evaluation' to see results")

    # Sidebar - Passkey Authentication
    with st.sidebar:
        st.header("🔐 Passkey Authentication")
        
        st.markdown("""
        Use WebAuthn passkeys for passwordless authentication.
        """)
        
        # Registration
        with st.expander("Register New Passkey"):
            user_id = st.text_input("User ID", value="user123", key="reg_user_id")
            username = st.text_input("Username/Email", value="test@example.com", key="reg_username")
            display_name = st.text_input("Display Name", value="Test User", key="reg_display_name")
            
            st.info("⚠️ Passkey registration requires browser WebAuthn API. Please use the web interface at /passkeys")
            st.markdown("[Open Passkeys Page](http://localhost:8000/passkeys)")
        
        # Authentication
        with st.expander("Sign In"):
            auth_user_id = st.text_input("User ID", value="user123", key="auth_user_id")
            
            st.info("⚠️ Passkey authentication requires browser WebAuthn API. Please use the web interface at /passkeys")
            st.markdown("[Open Passkeys Page](http://localhost:8000/passkeys)")
        
        # Finalize with token
        st.markdown("---")
        st.subheader("✍️ Finalize Evaluation")
        
        if st.session_state.evaluation_id:
            st.info(f"Evaluation ID: `{st.session_state.evaluation_id[:8]}...`")
            
            assertion_token_input = st.text_area(
                "Assertion Token",
                value="",
                placeholder="Paste token from passkey sign-in",
                height=100
            )
            
            if st.button("Finalize with Signature", use_container_width=True):
                if not assertion_token_input:
                    st.error("Please provide an assertion token")
                else:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/finalize",
                            json={
                                "evaluation_id": st.session_state.evaluation_id,
                                "assertion_token": assertion_token_input.strip()
                            }
                        )
                        
                        if response.ok:
                            finalize_result = response.json()
                            st.success("✅ Evaluation finalized and signed!")
                            st.json(finalize_result)
                        else:
                            error_detail = response.json().get("detail", "Unknown error")
                            st.error(f"Finalization failed: {error_detail}")
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("Run an evaluation first to get an evaluation ID")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>Community Spark v0.1.0 | Built with FastAPI + LangGraph + Streamlit</small>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    # About tab content
    st.header("About Community Spark")
    
    st.markdown("""
    ## 🧠 Multi-Agent Mind
    
    Community Spark uses a **3-agent LangGraph workflow** to evaluate loan applications
    with both financial rigor and community impact awareness. Each agent has a specialized role,
    and they work together through conditional routing to make intelligent decisions.
    """)
    
    # Display graph visualization
    graph_path = Path(__file__).parent / "artifacts" / "graph.png"
    
    if graph_path.exists():
        st.subheader("📊 Agent Workflow Diagram")
        st.image(str(graph_path), use_container_width=True)
        st.caption("Visual representation of the agent decision flow")
    else:
        st.info("💡 Run `python scripts/render_graph.py` to generate the workflow diagram")
    
    st.markdown("---")
    
    st.subheader("🤖 The Three Agents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🔍 Auditor Agent
        **Role:** Financial Analysis
        
        - Analyzes bank transaction data
        - Calculates revenue metrics, volatility, NSF counts
        - Generates baseline financial score (1-100)
        - Flags potential risk indicators
        """)
    
    with col2:
        st.markdown("""
        ### 🌱 Impact Analyst
        **Role:** Community Multiplier
        
        - Evaluates community metrics (food deserts, hiring, access)
        - Calculates community impact multiplier (1.0x - 1.6x)
        - Only activated when baseline score needs boost
        - Rewards businesses serving underserved communities
        """)
    
    with col3:
        st.markdown("""
        ### 🛡️ Compliance Sentry
        **Role:** Final Decision & Guardrails
        
        - Combines financial score × community multiplier
        - Applies policy guardrails (minimum thresholds)
        - Makes final APPROVE / DENY / REFER decision
        - Generates loan terms and detailed rationale
        """)
    
    st.markdown("---")
    
    st.subheader("🔄 Conditional Routing Logic")
    
    st.markdown("""
    The workflow uses **intelligent conditional routing** based on the auditor's initial assessment:
    
    1. **START** → All applications begin with the **Auditor Agent**
    
    2. **Conditional Branch:**
       - **If `auditor_score < 60`** → Route to **Impact Analyst** for community boost
       - **If `auditor_score >= 60`** → Skip directly to **Compliance Sentry**
    
    3. **Impact Analyst** (if activated) → Always routes to **Compliance Sentry**
    
    4. **Compliance Sentry** → Makes final decision and generates loan terms
    
    5. **END** → Decision returned (APPROVE / DENY / REFER)
    """)
    
    st.info("""
    💡 **Why conditional routing?** 
    
    Applications with strong financials (score ≥ 60) don't need community boost evaluation,
    saving time and resources. Only applications that need an "impact boost" go through
    the community analysis step.
    """)
    
    st.markdown("---")
    
    st.subheader("✨ Key Features")
    
    st.markdown("""
    ### 🧠 Multi-Agent Mind
    - **Specialized agents** each with distinct expertise
    - **Collaborative decision-making** through shared state
    - **Transparent reasoning** via detailed logs
    - **Scalable architecture** using LangGraph
    
    ### 📈 Impact Boost with Compliance Guardrails
    - **Community multiplier** (up to 1.6x) rewards businesses serving underserved areas
    - **Policy guardrails** ensure minimum financial standards are met
    - **Balanced approach** between financial risk and community impact
    - **Explainable decisions** with detailed breakdowns
    """)
    
    st.markdown("---")
    
    st.subheader("🔐 Security & Transparency")
    
    st.markdown("""
    - **1Password Secret References** - No `.env` files, secrets injected via `op run`
    - **WebAuthn Passkeys** - Passwordless authentication for loan finalization
    - **HMAC-signed tokens** - Secure session management
    - **Audit logs** - Complete reasoning trail for every decision
    """)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <strong>Community Spark v0.1.0</strong><br>
        Built with FastAPI + LangGraph + Streamlit<br>
        <small>Empowering community-focused lending through AI</small>
    </div>
    """, unsafe_allow_html=True)
