"""
Community Spark - Modern Financial Dashboard
A user-friendly interface for community loan evaluation with modern UI/UX and MongoDB authentication
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import os
from urllib.parse import unquote

# Backend configuration
BACKEND_URL = "http://localhost:8000"

# ==================== SESSION STATE INITIALIZATION ====================
# Initialize session state for authentication and app state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "session_token" not in st.session_state:
    st.session_state.session_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = None
if "evaluation_id" not in st.session_state:
    st.session_state.evaluation_id = None
if "place_id" not in st.session_state:
    st.session_state.place_id = None
if "place_address" not in st.session_state:
    st.session_state.place_address = None
if "place_lat" not in st.session_state:
    st.session_state.place_lat = None
if "place_lng" not in st.session_state:
    st.session_state.place_lng = None
if "show_bank_connect" not in st.session_state:
    st.session_state.show_bank_connect = False


# ==================== AUTHENTICATION FUNCTIONS ====================

def check_session():
    """Check if user session is valid."""
    if st.session_state.session_token:
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers={"Authorization": f"Bearer {st.session_state.session_token}"},
                timeout=5
            )
            if response.ok:
                result = response.json()
                if result.get("success"):
                    st.session_state.user_info = result["user"]
                    st.session_state.authenticated = True
                    return True
        except Exception as e:
            print(f"Session check failed: {e}")
    
    st.session_state.authenticated = False
    st.session_state.session_token = None
    st.session_state.user_info = None
    return False


def logout():
    """Logout current user."""
    if st.session_state.session_token:
        try:
            requests.post(
                f"{BACKEND_URL}/auth/logout",
                headers={"Authorization": f"Bearer {st.session_state.session_token}"},
                timeout=5
            )
        except:
            pass
    
    st.session_state.authenticated = False
    st.session_state.session_token = None
    st.session_state.user_info = None
    st.session_state.current_page = "Dashboard"
    st.rerun()


# Check session on app load
check_session()

# Page configuration - Modern Financial Dashboard
st.set_page_config(
    page_title="Community Spark - Loan Advisory Dashboard",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS for Modern Dashboard
def load_css():
    st.markdown("""
