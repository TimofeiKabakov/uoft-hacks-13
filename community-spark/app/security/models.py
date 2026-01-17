"""
WebAuthn In-Memory Data Stores

Demo-only implementation using in-memory dictionaries.
In production, these should be replaced with a proper database.

This module provides minimal data stores for:
- User accounts
- WebAuthn credentials
- Authentication challenges
"""

from typing import Dict, List, Any, Optional

# ========== IN-MEMORY DATA STORES (DEMO ONLY) ==========

# User store: user_id -> user info
users: Dict[str, Dict[str, Any]] = {}
"""
In-memory user store.
Format: {
    "user_id": {
        "id": "user_id",
        "username": "user@example.com",
        "display_name": "User Name"
    }
}

WARNING: This is demo-only. In production, use a proper database.
"""

# Credentials store: user_id -> list of credential dicts
credentials: Dict[str, List[Dict[str, Any]]] = {}
"""
In-memory WebAuthn credentials store.
Format: {
    "user_id": [
        {
            "id": bytes,  # credential_id
            "public_key": bytes,  # credential_public_key
            "sign_count": int,  # signature counter
            "transports": List[str],  # ["usb", "nfc", "ble", "internal"]
            # ... other credential metadata
        }
    ]
}

WARNING: This is demo-only. In production, use a proper database.
"""

# Challenges store: user_id -> challenge data
challenges: Dict[str, Dict[str, Any]] = {}
"""
In-memory challenge store for WebAuthn registration and authentication.
Format: {
    "user_id": {
        "register_challenge_bytes": bytes,  # Registration challenge
        "auth_challenge_bytes": bytes,  # Authentication challenge
        "challenge_expiry": float,  # Timestamp when challenge expires
    }
}

WARNING: This is demo-only. In production, use a proper database with TTL.
"""


# ========== HELPER FUNCTIONS ==========

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user by ID.
    
    Args:
        user_id: User identifier
        
    Returns:
        User dict or None if not found
    """
    return users.get(user_id)


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Get user by username.
    
    Args:
        username: Username/email
        
    Returns:
        User dict or None if not found
    """
    for user in users.values():
        if user.get("username") == username:
            return user
    return None


def create_user(user_id: str, username: str, display_name: str) -> Dict[str, Any]:
    """
    Create a new user.
    
    Args:
        user_id: Unique user identifier
        username: Username/email
        display_name: Display name
        
    Returns:
        Created user dict
    """
    user = {
        "id": user_id,
        "username": username,
        "display_name": display_name
    }
    users[user_id] = user
    credentials[user_id] = []  # Initialize empty credentials list
    return user


def get_user_credentials(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all credentials for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of credential dicts
    """
    return credentials.get(user_id, [])


def add_user_credential(user_id: str, credential: Dict[str, Any]) -> None:
    """
    Add a credential to a user.
    
    Args:
        user_id: User identifier
        credential: Credential dict to add
    """
    if user_id not in credentials:
        credentials[user_id] = []
    credentials[user_id].append(credential)


def get_challenge(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get challenge data for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        Challenge dict or None if not found
    """
    return challenges.get(user_id)


def set_challenge(user_id: str, challenge_data: Dict[str, Any]) -> None:
    """
    Set challenge data for a user.
    
    Args:
        user_id: User identifier
        challenge_data: Challenge dict to store
    """
    challenges[user_id] = challenge_data


def clear_challenge(user_id: str) -> None:
    """
    Clear challenge data for a user.
    
    Args:
        user_id: User identifier
    """
    if user_id in challenges:
        del challenges[user_id]

