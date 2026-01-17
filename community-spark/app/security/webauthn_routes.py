"""
WebAuthn Routes for Passwordless Authentication

Implements WebAuthn registration and authentication flows.
Uses in-memory storage (demo-only).
"""

import os
import hmac
import hashlib
import json
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
    AuthenticatorTransport,
    AttestationConveyancePreference,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from app.security import models

router = APIRouter(prefix="/webauthn", tags=["webauthn"])

# WebAuthn configuration
RP_NAME = "Community Spark"

def get_rp_config(request: Request) -> tuple[str, str]:
    """
    Get rp_id and expected_origin from request.
    Supports both localhost and 127.0.0.1.
    
    For same-origin requests, the origin header might be missing,
    so we construct it from the host header.
    """
    host = request.headers.get("host", "localhost:8000")
    hostname = host.split(":")[0]
    
    # For same-origin requests, origin header might be missing
    # So we construct it from the host header
    scheme = "http"  # For localhost, always HTTP
    expected_origin = f"{scheme}://{host}"
    
    # rp_id must be exactly the hostname (no port, no scheme)
    # For localhost/127.0.0.1, use the hostname as-is
    rp_id = hostname
    
    return rp_id, expected_origin

# Token configuration
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour
HMAC_SECRET = os.getenv("PASSKEY_HMAC_SECRET", "dev-secret-change-in-production")


# ========== REQUEST/RESPONSE MODELS ==========

class RegisterOptionsRequest(BaseModel):
    user_id: str
    username: str
    display_name: str


class VerifyCredentialRequest(BaseModel):
    """Generic model for credential responses from browser"""
    credential: Dict[str, Any]  # The PublicKeyCredential JSON


class AuthenticateOptionsRequest(BaseModel):
    user_id: str


# ========== TOKEN UTILITIES ==========

def generate_token(user_id: str) -> str:
    """
    Generate a simple HMAC-signed token.
    
    Token format: base64(user_id:exp_timestamp:hmac_signature)
    
    Args:
        user_id: User identifier
        
    Returns:
        Signed token string
    """
    exp = int(time.time()) + TOKEN_EXPIRY_SECONDS
    payload = f"{user_id}:{exp}"
    
    # Create HMAC signature
    signature = hmac.new(
        HMAC_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    token = f"{payload}:{signature}"
    return token


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a token.
    
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


# ========== REGISTRATION ENDPOINTS ==========

@router.post("/register/options")
async def register_options(
    request: RegisterOptionsRequest,
    http_request: Request
) -> Dict[str, Any]:
    """
    Generate WebAuthn registration options.
    
    Creates user if not exists and returns registration options
    for the browser to create a credential.
    """
    # Get rp_id and origin from request
    rp_id, expected_origin = get_rp_config(http_request)
    
    # Create user if not exists
    user = models.get_user(request.user_id)
    if not user:
        user = models.create_user(
            user_id=request.user_id,
            username=request.username,
            display_name=request.display_name
        )
    
    # Check if user already has credentials - if so, exclude them
    existing_credentials = models.get_user_credentials(request.user_id)
    exclude_credentials = [
        PublicKeyCredentialDescriptor(id=cred["id"])
        for cred in existing_credentials
    ] if existing_credentials else []
    
    print(f"[DEBUG] Register options - user_id: {request.user_id}, rp_id: {rp_id}, expected_origin: {expected_origin}")
    print(f"[DEBUG] Excluding {len(exclude_credentials)} existing credentials")
    
    # Generate registration options
    # Using most permissive settings for maximum compatibility with Windows Hello, 1Password, etc.
    options = generate_registration_options(
        rp_id=rp_id,
        rp_name=RP_NAME,
        user_id=request.user_id.encode('utf-8'),
        user_name=request.username,
        user_display_name=request.display_name,
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            # No authenticatorAttachment - allows both platform and cross-platform authenticators
            resident_key=ResidentKeyRequirement.PREFERRED,  # Preferred, not required
            user_verification=UserVerificationRequirement.PREFERRED,  # Preferred, not required
        ),
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,  # Most common
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,  # Backup
        ],
        exclude_credentials=exclude_credentials,  # Prevent duplicate registrations
    )
    
    # Store challenge for verification (also store rp_id and origin for verification)
    models.set_challenge(request.user_id, {
        "register_challenge_bytes": options.challenge,
        "challenge_expiry": time.time() + 300,  # 5 minutes
        "rp_id": rp_id,
        "expected_origin": expected_origin
    })
    
    # Convert options to JSON
    return json.loads(options_to_json(options))