<style>
        /* Import Modern Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Hide default Streamlit elements for cleaner look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
            padding: 0 !important;
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Fix main content area alignment */
        .block-container {
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* Remove top padding that causes shift */
        section[data-testid="stMain"] {
            padding-top: 0 !important;
        }
        
        /* Sidebar styling - Professional Financial Dashboard */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1d29 0%, #2c3142 100%);
            border-right: none;
            box-shadow: 4px 0 12px rgba(0, 0, 0, 0.1);
            padding-top: 0 !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .css-1d391kg {
            padding-top: 0 !important;
        }
        
        /* Sidebar content starts from top */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }
        
        /* Sidebar Navigation Items */
        .sidebar-nav-item {
            padding: 12px 20px;
            margin: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            font-weight: 500;
        }
        
        .sidebar-nav-item:hover {
            background-color: rgba(0, 102, 255, 0.15);
            transform: translateX(4px);
        }
        
        .sidebar-nav-item.active {
            background-color: #0066FF;
            box-shadow: 0 4px 8px rgba(0, 102, 255, 0.3);
        }
        
        /* Logo placeholder */
        .logo-container {
        padding: 20px;
            padding-top: 20px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
            margin-top: 0;
        }
        
        .logo-container img {
            margin: 0 auto 12px auto;
            display: block;
        }
        
        .logo-text {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
            margin-top: 8px;
        }
        
        .logo-subtitle {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 4px;
        }
        
        /* Header styling */
        .dashboard-header {
            background-color: #ffffff;
            padding: 20px 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            margin-bottom: 24px;
            margin-top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .welcome-text {
            font-size: 28px;
            font-weight: 600;
            color: #1a1d29;
            margin: 0;
        }
        
        .welcome-subtitle {
            font-size: 14px;
            color: #6c757d;
            margin-top: 4px;
        }
        
        /* Metric Cards - Premium Design */
        .metric-card {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .metric-card-title {
            font-size: 14px;
            color: #6c757d;
            font-weight: 500;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-card-value {
            font-size: 32px;
            font-weight: 700;
            color: #1a1d29;
            margin-bottom: 8px;
            line-height: 1;
        }
        
        .metric-card-change {
            font-size: 13px;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 6px;
            display: inline-block;
        }
        
        .metric-positive {
            color: #28a745;
            background-color: #d4edda;
        }
        
        .metric-negative {
            color: #dc3545;
            background-color: #f8d7da;
        }
        
        .metric-neutral {
            color: #0066FF;
            background-color: #e7f3ff;
        }
        
        /* Chart Container */
        .chart-container {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
            margin-bottom: 20px;
        }
        
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            color: #1a1d29;
            margin-bottom: 20px;
        }
        
        /* Activity List */
        .activity-item {
            padding: 16px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            align-items: center;
            transition: background-color 0.2s ease;
        }
        
        .activity-item:hover {
        background-color: #f8f9fa;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            font-size: 18px;
        }
        
        .activity-icon-blue {
            background-color: #e7f3ff;
            color: #0066FF;
        }
        
        .activity-icon-green {
            background-color: #d4edda;
            color: #28a745;
        }
        
        .activity-icon-orange {
            background-color: #fff3cd;
            color: #ffc107;
        }
        
        .activity-text {
            flex: 1;
        }
        
        .activity-title {
            font-size: 14px;
            font-weight: 500;
            color: #1a1d29;
            margin-bottom: 4px;
        }
        
        .activity-time {
            font-size: 12px;
            color: #6c757d;
        }
        
        .activity-amount {
            font-size: 15px;
            font-weight: 600;
        }
        
        /* Button Styling */
        .stButton > button {
            background-color: #0066FF;
            color: white;
            border: none;
        border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #0052cc;
            box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
            transform: translateY(-2px);
        }
        
        /* Form Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stNumberInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            padding: 10px 12px;
            font-size: 14px;
        }
        
        /* Decision Badge */
        .decision-badge {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .decision-approve {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        }
        
        .decision-deny {
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
        }
        
        .decision-refer {
            background: linear-gradient(135deg, #ffc107, #ff9800);
            color: white;
            box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
        }
        
        /* Table Styling */
        .dataframe {
            border: none !important;
        }
        
        .dataframe thead tr th {
            background-color: #f8f9fa !important;
            color: #1a1d29 !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 12px !important;
        }
        
        .dataframe tbody tr td {
            border: none !important;
            border-bottom: 1px solid #f0f0f0 !important;
            padding: 12px !important;
        }
        
        /* Search bar */
        .search-container {
            position: relative;
        }
        
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #6c757d;
        }
        
        /* Profile Icon */
        .profile-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #0066FF, #0052cc);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 102, 255, 0.3);
        }
        
        /* Responsive spacing */
        .section-spacing {
            margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

load_css()

# Add Hamburger Menu Button with working toggle (Floating/Fixed)
# Position in parent window to stay fixed during scroll
components.html("""
<style>
    #hamburger-btn {
        display: none !important; /* Hide the iframe button */
    }
</style>
<div id="hamburger-btn" style="display: none;">
    <div style="width: 24px; height: 3px; background: white; border-radius: 2px;"></div>
    <div style="width: 24px; height: 3px; background: white; border-radius: 2px;"></div>
    <div style="width: 24px; height: 3px; background: white; border-radius: 2px;"></div>
</div>

<script>
(function() {
    const hamburger = document.getElementById('hamburger-btn');
    if (!hamburger) return;
    
    // Hide the iframe button
    hamburger.style.display = 'none';
    
    // Create button in parent window to stay fixed
    function createFixedButton() {
        try {
            const parentWindow = window.parent;
            const parentDoc = parentWindow.document;
            
            if (!parentDoc || !parentDoc.body) return;
            
            // Remove existing button if any
            const existing = parentDoc.getElementById('hamburger-btn-parent');
            if (existing) existing.remove();
            
            // Create button in parent
            const fixedBtn = parentDoc.createElement('div');
            fixedBtn.id = 'hamburger-btn-parent';
            fixedBtn.innerHTML = `
                <div style="width: 24px; height: 3px; background: white; border-radius: 2px; margin-bottom: 4px;"></div>
                <div style="width: 24px; height: 3px; background: white; border-radius: 2px; margin-bottom: 4px;"></div>
                <div style="width: 24px; height: 3px; background: white; border-radius: 2px;"></div>
            `;
            fixedBtn.style.cssText = `
                position: fixed !important;
                top: 20px !important;
                left: 20px !important;
                z-index: 999999 !important;
                cursor: pointer;
                background: #0066FF;
                border-radius: 8px;
                padding: 12px;
                box-shadow: 0 2px 8px rgba(0, 102, 255, 0.3);
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                gap: 4px;
            `;
            parentDoc.body.appendChild(fixedBtn);
            
            // Hover effects
            fixedBtn.addEventListener('mouseenter', function() {
                this.style.background = '#0052cc';
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 12px rgba(0, 102, 255, 0.4)';
            });
            
            fixedBtn.addEventListener('mouseleave', function() {
                this.style.background = '#0066FF';
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 8px rgba(0, 102, 255, 0.3)';
            });
            
            // Click handler - comprehensive sidebar toggle
            fixedBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                
                console.log('Hamburger button clicked!');
                
                try {
                    const parentDoc = window.parent.document;
                    const parentWindow = window.parent;
                    
                    // Log current state
                    const sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
                    const collapsedControl = parentDoc.querySelector('[data-testid="collapsedControl"]');
                    
                    console.log('Sidebar found:', !!sidebar);
                    console.log('Collapsed control found:', !!collapsedControl);
                    if (sidebar) {
                        console.log('Sidebar visible:', sidebar.offsetParent !== null);
                        console.log('Sidebar aria-expanded:', sidebar.getAttribute('aria-expanded'));
                    }
                    
                    // Method 1: Try collapsed control first (most reliable)
                    if (collapsedControl) {
                        console.log('Trying collapsed control...');
                        collapsedControl.click();
                        setTimeout(() => {
                            if (sidebar && sidebar.offsetParent === null) {
                                // Sidebar closed, try opening
                                collapsedControl.click();
                            }
                        }, 100);
                        return;
                    }
                    
                    // Method 2: Try sidebar close button
                    if (sidebar) {
                        console.log('Trying sidebar buttons...');
                        const buttons = sidebar.querySelectorAll('button');
                        console.log('Found buttons:', buttons.length);
                        
                        for (let btn of buttons) {
                            const kind = btn.getAttribute('kind');
                            const ariaLabel = btn.getAttribute('aria-label') || '';
                            console.log('Button kind:', kind, 'aria-label:', ariaLabel);
                            
                            if (kind === 'header') {
                                console.log('Clicking header button');
                                btn.click();
                                return;
                            }
                        }
                        
                        // Try first button
                        if (buttons.length > 0) {
                            console.log('Clicking first button');
                            buttons[0].click();
                            return;
                        }
                    }
                    
                    // Method 3: Simulate keyboard shortcut
                    console.log('Trying keyboard shortcut...');
                    const keyEvent = new KeyboardEvent('keydown', {
                        key: '[',
                        code: 'BracketLeft',
                        keyCode: 219,
                        which: 219,
                        bubbles: true,
                        cancelable: true,
                        view: parentWindow
                    });
                    
                    // Try on document
                    parentDoc.dispatchEvent(keyEvent);
                    parentDoc.body.dispatchEvent(keyEvent);
                    
                    // Try on window
                    parentWindow.dispatchEvent(keyEvent);
                    
                    // Try on all iframes
                    const iframes = parentDoc.querySelectorAll('iframe');
                    for (let iframe of iframes) {
                        try {
                            if (iframe.contentWindow && iframe.contentDocument) {
                                iframe.contentWindow.document.dispatchEvent(keyEvent);
                                iframe.contentWindow.dispatchEvent(keyEvent);
                            }
                        } catch (e) {
                            console.log('Cannot access iframe (cross-origin)');
                        }
                    }
                    
                } catch (err) {
                    console.error('Error toggling sidebar:', err);
                }
            });
            
            return true; // Success
        } catch (err) {
            console.error('Error creating fixed button:', err);
            return false;
        }
    }
    
    // Initialize immediately
    if (createFixedButton()) {
        // Success
    } else {
        // Retry after delays
        setTimeout(createFixedButton, 100);
        setTimeout(createFixedButton, 500);
        setTimeout(createFixedButton, 1000);
    }
    
    // Also initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createFixedButton);
    }
    
    // Watch for parent window ready
    if (window.parent && window.parent.document) {
        if (window.parent.document.readyState === 'loading') {
            window.parent.document.addEventListener('DOMContentLoaded', createFixedButton);
        } else {
            createFixedButton();
        }
    }
})();
</script>
""", height=0)

# ==================== AUTHENTICATION SCREEN ====================
# Show login/signup screen if not authenticated
if not st.session_state.authenticated:
    st.markdown("""
    <div style="max-width: 450px; margin: 80px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="app/static/logo.png" width="80" style="margin-bottom: 16px;">
            <h1 style="color: #1a1d29; margin: 0;">Community Spark</h1>
            <p style="color: #6c757d; margin-top: 8px;">Empowering Communities Through Smart Lending</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tab for Login / Sign Up
    auth_tab = st.tabs(["Login", "Sign Up"])
    
    with auth_tab[0]:  # Login Tab
        st.markdown("### Welcome Back")
        with st.form("login_form"):
            identifier = st.text_input("Email or Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)
            
            if login_btn:
                if identifier and password:
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"identifier": identifier, "password": password},
                            timeout=10
                        )
                        
                        if response.ok:
                            result = response.json()
                            st.session_state.session_token = result["session_token"]
                            st.session_state.user_info = result["user"]
                            st.session_state.authenticated = True
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            error = response.json().get("detail", "Login failed")
                            st.error(f"❌ {error}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
                else:
                    st.warning("⚠️ Please fill in all fields")
    
    with auth_tab[1]:  # Sign Up Tab
        st.markdown("### Create Account")
        with st.form("signup_form"):
            email = st.text_input("Email")
            username = st.text_input("Username")
            full_name = st.text_input("Full Name (optional)")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            signup_btn = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_btn:
                if email and username and password and password_confirm:
                    if password != password_confirm:
                        st.error("❌ Passwords don't match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/auth/register",
                                json={
                                    "email": email,
                                    "username": username,
                                    "password": password,
                                    "full_name": full_name
                                },
                                timeout=10
                            )
                            
                            if response.ok:
                                st.success("✅ Account created! Please login.")
                            else:
                                error = response.json().get("detail", "Registration failed")
                                st.error(f"❌ {error}")
                        except Exception as e:
                            st.error(f"❌ Connection error: {e}")
                else:
                    st.warning("⚠️ Please fill in all required fields")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()  # Stop execution here if not authenticated


# ==================== MAIN AUTHENTICATED APP ====================

# Sidebar - Professional Navigation
with st.sidebar:
    # Logo Section - starts from top
    st.markdown("""
    <div class="logo-container" style="margin-top: 0; padding-top: 20px;">
    """, unsafe_allow_html=True)
    
    # Display logo image
    st.image("logo.png", width=80)
    
    st.markdown(f"""
        <div class="logo-text">Community Spark</div>
        <div class="logo-subtitle">Welcome, {st.session_state.user_info.get('username', 'User')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bank Connection Status
    connected_bank = st.session_state.user_info.get("connected_bank")
    if connected_bank:
        st.success(f"🏦 Bank Connected: {connected_bank}")
        if st.button("Disconnect Bank", use_container_width=True):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/auth/disconnect-bank",
                    headers={"Authorization": f"Bearer {st.session_state.session_token}"},
                    timeout=10
                )
                if response.ok:
                    st.session_state.user_info["connected_bank"] = None
                    st.success("✅ Bank disconnected")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("⚠️ No bank account connected")
        if st.button("Connect Bank Account", use_container_width=True):
            st.session_state.show_bank_connect = True
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### Navigation")
    
    pages = {
        "Dashboard": "Dashboard",
        "Coaching": "Coaching",
        "Invoices": "Invoices",
        "Analytics": "Analytics",
        "Settings": "Settings",
        "About": "About"
    }
    
    for page_label, page_name in pages.items():
        if st.button(page_label, key=page_name, use_container_width=True):
            st.session_state.current_page = page_name
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Logout Button
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; font-size: 11px; color: rgba(255,255,255,0.6);'>
        Community Spark v0.3.0<br>
        Logged in as: {st.session_state.user_info.get('email', 'Unknown')}<br>
        © 2026 All Rights Reserved
    </div>
    """, unsafe_allow_html=True)


# ==================== BANK CONNECTION MODAL ====================
if st.session_state.show_bank_connect:
    # Initialize bank login step if not set
    if "bank_login_step" not in st.session_state:
        st.session_state.bank_login_step = "select_bank"
    
    # Modal container (using centered div instead of fixed positioning)
    st.markdown("""
    <div style="position: relative; margin: 40px auto; max-width: 600px; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
    """, unsafe_allow_html=True)
    
    # Step 1: Select Bank
    if st.session_state.bank_login_step == "select_bank":
        st.markdown("### 🏦 Select Your Bank")
        st.markdown("Choose your bank to securely connect your account")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fake bank options with logos
        banks = [
            {"id": "demo_bank", "name": "Demo Community Bank", "logo": "🏦"},
            {"id": "test_bank", "name": "Test Financial Services", "logo": "🏛️"},
            {"id": "first_national", "name": "First National Bank", "logo": "💼"}
        ]
        
        for bank in banks:
            col_logo, col_name, col_btn = st.columns([1, 4, 2])
            with col_logo:
                st.markdown(f"<div style='font-size: 40px; text-align: center;'>{bank['logo']}</div>", unsafe_allow_html=True)
            with col_name:
                st.markdown(f"**{bank['name']}**")
                st.caption("Personal & Business Banking")
            with col_btn:
                if st.button("Select", key=f"select_{bank['id']}", use_container_width=True):
                    st.session_state.selected_bank = bank
                    st.session_state.bank_login_step = "login"
                    st.rerun()
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_bank_connect = False
            st.session_state.bank_login_step = "select_bank"
            st.rerun()
    
    # Step 2: Bank Login
    elif st.session_state.bank_login_step == "login":
        selected_bank = st.session_state.get("selected_bank", {"name": "Bank", "logo": "🏦"})
        
        # Bank header
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 50px;">{selected_bank['logo']}</div>
            <h3 style="margin: 10px 0; color: #1a1d29;">{selected_bank['name']}</h3>
            <p style="color: #6c757d; font-size: 14px;">Secure Online Banking</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### Sign In to Your Account")
        st.info("💡 **Demo Mode**: Use username **bad_habit_user** (any password works)")
        
        with st.form("bank_login_form"):
            username = st.text_input(
                "Username or Account Number",
                placeholder="Enter your username",
                help="Try: bad_habit_user"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Any password works in demo mode"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                back_btn = st.form_submit_button("← Back", use_container_width=True)
            with col2:
                login_btn = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if back_btn:
                st.session_state.bank_login_step = "select_bank"
                st.rerun()
            
            if login_btn:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    # Map username to profile (case insensitive)
                    username_lower = username.lower().strip()
                    
                    # Profile mapping
                    profile_map = {
                        "bad_habit_user": "bad_habit_user",
                        "badhabituser": "bad_habit_user",
                        "bad_habits": "bad_habit_user",
                        "demo": "bad_habit_user",
                        "test": "bad_habit_user"
                    }
                    
                    bank_profile = profile_map.get(username_lower, "bad_habit_user")
                    
                    # Simulate loading
                    with st.spinner("🔐 Authenticating..."):
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/auth/connect-bank",
                                headers={"Authorization": f"Bearer {st.session_state.session_token}"},
                                json={"bank_profile": bank_profile},
                                timeout=10
                            )
                            
                            if response.ok:
                                st.session_state.user_info["connected_bank"] = bank_profile
                                st.session_state.bank_login_step = "success"
                                st.rerun()
                            else:
                                error = response.json().get("detail", "Connection failed")
                                st.error(f"❌ {error}")
                        except Exception as e:
                            st.error(f"❌ Connection error: {e}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; font-size: 12px; color: #6c757d;">
            🔒 Your credentials are encrypted and secure<br>
            Demo mode - All connections are simulated
        </div>
        """, unsafe_allow_html=True)
    
    # Step 3: Success
    elif st.session_state.bank_login_step == "success":
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 80px; margin-bottom: 20px;">✅</div>
            <h2 style="color: #28a745; margin: 0;">Connected Successfully!</h2>
            <p style="color: #6c757d; margin-top: 10px;">Your bank account has been securely linked</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        connected_profile = st.session_state.user_info.get("connected_bank", "Unknown")
        st.success(f"✅ **Connected Profile:** {connected_profile}")
        st.info("You can now evaluate loan applications using your connected bank account data.")
        
        if st.button("Continue to Dashboard", use_container_width=True, type="primary"):
            st.session_state.show_bank_connect = False
            st.session_state.bank_login_step = "select_bank"
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Stop execution here so main content doesn't show behind modal
    st.stop()


# Main Content Area
current_page = st.session_state.current_page

# ==================== DASHBOARD PAGE ====================
if current_page == "Dashboard":
    # Header with Welcome Message
    col_header_left, col_header_right = st.columns([3, 1])
    
    with col_header_left:
        st.markdown("""
        <div class="dashboard-header" style="margin-right: 10px;">
            <div>
                <div class="welcome-text">Welcome, Alex 👋</div>
                <div class="welcome-subtitle">Here's your loan advisory overview for today</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_header_right:
        st.markdown("""
        <div class="dashboard-header">
            <div class="profile-icon">AS</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Metric Cards Row
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-card-title">💰 Total Balance</div>
            <div class="metric-card-value">$45,320</div>
            <div class="metric-card-change metric-positive">↑ 12.5% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-card-title">💸 Total Spending</div>
            <div class="metric-card-value">$12,480</div>
            <div class="metric-card-change metric-negative">↓ 3.2% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-card-title">💎 Total Saved</div>
            <div class="metric-card-value">$8,940</div>
            <div class="metric-card-change metric-positive">↑ 8.1% from last month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-card-title">📊 Active Loans</div>
            <div class="metric-card-value">3</div>
            <div class="metric-card-change metric-neutral">→ No change</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Grid
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    col_main_left, col_main_right = st.columns([2, 1])
    
    with col_main_left:
        # User Statistics Chart
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">📈 User Statistics</div>
        """, unsafe_allow_html=True)
        
        # Create Plotly grouped bar chart
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        profit = [15000, 18000, 22000, 19000, 25000, 28000]
        investment = [12000, 14000, 18000, 16000, 20000, 23000]
        
        fig = go.Figure(data=[
            go.Bar(
                name='Profit',
                x=months,
                y=profit,
                marker=dict(
                    color='#5DADE2',
                    line=dict(color='#5DADE2', width=1)
                ),
                text=[f'${p/1000:.0f}k' for p in profit],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Profit: $%{y:,}<extra></extra>'
            ),
            go.Bar(
                name='Investment',
                x=months,
                y=investment,
                marker=dict(
                    color='#0066FF',
                    line=dict(color='#0066FF', width=1)
                ),
                text=[f'${i/1000:.0f}k' for i in investment],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Investment: $%{y:,}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter, Segoe UI', size=12, color='#1a1d29'),
            xaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f0f0f0',
                showline=False,
                zeroline=False,
                tickformat='$,.0f'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            ),
            margin=dict(l=0, r=0, t=40, b=0),
            height=320,
            bargap=0.15,
            bargroupgap=0.1,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Loan Evaluation Section
        st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">📝 New Loan Evaluation</div>
        """, unsafe_allow_html=True)
        
        # Google Places Autocomplete Location Picker
        st.markdown("### 📍 Business Location")
        
        # Try to get API key from environment or Streamlit secrets
        google_maps_key = os.getenv("GOOGLE_MAPS_FRONTEND_KEY", "")
        
        # Fallback to Streamlit secrets
        if not google_maps_key and hasattr(st, 'secrets'):
            try:
                google_maps_key = st.secrets.get("GOOGLE_MAPS_FRONTEND_KEY", "")
            except Exception:
                pass
        
        if google_maps_key:
            # Google Maps HTML Component with Places Autocomplete and explicit selection button
            map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; }}
        #search-container {{
            position: relative;
            margin-bottom: 10px;
        }}
        #autocomplete {{
            width: 100%;
            padding: 12px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
        }}
        #autocomplete:focus {{
            border-color: #0066FF;
            box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);
        }}
        #map {{
            width: 100%;
            height: 350px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }}
        #info {{
            margin-top: 10px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 13px;
            color: #495057;
        }}
        .info-label {{
            font-weight: 600;
            color: #1a1d29;
        }}
        #selectBtn {{
            margin-top: 10px;
            width: 100%;
            padding: 12px;
            background: #0066FF;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
        }}
        #selectBtn:hover {{
            background: #0052CC;
        }}
        #selectBtn:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        .success {{
            margin-top: 10px;
            padding: 12px;
            background: #d4edda;
            border-left: 4px solid #28a745;
            border-radius: 6px;
            color: #155724;
            display: none;
        }}
    </style>
