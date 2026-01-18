"""
FastAPI Main Application Entry Point

This module contains the FastAPI application setup, including:
- API route definitions
- Middleware configuration
- Integration with LangGraph workflows
- Health check endpoints
"""

import os
import hmac
import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Response, Header
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from app.graph import build_graph
from app.state import CommunitySparkState
from app.data.plaid_client import plaid_sandbox_get_transactions
from app.data.feature_extractor import extract_bank_features
from app.data.user_profiles import get_user_profile, convert_profile_to_plaid_format
from app.security.webauthn_routes import router as webauthn_router
from app.maps.google_maps import geocode_address
from app.database.mongodb import user_manager

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Community Spark API",
    description="Community impact analysis and compliance monitoring platform",
    version="0.1.0"
)

# Mount WebAuthn routes
app.include_router(webauthn_router)

# Initialize graph once at startup
graph = build_graph()

# In-memory evaluation storage (demo-only)
evaluations: Dict[str, Dict[str, Any]] = {}

# Token verification (shared with webauthn_routes)
HMAC_SECRET = os.getenv("PASSKEY_HMAC_SECRET", "dev-secret-change-in-production")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode an assertion token.
    
    Args:
        token: Token string to verify
        
    Returns:
        Dict with user_id if valid
        
    Raises:
        HTTPException if token is invalid or expired
    """
    try:
        parts = token.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        user_id, exp_str, signature = parts
        exp = int(exp_str)
        
        # Check expiry
        if time.time() > exp:
            raise HTTPException(status_code=401, detail="Token expired")
        
        # Verify signature
        payload = f"{user_id}:{exp_str}"
        expected_signature = hmac.new(
            HMAC_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid token signature")
        
        return {"user_id": user_id, "exp": exp}
    
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


class EvaluateRequest(BaseModel):
    """Request model for /evaluate endpoint"""
    business_profile: Dict[str, Any]
    bank_data: Dict[str, Any]


class EvaluatePlaidRequest(BaseModel):
    """Request model for /evaluate/plaid endpoint"""
    business_profile: Dict[str, Any]
    profile: Optional[str] = None  # Optional: "bad_habit_user" or None for default Plaid sandbox


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = ""


class LoginRequest(BaseModel):
    """Request model for user login"""
    identifier: str  # Email or username
    password: str


class ConnectBankRequest(BaseModel):
    """Request model for connecting bank account"""
    bank_profile: str  # Profile name to connect


class FinalizeRequest(BaseModel):
    """Request model for /finalize endpoint"""
    evaluation_id: str
    assertion_token: str


class GeocodeRequest(BaseModel):
    """Request model for /geocode endpoint"""
    address: str


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {"message": "Community Spark API is running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"ok": True}


@app.get("/secrets-check")
async def secrets_check():
    """
    Demo-only endpoint to check if required secrets are configured.
    
    Returns boolean status for each secret without exposing values.
    Useful for debugging configuration issues.
    """
    from app.utils.openai_helper import openai_client
    
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    return {
        "OPENAI_API_KEY": bool(openai_key),
        "OPENAI_API_KEY_PREFIX": openai_key[:10] if openai_key else "N/A",
        "OPENAI_CLIENT_INITIALIZED": openai_client is not None,
        "PLAID_CLIENT_ID": bool(os.getenv("PLAID_CLIENT_ID", "")),
        "PLAID_SECRET": bool(os.getenv("PLAID_SECRET", ""))
    }


@app.post("/geocode")
async def geocode(request: GeocodeRequest) -> Dict[str, Any]:
    """
    Geocode an address to get latitude, longitude, and formatted address.
    
    Uses Google Geocoding API with GOOGLE_MAPS_BACKEND_KEY environment variable.
    
    Args:
        request: Contains address string to geocode
        
    Returns:
        Dictionary with lat, lng, and formatted_address
        
    Raises:
        400: If address is invalid or not found
        500: If geocoding service fails or API key is not configured
    """
    try:
        result = geocode_address(request.address)
        return result
    except ValueError as e:
        # Client error (bad address, no results, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Server error (API key missing, network error, etc.)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during geocoding: {str(e)}"
        )


@app.get("/passkeys")
async def passkey_page():
    """
    Serve a simple HTML page for WebAuthn registration and authentication.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Spark - Passkey Authentication</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            margin-right: 10px;
            margin-top: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #007bff;
            word-break: break-all;
            white-space: pre-wrap;
        }
        .error {
            border-left-color: #dc3545;
            background: #f8d7da;
            color: #721c24;
        }
        .success {
            border-left-color: #28a745;
            background: #d4edda;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Passkey Authentication</h1>
        
        <div style="background: #e7f3ff; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #2196F3;">
            <strong>ℹ️ Info:</strong> WebAuthn works with both <code>localhost</code> and <code>127.0.0.1</code>.
            <br><br>
            <strong>Current origin:</strong> <code id="currentOrigin"></code>
        </div>
        
        <div class="form-group">
            <label for="user_id">User ID:</label>
            <input type="text" id="user_id" placeholder="user123" value="user123">
        </div>
        
        <div class="form-group">
            <label for="username">Username/Email:</label>
            <input type="text" id="username" placeholder="test@example.com" value="test@example.com">
        </div>
        
        <div class="form-group">
            <label for="display_name">Display Name:</label>
            <input type="text" id="display_name" placeholder="Test User" value="Test User">
        </div>
        
        <button id="registerBtn" onclick="registerPasskey()">Register Passkey</button>
        <button id="signBtn" onclick="signIn()">Sign In / Approve Loan</button>
        
        <div id="result"></div>
    </div>

    <script>
        // Base64url conversion helpers
        function base64urlToArrayBuffer(base64url) {
            const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
            const padded = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=');
            const binary = atob(padded);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) {
                bytes[i] = binary.charCodeAt(i);
            }
            return bytes.buffer;
        }

        function arrayBufferToBase64url(buffer) {
            const bytes = new Uint8Array(buffer);
            let binary = '';
            for (let i = 0; i < bytes.length; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary)
                .replace(/\+/g, '-')
                .replace(/\//g, '_')
                .replace(/=/g, '');
        }

        function showResult(message, isError = false) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'result ' + (isError ? 'error' : 'success');
            resultDiv.textContent = message;
        }

        async function registerPasskey() {
            const user_id = document.getElementById('user_id').value;
            const username = document.getElementById('username').value;
            const display_name = document.getElementById('display_name').value;

            if (!user_id || !username || !display_name) {
                showResult('Please fill in all fields', true);
                return;
            }
            
            // Check WebAuthn support
            if (!window.PublicKeyCredential) {
                showResult('❌ WebAuthn is not supported in this browser. Please use Chrome, Firefox, Edge, or Safari.', true);
                return;
            }
            
            // Check if using localhost
            if (window.location.hostname === '127.0.0.1') {
                showResult('⚠️ Warning: You are using 127.0.0.1. WebAuthn requires localhost. Please access this page via http://localhost:8000', true);
                return;
            }

            try {
                // Get registration options
                const optionsResponse = await fetch('/webauthn/register/options', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id, username, display_name })
                });

                if (!optionsResponse.ok) {
                    const error = await optionsResponse.json();
                    throw new Error(error.detail || 'Failed to get registration options');
                }

                const options = await optionsResponse.json();
                
                // DEBUG: Log the options to see what we're sending
                console.log('Registration options received:', {
                    rp: options.rp,
                    challenge: options.challenge ? 'present' : 'missing',
                    user: options.user,
                    authenticatorSelection: options.authenticatorSelection
                });

                // Convert challenge and user.id from base64url to ArrayBuffer
                options.challenge = base64urlToArrayBuffer(options.challenge);
                options.user.id = base64urlToArrayBuffer(options.user.id);

                // Create credential
                showResult('Creating passkey... (You may be prompted by your browser/OS)');
                console.log('Calling navigator.credentials.create with options:', {
                    rp: options.rp,
                    user: { id: 'ArrayBuffer', name: options.user.name },
                    challenge: 'ArrayBuffer',
                    authenticatorSelection: options.authenticatorSelection
                });
                const credential = await navigator.credentials.create({
                    publicKey: options
                });
                console.log('Credential created successfully:', {
                    id: credential.id,
                    type: credential.type
                });

                // Convert credential to format expected by server
                const credentialForServer = {
                    id: credential.id,
                    rawId: arrayBufferToBase64url(credential.rawId),
                    type: credential.type,
                    response: {
                        clientDataJSON: arrayBufferToBase64url(credential.response.clientDataJSON),
                        attestationObject: arrayBufferToBase64url(credential.response.attestationObject)
                    },
                    user_id: user_id
                };

                // Verify registration
                const verifyResponse = await fetch('/webauthn/register/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credential: credentialForServer })
                });

                const verifyResult = await verifyResponse.json();

                if (verifyResponse.ok && verifyResult.verified) {
                    showResult('✅ Passkey registered successfully!');
                } else {
                    throw new Error(verifyResult.detail || 'Registration verification failed');
                }

            } catch (error) {
                console.error('Registration error:', error);
                console.error('Error name:', error.name);
                console.error('Error message:', error.message);
                let errorMsg = error.message || String(error);
                
                // Provide helpful error messages
                if (error.name === 'NotAllowedError' || errorMsg.includes('not allowed') || errorMsg.includes('The operation')) {
                    errorMsg = '❌ WebAuthn operation was not allowed.\\n\\n' +
                               'Common causes:\\n' +
                               '1. You cancelled the passkey prompt\\n' +
                               '2. The authenticator (1Password/Windows Hello) rejected the request\\n' +
                               '3. A credential for this user already exists in the authenticator\\n' +
                               '4. Browser security settings are blocking WebAuthn\\n\\n' +
                               'For 1Password: Try using a different user_id, or clear existing passkeys for this site in 1Password.\\n' +
                               'For Windows Hello: Try using a different user_id.';
                } else if (errorMsg.includes('timeout')) {
                    errorMsg = '❌ WebAuthn operation timed out.\\n\\n' +
                               'Try: Refresh the page and try again.';
                }
                
                showResult('Registration failed: ' + errorMsg, true);
            }
        }

        async function signIn() {
            const user_id = document.getElementById('user_id').value;

            if (!user_id) {
                showResult('Please enter User ID', true);
                return;
            }
            
            // Check WebAuthn support
            if (!window.PublicKeyCredential) {
                showResult('❌ WebAuthn is not supported in this browser. Please use Chrome, Firefox, Edge, or Safari.', true);
                return;
            }

            try {
                // Get authentication options
                const optionsResponse = await fetch('/webauthn/authenticate/options', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id })
                });

                if (!optionsResponse.ok) {
                    const error = await optionsResponse.json();
                    throw new Error(error.detail || 'Failed to get authentication options');
                }

                const options = await optionsResponse.json();
                
                // DEBUG: Log the authentication options
                console.log('Authentication options received:', {
                    rp: options.rp,
                    challenge: options.challenge ? 'present' : 'missing',
                    allowCredentials: options.allowCredentials ? options.allowCredentials.length + ' credentials' : 'none',
                    userVerification: options.userVerification
                });

                // Convert challenge from base64url to ArrayBuffer
                options.challenge = base64urlToArrayBuffer(options.challenge);

                // Convert allowCredentials IDs
                if (options.allowCredentials) {
                    options.allowCredentials = options.allowCredentials.map(cred => ({
                        ...cred,
                        id: base64urlToArrayBuffer(cred.id)
                    }));
                }

                // Get credential
                showResult('Signing in with passkey... (You may be prompted by your browser/OS)');
                console.log('Calling navigator.credentials.get with options:', {
                    rp: options.rp,
                    challenge: 'ArrayBuffer',
                    allowCredentials: options.allowCredentials ? options.allowCredentials.length + ' credentials' : 'none',
                    userVerification: options.userVerification
                });
                const credential = await navigator.credentials.get({
                    publicKey: options
                });
                console.log('Credential retrieved successfully:', {
                    id: credential.id,
                    type: credential.type
                });

                // Convert credential to format expected by server
                const credentialForServer = {
                    id: credential.id,
                    rawId: arrayBufferToBase64url(credential.rawId),
                    type: credential.type,
                    response: {
                        clientDataJSON: arrayBufferToBase64url(credential.response.clientDataJSON),
                        authenticatorData: arrayBufferToBase64url(credential.response.authenticatorData),
                        signature: arrayBufferToBase64url(credential.response.signature),
                        userHandle: credential.response.userHandle ? arrayBufferToBase64url(credential.response.userHandle) : null
                    },
                    user_id: user_id
                };

                // Verify authentication
                const verifyResponse = await fetch('/webauthn/authenticate/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credential: credentialForServer })
                });

                const verifyResult = await verifyResponse.json();

                if (verifyResponse.ok && verifyResult.ok) {
                    showResult('✅ Signed in successfully!\\n\\nAssertion Token:\\n' + verifyResult.assertion_token);
                } else {
                    throw new Error(verifyResult.detail || 'Authentication verification failed');
                }

            } catch (error) {
                console.error('Authentication error:', error);
                let errorMsg = error.message || String(error);
                
                // Provide helpful error messages
                if (errorMsg.includes('timeout') || errorMsg.includes('not allowed') || errorMsg.includes('The operation')) {
                    errorMsg = '❌ WebAuthn operation timed out or was not allowed.\\n\\n' +
                               'Common causes:\\n' +
                               '1. No passkey registered for this user_id\\n' +
                               '2. Browser security settings are blocking WebAuthn\\n' +
                               '3. You cancelled the passkey prompt\\n' +
                               '4. Network or origin mismatch issues\\n\\n' +
                               'Try: Refresh the page and try again.';
                }
                
                showResult('Authentication failed: ' + errorMsg, true);
            }
        }
    </script>