@router.post("/register/verify")
async def register_verify(
    request: VerifyCredentialRequest,
    http_request: Request
) -> Dict[str, Any]:
    """
    Verify WebAuthn registration response.
    
    Stores the credential for future authentication.
    """
    try:
        credential = request.credential
        
        # Extract user_id from credential response
        # The user handle is base64url encoded in the response
        response_data = credential.get("response", {})
        
        # Get user_id from the credential (it's in the response during registration)
        # For registration, we need to find the user by looking at stored challenges
        # In a real app, you'd associate this with a session
        
        # For demo purposes, let's extract from the credential or require it in request
        # Actually, let's require user_id in the request body
        user_id = credential.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required in credential")
        
        # Get stored challenge
        challenge_data = models.get_challenge(user_id)
        if not challenge_data:
            raise HTTPException(status_code=400, detail="No registration challenge found")
        
        # Check challenge expiry
        if time.time() > challenge_data.get("challenge_expiry", 0):
            models.clear_challenge(user_id)
            raise HTTPException(status_code=400, detail="Challenge expired")
        
        # Get rp_id and origin (use stored values if available, otherwise from request)
        rp_id = challenge_data.get("rp_id") or get_rp_config(http_request)[0]
        expected_origin = challenge_data.get("expected_origin") or get_rp_config(http_request)[1]
        
        # Verify the registration response
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_data["register_challenge_bytes"],
            expected_rp_id=rp_id,
            expected_origin=expected_origin,
        )
        
        # Store the credential
        credential_data = {
            "id": verification.credential_id,
            "public_key": verification.credential_public_key,
            "sign_count": verification.sign_count,
            "credential_type": verification.credential_type,
            "credential_device_type": verification.credential_device_type,
            "credential_backed_up": verification.credential_backed_up,
        }
        
        models.add_user_credential(user_id, credential_data)
        models.clear_challenge(user_id)
        
        return {
            "verified": True,
            "message": "Registration successful"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration verification failed: {str(e)}")


# ========== AUTHENTICATION ENDPOINTS ==========

@router.post("/authenticate/options")
async def authenticate_options(
    request: AuthenticateOptionsRequest,
    http_request: Request
) -> Dict[str, Any]:
    """
    Generate WebAuthn authentication options.
    
    Returns challenge and allowed credentials for authentication.
    """
    # Get rp_id and origin from request
    rp_id, expected_origin = get_rp_config(http_request)
    
    # Get user credentials
    user_credentials = models.get_user_credentials(request.user_id)
    if not user_credentials:
        raise HTTPException(status_code=404, detail="No credentials found for user")
    
    # Build allow_credentials list
    # Include ALL transport types to support:
    # - INTERNAL: Windows Hello, Touch ID, Face ID (platform authenticators)
    # - USB/NFC/BLE: Physical security keys
    # - HYBRID: 1Password and other cross-platform authenticators
    allow_credentials = [
        PublicKeyCredentialDescriptor(
            id=cred["id"],
            # Include all transports to support Windows Hello, 1Password, and security keys
            transports=[
                AuthenticatorTransport.USB,
                AuthenticatorTransport.NFC,
                AuthenticatorTransport.BLE,
                AuthenticatorTransport.INTERNAL,  # Windows Hello, Touch ID, Face ID
                AuthenticatorTransport.HYBRID,    # 1Password and similar
            ]
        )
        for cred in user_credentials
    ]
    
    # Generate authentication options
    # Use permissive settings to allow any available authenticator
    options = generate_authentication_options(
        rp_id=rp_id,
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.PREFERRED,  # Preferred, not required
    )
    
    # Store challenge for verification (also store rp_id and origin for verification)
    challenge_data = models.get_challenge(request.user_id) or {}
    challenge_data.update({
        "auth_challenge_bytes": options.challenge,
        "challenge_expiry": time.time() + 300,  # 5 minutes
        "rp_id": rp_id,
        "expected_origin": expected_origin
    })
    models.set_challenge(request.user_id, challenge_data)
    
    # Convert options to JSON
    return json.loads(options_to_json(options))


@router.post("/authenticate/verify")
async def authenticate_verify(
    request: VerifyCredentialRequest,
    http_request: Request
) -> Dict[str, Any]:
    """
    Verify WebAuthn authentication response.
    
    Returns a signed token on successful authentication.
    """
    try:
        credential = request.credential
        
        # Extract user_id (require it in request for demo)
        user_id = credential.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id required in credential")
        
        # Get stored challenge
        challenge_data = models.get_challenge(user_id)
        if not challenge_data or "auth_challenge_bytes" not in challenge_data:
            raise HTTPException(status_code=400, detail="No authentication challenge found")
        
        # Check challenge expiry
        if time.time() > challenge_data.get("challenge_expiry", 0):
            models.clear_challenge(user_id)
            raise HTTPException(status_code=400, detail="Challenge expired")
        
        # Get rp_id and origin (use stored values if available, otherwise from request)
        rp_id = challenge_data.get("rp_id") or get_rp_config(http_request)[0]
        expected_origin = challenge_data.get("expected_origin") or get_rp_config(http_request)[1]
        
        # Find the credential being used
        # The credential_id from browser is base64url string, need to convert to bytes
        credential_id_b64 = credential.get("rawId") or credential.get("id")
        
        # Convert base64url to bytes for comparison
        import base64
        try:
            # Add padding if needed for base64url
            credential_id_bytes = base64.urlsafe_b64decode(credential_id_b64 + "==")
        except Exception as e:
            print(f"[ERROR] Failed to decode credential_id: {credential_id_b64}, error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid credential ID format: {str(e)}")
        
        user_credentials = models.get_user_credentials(user_id)
        
        print(f"[DEBUG] Auth verify - user_id: {user_id}")
        print(f"[DEBUG] Looking for credential_id: {credential_id_bytes.hex()}")
        print(f"[DEBUG] User has {len(user_credentials)} stored credentials")
        
        matching_cred = None
        for i, cred in enumerate(user_credentials):
            stored_id_hex = cred["id"].hex() if isinstance(cred["id"], bytes) else cred["id"]
            print(f"[DEBUG] Credential {i}: {stored_id_hex}")
            
            # Compare credential IDs (both as bytes)
            if cred["id"] == credential_id_bytes:
                matching_cred = cred
                print(f"[DEBUG] Found matching credential at index {i}")
                break
        
        if not matching_cred:
            print(f"[ERROR] Credential not found for user {user_id}")
            print(f"[ERROR] Searched for: {credential_id_bytes.hex()}")
            print(f"[ERROR] Available credentials: {[c['id'].hex() for c in user_credentials]}")
            raise HTTPException(status_code=400, detail="Credential not found")
        
        # Verify the authentication response
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge_data["auth_challenge_bytes"],
            expected_rp_id=rp_id,
            expected_origin=expected_origin,
            credential_public_key=matching_cred["public_key"],
            credential_current_sign_count=matching_cred["sign_count"],
        )
        
        # Update sign count
        matching_cred["sign_count"] = verification.new_sign_count
        
        # Clear challenge
        models.clear_challenge(user_id)
        
        # Generate token
        token = generate_token(user_id)
        
        return {
            "ok": True,
            "assertion_token": token,
            "user_id": user_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication verification failed: {str(e)}")
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

                // Convert challenge and user.id from base64url to ArrayBuffer
                options.challenge = base64urlToArrayBuffer(options.challenge);
                options.user.id = base64urlToArrayBuffer(options.user.id);

                // Create credential
                const credential = await navigator.credentials.create({
                    publicKey: options
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
                showResult('❌ Error: ' + error.message, true);
                console.error('Registration error:', error);
            }
        }

        async function signIn() {
            const user_id = document.getElementById('user_id').value;

            if (!user_id) {
                showResult('Please enter User ID', true);
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
                const credential = await navigator.credentials.get({
                    publicKey: options
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
                showResult('❌ Error: ' + error.message, true);
                console.error('Authentication error:', error);
            }
        }
    </script>
</body>
</html>"""
    
    return Response(content=html_content, media_type="text/html")