</head>
<body>
    <div id="search-container">
        <input id="autocomplete" type="text" placeholder="Search for a business address...">
    </div>
    <div id="map"></div>
    <div id="info">
        <span class="info-label">Preview:</span>
        <span id="location-text">Search for an address or click anywhere on the map</span>
    </div>
    
    <button id="selectBtn" disabled>Select a location first</button>
    
    <div style="margin-top: 8px; font-size: 12px; color: #6c757d;">
        💡 Tip: Use the search box or click directly on the map to place a pin
    </div>
    
    <div id="success" class="success"></div>
    
    <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_key}&libraries=places&callback=initMap" async defer></script>
    <script>
        let map;
        let marker;
        let autocomplete;
        let geocoder;
        let selectedPlace = null;
        
        // Helper function to handle location selection (from autocomplete OR map click)
        function selectLocation(place) {{
            selectedPlace = place;
            
            // Clear existing marker
            if (marker) {{
                marker.setMap(null);
            }}
            
            // Create new marker
            marker = new google.maps.Marker({{
                map: map,
                position: place.geometry.location,
                animation: google.maps.Animation.DROP,
                draggable: true  // Allow dragging the marker
            }});
            
            // Allow marker to be dragged
            marker.addListener('dragend', () => {{
                const newPos = marker.getPosition();
                reverseGeocode(newPos.lat(), newPos.lng());
            }});
            
            // Center map on location
            map.setCenter(place.geometry.location);
            map.setZoom(15);
            
            // Update info display
            const lat = place.geometry.location.lat();
            const lng = place.geometry.location.lng();
            document.getElementById('location-text').textContent = 
                place.formatted_address + ' (Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + ')';
            
            // Enable the select button
            document.getElementById('selectBtn').disabled = false;
            document.getElementById('selectBtn').textContent = '✓ Use This Location';
            document.getElementById('success').style.display = 'none';
        }}
        
        // Reverse geocode coordinates to get address
        function reverseGeocode(lat, lng) {{
            geocoder.geocode({{ location: {{ lat, lng }} }}, (results, status) => {{
                if (status === 'OK' && results[0]) {{
                    const place = {{
                        place_id: results[0].place_id,
                        formatted_address: results[0].formatted_address,
                        geometry: {{
                            location: {{ lat: () => lat, lng: () => lng }}
                        }}
                    }};
                    selectedPlace = place;
                    
                    // Update display
                    document.getElementById('location-text').textContent = 
                        results[0].formatted_address + ' (Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + ')';
                    
                    // Enable button
                    document.getElementById('selectBtn').disabled = false;
                    document.getElementById('selectBtn').textContent = '✓ Use This Location';
                }} else {{
                    // Even if geocoding fails, allow selection with coordinates
                    const place = {{
                        place_id: 'manual_' + Date.now(),
                        formatted_address: `Coordinates: ${{lat.toFixed(6)}}, ${{lng.toFixed(6)}}`,
                        geometry: {{
                            location: {{ lat: () => lat, lng: () => lng }}
                        }}
                    }};
                    selectedPlace = place;
                    document.getElementById('location-text').textContent = place.formatted_address;
                    document.getElementById('selectBtn').disabled = false;
                    document.getElementById('selectBtn').textContent = '✓ Use This Location';
                }}
            }});
        }}
        
        function initMap() {{
            // Default center (New York)
            const defaultCenter = {{ lat: 40.7128, lng: -74.0060 }};
            
            map = new google.maps.Map(document.getElementById('map'), {{
                center: defaultCenter,
                zoom: 13,
                mapTypeControl: true,
                streetViewControl: false,
                fullscreenControl: false
            }});
            
            // Initialize geocoder
            geocoder = new google.maps.Geocoder();
            
            // Initialize autocomplete (no type restriction = show all results like Google Maps)
            autocomplete = new google.maps.places.Autocomplete(
                document.getElementById('autocomplete'),
                {{
                    fields: ['place_id', 'formatted_address', 'geometry', 'name', 'types']
                }}
            );
            
            // Bias autocomplete to current map viewport
            map.addListener('bounds_changed', () => {{
                autocomplete.setBounds(map.getBounds());
            }});
            
            // Listen for place selection from autocomplete
            autocomplete.addListener('place_changed', () => {{
                const place = autocomplete.getPlace();
                
                if (!place.geometry || !place.geometry.location) {{
                    document.getElementById('location-text').textContent = 'No details available for: ' + place.name;
                    document.getElementById('selectBtn').disabled = true;
                    document.getElementById('selectBtn').textContent = 'Select a location first';
                    return;
                }}
                
                // Use the shared selection function
                selectLocation(place);
            }});
            
            // Listen for clicks on the map to place a pin
            map.addListener('click', (event) => {{
                const lat = event.latLng.lat();
                const lng = event.latLng.lng();
                
                // Clear existing marker
                if (marker) {{
                    marker.setMap(null);
                }}
                
                // Create new marker
                marker = new google.maps.Marker({{
                    map: map,
                    position: event.latLng,
                    animation: google.maps.Animation.DROP,
                    draggable: true
                }});
                
                // Allow marker to be dragged
                marker.addListener('dragend', () => {{
                    const newPos = marker.getPosition();
                    reverseGeocode(newPos.lat(), newPos.lng());
                }});
                
                // Reverse geocode the clicked location
                document.getElementById('location-text').textContent = 'Getting address...';
                reverseGeocode(lat, lng);
            }});
            
            // Handle "Use This Location" button click
            document.getElementById('selectBtn').addEventListener('click', () => {{
                if (!selectedPlace) return;
                
                // Get lat/lng (handle both Google Place object and manual object)
                const lat = typeof selectedPlace.geometry.location.lat === 'function' 
                    ? selectedPlace.geometry.location.lat() 
                    : selectedPlace.geometry.location.lat;
                const lng = typeof selectedPlace.geometry.location.lng === 'function'
                    ? selectedPlace.geometry.location.lng()
                    : selectedPlace.geometry.location.lng;
                
                // Update parent URL query params
                try {{
                    const parentUrl = new URL(window.parent.location.href);
                    parentUrl.searchParams.set('place_id', selectedPlace.place_id || 'manual');
                    parentUrl.searchParams.set('address', selectedPlace.formatted_address || 'Manual selection');
                    parentUrl.searchParams.set('lat', lat);
                    parentUrl.searchParams.set('lng', lng);
                    parentUrl.searchParams.set('map_updated', Date.now()); // Trigger change
                    window.parent.history.replaceState({{}}, '', parentUrl);
                    
                    // Force Streamlit to notice the change by reloading
                    window.parent.location.href = parentUrl.toString();
                }} catch (e) {{
                    console.log('Could not update parent URL:', e);
                    // Fallback: show message to user
                    document.getElementById('success').style.display = 'block';
                    document.getElementById('success').textContent = '✓ Location selected! Please click the "Refresh Location" button below the map.';
                }}
            }});
        }}
    </script>