</body>
</html>"""
    
    return Response(content=html_content, media_type="text/html")


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/register")
async def register(request: RegisterRequest) -> Dict[str, Any]:
    """
    Register a new user account.
    
    Args:
        request: Contains email, username, password, and full_name
        
    Returns:
        Dict with success status and user info
    """
    if not user_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    result = user_manager.register_user(
        email=request.email,
        username=request.username,
        password=request.password,
        full_name=request.full_name
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/auth/login")
async def login(request: LoginRequest) -> Dict[str, Any]:
    """
    Authenticate a user and create a session.
    
    Args:
        request: Contains identifier (email/username) and password
        
    Returns:
        Dict with session token and user info
    """
    if not user_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    result = user_manager.authenticate_user(
        identifier=request.identifier,
        password=request.password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@app.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Logout a user by invalidating their session.
    
    Args:
        authorization: Bearer token from Authorization header
        
    Returns:
        Dict with success status
    """
    if not user_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.replace("Bearer ", "")
    result = user_manager.logout_user(session_token)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.get("/auth/me")
async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Get current user information from session token.
    
    Args:
        authorization: Bearer token from Authorization header
        
    Returns:
        Dict with user info
    """
    if not user_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.replace("Bearer ", "")
    result = user_manager.validate_session(session_token)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@app.post("/auth/connect-bank")
async def connect_bank(
    request: ConnectBankRequest,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Connect a bank account profile to user's account.
    
    This simulates the Plaid Link flow where users would normally connect
    their real bank account. For demo purposes, we connect predefined profiles.
    
    Args:
        request: Contains bank_profile name
        authorization: Bearer token from Authorization header
        
    Returns:
        Dict with success status
    """
    if not user_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.replace("Bearer ", "")
    
    # Validate bank profile exists
    if not get_user_profile(request.bank_profile):
        raise HTTPException(status_code=400, detail=f"Bank profile '{request.bank_profile}' not found")
    
    result = user_manager.connect_bank_account(session_token, request.bank_profile)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/auth/disconnect-bank")