</body>
</html>
            """
            
            components.html(map_html, height=560)
            
            # Check for location data in query params
            query_params = st.query_params
            if 'place_id' in query_params and 'map_updated' in query_params:
                try:
                    place_id = query_params.get('place_id', '')
                    address = query_params.get('address', '')
                    lat = float(query_params.get('lat', 0))
                    lng = float(query_params.get('lng', 0))
                    
                    # Update session state
                    st.session_state.place_id = place_id
                    st.session_state.place_address = address
                    st.session_state.place_lat = lat
                    st.session_state.place_lng = lng
                    
                    # Clear the map_updated param to avoid constant reruns
                    st.query_params.clear()
                except (ValueError, TypeError) as e:
                    pass
            
            # Display current selection
            if st.session_state.place_address:
                st.success(f"✅ **Location Selected:** {st.session_state.place_address}")
                st.caption(f"📍 Coordinates: Lat {st.session_state.place_lat:.6f}, Lng {st.session_state.place_lng:.6f}")
            else:
                st.info("👆 **Two ways to select location:**\n"
                       "1. Search for an address in the search box above\n"
                       "2. Click anywhere on the map to place a pin\n\n"
                       "Then click '✓ Use This Location' button")
            
            # Fallback refresh button (in case auto-reload doesn't work)
            if st.button("🔄 Refresh Location Data", key="refresh_location", help="Click this if the location doesn't update automatically"):
                st.rerun()
        else:
            st.warning("⚠️ Google Maps API key not configured. Set GOOGLE_MAPS_FRONTEND_KEY environment variable.")
        
        st.markdown("---")
        
        with st.form("loan_evaluation_form"):
            # Bank Connection Check
            if not st.session_state.user_info.get("connected_bank"):
                st.warning("⚠️ **No Bank Account Connected** - You need to connect a bank account to evaluate your loan application.")
                if st.form_submit_button("Connect Bank Account"):
                    st.session_state.show_bank_connect = True
                    st.rerun()
                st.stop()
            else:
                st.success(f"🏦 Using connected bank account: **{st.session_state.user_info.get('connected_bank')}**")
            
            st.markdown("---")
            st.markdown("### 🏢 Business Information")
            
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                business_name = st.text_input("Business Name", value="Local Community Market")
            business_type = st.selectbox(
                "Business Type",
                options=["grocery", "pharmacy", "clinic", "childcare", "retail", "other"],
                index=0
            )
            zip_code = st.text_input("ZIP Code", value="10451")
            
            with col_form2:
                hires_locally = st.checkbox("Hires Locally", value=True)
                nearest_competitor_miles = st.number_input(
                    "Nearest Competitor (miles)",
                    min_value=0.0,
                    max_value=100.0,
                    value=8.0,
                    step=0.5
                )
            
            submitted = st.form_submit_button("🚀 Evaluate Loan Application", use_container_width=True)
        
        if submitted:
            # Validate location is selected
            if not st.session_state.place_lat or not st.session_state.place_lng:
                st.error("❌ Please select a business location using the map above before submitting.")
            else:
                business_profile = {
                    "name": business_name,
                    "type": business_type,
                    "zip_code": zip_code,
                    "hires_locally": hires_locally,
                    "nearest_competitor_miles": nearest_competitor_miles,
                    "latitude": st.session_state.place_lat,
                    "longitude": st.session_state.place_lng,
                    "address": st.session_state.place_address,
                    "place_id": st.session_state.place_id
                }
                
                with st.spinner("🔄 Evaluating loan application..."):
                    try:
                        # Use session token to automatically use connected bank account
                        response = requests.post(
                            f"{BACKEND_URL}/evaluate/plaid",
                            json={"business_profile": business_profile},
                            headers={"Authorization": f"Bearer {st.session_state.session_token}"},
                            timeout=30
                        )
                        
                        if response.ok:
                            result = response.json()
                            st.session_state.evaluation_result = result
                            st.session_state.evaluation_id = result.get("evaluation_id")
                            st.success("✅ Evaluation complete!")
                            st.rerun()
                        else:
                            st.error(f"Evaluation failed: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")

        # Display Evaluation Results
        if st.session_state.evaluation_result:
            result = st.session_state.evaluation_result
            decision = result.get("final_decision", "UNKNOWN")
            
            decision_class = f"decision-{decision.lower()}"
            st.markdown(f"""
            <div class="decision-badge {decision_class}">
                {decision}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Rationale:** {result.get('decision_rationale', 'N/A')}")
            
            # Scores
            col_score1, col_score2 = st.columns(2)
            with col_score1:
                st.metric("Auditor Score", f"{result.get('auditor_score', 0)}/100")
            with col_score2:
                multiplier = result.get('community_multiplier', 1.0)
                st.metric("Community Multiplier", f"{multiplier}x")
            
            # Loan Terms
            if result.get("loan_terms"):
                terms = result["loan_terms"]
                st.markdown("### 💰 Loan Terms")
                col_term1, col_term2 = st.columns(2)
                with col_term1:
                    st.metric("Loan Amount", f"${terms.get('loan_amount', 0):,}")
                    st.metric("Term", f"{terms.get('term_months', 0)} months")
                with col_term2:
                    st.metric("Interest Rate", f"{terms.get('interest_rate', 0)}%")
                    st.metric("Monthly Payment", f"${terms.get('monthly_payment', 0):,}")
            
            # Improvement Plan (if DENY/REFER)
            if result.get("improvement_plan"):
                st.markdown("---")
                st.markdown("### 🎯 Improvement Plan")
                improvement_plan = result.get("improvement_plan")
                
                # Spending Analysis (if available)
                if improvement_plan.get("spending_analysis"):
                    st.markdown("#### 💡 Spending Habit Analysis")
                    st.warning(improvement_plan.get("spending_analysis"))
                
                # Critical Issues
                if improvement_plan.get("critical_issues"):
                    st.markdown("#### ⚠️ Critical Issues")
                    for issue in improvement_plan.get("critical_issues", []):
                        st.markdown(f"- {issue}")
                    st.markdown("")
                
                # Summary
                st.info(improvement_plan.get("summary", ""))
                
                st.markdown("**Recommendations:**")
                for rec in improvement_plan.get("recommendations", []):
                    priority_color = {
                        "Critical": "#dc3545",
                        "High": "#ffc107",
                        "Medium": "#0066FF",
                        "Low": "#6c757d"
                    }.get(rec.get("priority", "Medium"), "#0066FF")
                    
                    timeframe = f" • {rec.get('timeframe', '')}" if rec.get('timeframe') else ""
                    
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 12px; padding: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <strong style="color: #1a1d29;">{rec.get('issue', 'N/A')}</strong>
                            <span style="background: {priority_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">
                                {rec.get('priority', 'Medium')}
                            </span>
                        </div>
                        <p style="color: #6c757d; margin: 8px 0; font-size: 14px;">{rec.get('action', 'N/A')}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #28a745; font-size: 12px; font-weight: 600;">{rec.get('expected_impact', '')}</span>
                            <span style="color: #6c757d; font-size: 12px;">{timeframe}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if improvement_plan.get("timeline"):
                    st.markdown(f"**Timeline:** {improvement_plan.get('timeline')}")
                
                if improvement_plan.get("resources"):
                    with st.expander("📚 Resources"):
                        for resource in improvement_plan.get("resources", []):
                            st.markdown(f"- **{resource.get('name')}** ({resource.get('type')})")
                            if resource.get("description"):
                                st.markdown(f"  _{resource.get('description')}_")
                            if resource.get("url"):
                                st.markdown(f"  [Learn more →]({resource.get('url')})")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_main_right:
        # Recent Activity
        
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">🔔 Recent Activity</div>
        """, unsafe_allow_html=True)
        
        activities = [
            {"icon": "💰", "color": "green", "title": "Loan Approved", "time": "2 hours ago", "amount": "+$25,000", "amount_color": "#28a745"},
            {"icon": "📊", "color": "blue", "title": "Application Reviewed", "time": "5 hours ago", "amount": "", "amount_color": "#0066FF"},
            {"icon": "📝", "color": "orange", "title": "Document Submitted", "time": "1 day ago", "amount": "", "amount_color": "#ffc107"},
            {"icon": "✅", "color": "green", "title": "Verification Complete", "time": "2 days ago", "amount": "", "amount_color": "#28a745"},
        ]
        
        for activity in activities:
            amount_html = f'<div class="activity-amount" style="color: {activity["amount_color"]}">{activity["amount"]}</div>' if activity["amount"] else ""
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-icon activity-icon-{activity['color']}">{activity['icon']}</div>
                <div class="activity-text">
                    <div class="activity-title">{activity['title']}</div>
                    <div class="activity-time">{activity['time']}</div>
                </div>
                {amount_html}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Saving Overview
        st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">💎 Saving Overview</div>
        """, unsafe_allow_html=True)
        
        # Create savings data
        savings_data = pd.DataFrame({
            "Category": ["Emergency Fund", "Business Growth", "Equipment", "Marketing"],
            "Amount": ["$3,200", "$2,800", "$1,940", "$1,000"],
            "Progress": ["80%", "70%", "55%", "25%"]
        })
        
        st.dataframe(
            savings_data,
            hide_index=True,
            use_container_width=True,
            height=180
        )
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== ANALYTICS PAGE ====================
elif current_page == "Analytics":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <div class="welcome-text">📈 Analytics</div>
            <div class="welcome-subtitle">Detailed insights and performance metrics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-container">
        <div class="chart-title">Coming Soon</div>
        <p style="color: #6c757d; padding: 40px; text-align: center;">
            Advanced analytics dashboard with detailed loan performance metrics,
            community impact analysis, and trend forecasting.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== COACHING PAGE ====================
elif current_page == "Coaching":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <div class="welcome-text">🎯 Improvement Plans</div>
            <div class="welcome-subtitle">Personalized recommendations to improve your loan application</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    # Display improvement plan from current evaluation if available
    if st.session_state.evaluation_result and st.session_state.evaluation_result.get("improvement_plan"):
        improvement_plan = st.session_state.evaluation_result.get("improvement_plan")
        
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">Current Improvement Plan</div>
        """, unsafe_allow_html=True)
        
        # Business Info
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Business", improvement_plan.get("business_name", "N/A"))
            st.metric("Decision", improvement_plan.get("decision", "N/A"))
        with col_info2:
            st.metric("Current Score", f"{improvement_plan.get('current_score', 0)}/100")
            st.metric("Target Score", f"{improvement_plan.get('target_score', 75)}/100")
        
        # Spending Analysis
        if improvement_plan.get("spending_analysis"):
            st.markdown("---")
            st.markdown("### 💡 Spending Habit Analysis")
            st.warning(improvement_plan.get("spending_analysis"))
        
        # Critical Issues
        if improvement_plan.get("critical_issues"):
            st.markdown("---")
            st.markdown("### ⚠️ Critical Issues")
            for issue in improvement_plan.get("critical_issues", []):
                st.markdown(f"- **{issue}**")
        
        # Summary
        st.markdown("---")
        st.markdown("### 📋 Summary")
        st.info(improvement_plan.get("summary", ""))
        
        # Recommendations
        st.markdown("---")
        st.markdown("### Recommendations")
        
        recommendations = improvement_plan.get("recommendations", [])
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                priority_color = {
                    "Critical": "#dc3545",
                    "High": "#ffc107",
                    "Medium": "#0066FF",
                    "Low": "#6c757d"
                }.get(rec.get("priority", "Medium"), "#0066FF")
                
                timeframe = f"<div style='color: #6c757d; font-size: 13px; margin-top: 8px;'>⏱️ Timeframe: {rec.get('timeframe', 'N/A')}</div>" if rec.get('timeframe') else ""
                
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                        <div>
                            <span style="background: #0066FF; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-right: 8px;">
                                #{idx}
                            </span>
                            <strong style="color: #1a1d29; font-size: 16px;">{rec.get('issue', 'N/A')}</strong>
                        </div>
                        <span style="background: {priority_color}; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600;">
                            {rec.get('priority', 'Medium')} Priority
                        </span>
                    </div>
                    <p style="color: #6c757d; margin: 12px 0; font-size: 14px; line-height: 1.6;">
                        {rec.get('action', 'N/A')}
                    </p>
                    <div style="background: #d4edda; color: #28a745; padding: 8px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; margin-top: 8px; display: inline-block;">
                        💰 {rec.get('expected_impact', '')}
                    </div>
                    {timeframe}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific recommendations available at this time.")

        # Timeline
        if improvement_plan.get("timeline"):
            st.markdown("---")
            st.markdown("### Timeline")
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 18px; font-weight: 600; color: #1a1d29; margin-bottom: 8px;">
                    Expected Improvement Time
                </div>
                <div style="font-size: 24px; font-weight: 700; color: #0066FF;">
                    {improvement_plan.get('timeline')}
                </div>
    </div>
    """, unsafe_allow_html=True)

        # Resources
        if improvement_plan.get("resources"):
            st.markdown("---")
            st.markdown("### Resources")
            st.markdown("""
            <div class="chart-container">
            """, unsafe_allow_html=True)
            
            resources = improvement_plan.get("resources", [])
            for resource in resources:
                description = f"<div style='font-size: 12px; color: #6c757d; margin-top: 4px;'>{resource.get('description', '')}</div>" if resource.get('description') else ""
                
                st.markdown(f"""
                <div style="padding: 16px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #1a1d29; margin-bottom: 4px;">{resource.get('name', 'N/A')}</div>
                        <div style="font-size: 12px; color: #6c757d;">{resource.get('type', 'N/A')}</div>
                        {description}
                    </div>
                    {f'<a href="{resource.get("url")}" target="_blank" style="color: #0066FF; text-decoration: none; font-weight: 600;">View →</a>' if resource.get('url') else ''}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # No improvement plan available
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">No Active Improvement Plan</div>
            <p style="color: #6c757d; padding: 40px; text-align: center;">
                Improvement plans are generated for loan applications that receive a <strong>DENY</strong> or <strong>REFER</strong> decision.
                <br><br>
                Submit a loan evaluation from the Dashboard to receive personalized recommendations and an improvement plan.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Go to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()

# ==================== INVOICES PAGE ====================
elif current_page == "Invoices":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <div class="welcome-text">📋 Invoices</div>
            <div class="welcome-subtitle">Manage your loan invoices and payment history</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-container">
        <div class="chart-title">Invoice Management</div>
        <p style="color: #6c757d; padding: 40px; text-align: center;">
            Invoice tracking and payment management features coming soon.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SETTINGS PAGE ====================
elif current_page == "Settings":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <div class="welcome-text">⚙️ Settings</div>
            <div class="welcome-subtitle">Configure your account and preferences</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    col_settings1, col_settings2 = st.columns(2)
    
    with col_settings1:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">Profile Settings</div>
        """, unsafe_allow_html=True)
        
        st.text_input("Full Name", value="Alex Smith")
        st.text_input("Email", value="alex.smith@example.com")
        st.text_input("Phone", value="+1 (555) 123-4567")
        
        if st.button("Update Profile"):
            st.success("Profile updated successfully!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_settings2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">Security Settings</div>
        """, unsafe_allow_html=True)
        
        st.checkbox("Enable two-factor authentication", value=True)
        st.checkbox("Email notifications", value=True)
        st.checkbox("SMS alerts for loan updates", value=False)
        
        if st.button("Manage Passkeys"):
            st.info("Opening WebAuthn configuration...")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== ABOUT PAGE ====================
elif current_page == "About":
    st.markdown("""
    <div class="dashboard-header">
        <div>
            <div class="welcome-text">ℹ️ About Community Spark</div>
            <div class="welcome-subtitle">Learn about our multi-agent loan evaluation platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    # Display graph visualization if available
    graph_path = Path(__file__).parent / "artifacts" / "graph.png"
    
    if graph_path.exists():
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">📊 Agent Workflow Diagram</div>
        """, unsafe_allow_html=True)
        st.image(str(graph_path), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    col_about1, col_about2, col_about3 = st.columns(3)
    
    with col_about1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #0066FF;">🔍 Auditor Agent</h3>
            <p style="font-size: 14px; color: #6c757d;">
                Analyzes bank transaction data, calculates revenue metrics,
                and generates baseline financial scores.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_about2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #0066FF;">🌱 Impact Analyst</h3>
            <p style="font-size: 14px; color: #6c757d;">
                Evaluates community metrics and calculates impact multipliers
                for businesses serving underserved areas.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_about3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #0066FF;">🛡️ Compliance Sentry</h3>
            <p style="font-size: 14px; color: #6c757d;">
                Applies policy guardrails, makes final decisions,
                and generates loan terms with detailed rationale.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-container">
        <div class="chart-title">✨ Key Features</div>
        <ul style="font-size: 14px; color: #6c757d; line-height: 1.8;">
            <li><strong>Multi-Agent Architecture:</strong> Specialized agents with distinct expertise</li>
            <li><strong>Community Impact Focus:</strong> Rewards businesses serving underserved communities</li>
            <li><strong>WebAuthn Security:</strong> Passwordless authentication with biometric passkeys</li>
            <li><strong>Transparent Decisions:</strong> Complete reasoning trail for every evaluation</li>
            <li><strong>Real-time Analysis:</strong> Instant loan evaluation with Plaid integration</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