async def disconnect_bank(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Disconnect bank account from user's account.
    
    Args:
        authorization: Bearer token from Authorization header
        
    Returns:
        Dict with success status
    """
    if not user_manager:
        raise HTTPException(status_code=503, detail="Database not available")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    session_token = authorization.replace("Bearer ", "")
    result = user_manager.disconnect_bank_account(session_token)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


# ==================== LOAN EVALUATION ENDPOINTS ====================

@app.post("/evaluate")
async def evaluate(request: EvaluateRequest) -> Dict[str, Any]:
    """
    Evaluate a loan application through the agent pipeline.
    
    Args:
        request: Contains business_profile and bank_data
        
    Returns:
        Evaluation results including decision, terms, rationale, logs, and evaluation_id
    """
    # Basic input validation (hackathon-light)
    if not request.business_profile:
        raise HTTPException(status_code=400, detail="business_profile is required")
    
    if not request.bank_data:
        raise HTTPException(status_code=400, detail="bank_data is required")
    
    # Initialize state with input data and empty log
    initial_state: CommunitySparkState = {
        "bank_data": request.bank_data,
        "business_profile": request.business_profile,
        "log": []
    }
    
    # Invoke the graph workflow
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing evaluation: {str(e)}"
        )
    
    # Generate evaluation ID
    evaluation_id = str(uuid.uuid4())
    
    # Store full evaluation result
    evaluations[evaluation_id] = {
        **final_state,
        "signed": False
    }
    
    # Determine if signature is needed
    final_decision = final_state.get("final_decision")
    needs_signature = final_decision in ["APPROVE", "REFER"]
    
    # Extract and return relevant fields
    return {
        "evaluation_id": evaluation_id,
        "final_decision": final_decision,
        "loan_terms": final_state.get("loan_terms"),
        "decision_rationale": final_state.get("decision_rationale"),
        "auditor_score": final_state.get("auditor_score"),
        "community_multiplier": final_state.get("community_multiplier"),
        "explain": final_state.get("explain"),
        "log": final_state.get("log", []),
        "needs_signature": needs_signature,
        "improvement_plan": final_state.get("improvement_plan")
    }


@app.post("/evaluate/plaid")
async def evaluate_with_plaid(
    request: EvaluatePlaidRequest,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Evaluate a loan application using connected bank account data.
    
    This endpoint demonstrates the full flow:
    1. Validate user session and get connected bank account
    2. Fetch transactions from connected bank profile or Plaid sandbox
    3. Extract financial features from transaction data
    4. Run evaluation through agent pipeline
    
    Args:
        request: Contains business_profile
        authorization: Bearer token (optional - if provided, uses connected bank account)
        
    Returns:
        Evaluation results with used_plaid flag set to true
    """
    # Basic input validation
    if not request.business_profile:
        raise HTTPException(status_code=400, detail="business_profile is required")
    
    # Try to get connected bank account from session
    connected_profile = None
    if authorization and authorization.startswith("Bearer ") and user_manager:
        session_token = authorization.replace("Bearer ", "")
        session_result = user_manager.validate_session(session_token)
        
        if session_result["success"]:
            connected_profile = session_result["user"].get("connected_bank")
    
    # Use connected profile if available, otherwise use request profile or default
    profile_to_use = connected_profile or request.profile
    
    try:
        # Step 1: Get transaction data (either from user profile or Plaid sandbox)
        if profile_to_use:
            # Use predefined user profile
            profile_data = get_user_profile(profile_to_use)
            if not profile_data:
                raise HTTPException(status_code=400, detail=f"Profile '{profile_to_use}' not found")
            
            # Convert profile to Plaid format
            plaid_data = convert_profile_to_plaid_format(profile_data)
            data_source = f"Connected Bank Account ({profile_to_use})"
        else:
            # Fetch transactions from Plaid sandbox (default)
            # Uses environment variables: PLAID_CLIENT_ID, PLAID_SECRET
            plaid_data = await plaid_sandbox_get_transactions(
                start_date="2023-01-01",
                end_date="2024-01-01"
            )
            data_source = "Plaid Sandbox (Demo)"
        
        # Step 2: Extract bank features from Plaid transaction data
        bank_data = extract_bank_features(plaid_data)
        
        # Add a default traditional_credit_score if not present
        # (In production, this would come from credit bureau or be calculated)
        if "traditional_credit_score" not in bank_data:
            bank_data["traditional_credit_score"] = 650  # Default middle-range score
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Plaid data: {str(e)}"
        )
    
    # Step 3: Initialize state with extracted data
    initial_state: CommunitySparkState = {
        "bank_data": bank_data,
        "business_profile": request.business_profile,
        "log": []
    }
    
    # Step 4: Invoke the graph workflow
    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing evaluation: {str(e)}"
        )
    
    # Step 5: Generate evaluation ID and store result
    evaluation_id = str(uuid.uuid4())
    
    # Store full evaluation result
    evaluations[evaluation_id] = {
        **final_state,
        "signed": False
    }
    
    # Determine if signature is needed
    final_decision = final_state.get("final_decision")
    needs_signature = final_decision in ["APPROVE", "REFER"]
    
    # Step 6: Extract and return relevant fields
    return {
        "evaluation_id": evaluation_id,
        "final_decision": final_decision,
        "loan_terms": final_state.get("loan_terms"),
        "decision_rationale": final_state.get("decision_rationale"),
        "auditor_score": final_state.get("auditor_score"),
        "community_multiplier": final_state.get("community_multiplier"),
        "explain": final_state.get("explain"),
        "log": final_state.get("log", []),
        "needs_signature": needs_signature,
        "used_plaid": True,
        "data_source": data_source,  # Show where data came from
        "extracted_features": bank_data,  # Include the extracted features for transparency
        "improvement_plan": final_state.get("improvement_plan")
    }


@app.post("/finalize")
async def finalize(request: FinalizeRequest) -> Dict[str, Any]:
    """
    Finalize a loan evaluation with passkey signature.
    
    Verifies the assertion token and marks the evaluation as signed.
    Returns the final loan terms if the evaluation was approved.
    
    Args:
        request: Contains evaluation_id and assertion_token
        
    Returns:
        Final loan terms and signed status, or 401 if token invalid
    """
    # Verify assertion token
    try:
        token_data = verify_token(request.assertion_token)
        user_id = token_data["user_id"]
    except HTTPException:
        raise  # Re-raise HTTPException from verify_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    
    # Get evaluation
    evaluation = evaluations.get(request.evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Check if already signed
    if evaluation.get("signed"):
        raise HTTPException(status_code=400, detail="Evaluation already signed")
    
    # Mark as signed
    evaluation["signed"] = True
    evaluation["signed_by"] = user_id
    evaluation["signed_at"] = time.time()
    
    # Return final loan terms
    final_decision = evaluation.get("final_decision")
    
    if final_decision == "APPROVE":
        return {
            "signed": True,
            "final_decision": final_decision,
            "loan_terms": evaluation.get("loan_terms"),
            "decision_rationale": evaluation.get("decision_rationale"),
            "signed_by": user_id
        }
    elif final_decision == "REFER":
        return {
            "signed": True,
            "final_decision": final_decision,
            "decision_rationale": evaluation.get("decision_rationale"),
            "message": "Evaluation signed and referred for manual review",
            "signed_by": user_id
        }
    else:
        # DENY - no loan terms to return
        return {
            "signed": True,
            "final_decision": final_decision,
            "decision_rationale": evaluation.get("decision_rationale"),
            "message": "Evaluation signed (denied)",
            "signed_by": user_id
        }

