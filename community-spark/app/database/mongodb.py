"""
MongoDB Atlas Connection and User Management

Handles database connections, user authentication, and bank account linking.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

load_dotenv()

# MongoDB Atlas connection
MONGODB_URI = os.getenv("MONGODB_URI", "")
DATABASE_NAME = "community_spark"

# Initialize MongoDB client
client = None
db = None

if MONGODB_URI:
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        # Test connection
        client.admin.command('ping')
        print("[INFO] Successfully connected to MongoDB Atlas")
    except Exception as e:
        print(f"[ERROR] Failed to connect to MongoDB: {e}")
        client = None
        db = None
else:
    print("[WARNING] MONGODB_URI not set. Database features will be disabled.")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_session_token() -> str:
    """Generate a secure session token."""
    return secrets.token_urlsafe(32)


class UserManager:
    """Manages user accounts and authentication."""
    
    def __init__(self):
        self.users = db.users if db is not None else None
        self.sessions = db.sessions if db is not None else None
        
        # Create indexes
        if self.users is not None:
            self.users.create_index("email", unique=True)
            self.users.create_index("username", unique=True)
        if self.sessions is not None:
            self.sessions.create_index("token", unique=True)
            self.sessions.create_index("expires_at")
    
    def register_user(self, email: str, username: str, password: str, full_name: str = "") -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: User's full name (optional)
            
        Returns:
            Dict with success status and message
        """
        if self.users is None:
            return {"success": False, "error": "Database not available"}
        
        try:
            user_doc = {
                "email": email.lower().strip(),
                "username": username.lower().strip(),
                "password_hash": hash_password(password),
                "full_name": full_name,
                "created_at": datetime.utcnow(),
                "connected_bank": None,  # Will store profile name when bank is connected
                "bank_connected_at": None,
                "last_login": None
            }
            
            result = self.users.insert_one(user_doc)
            return {
                "success": True,
                "user_id": str(result.inserted_id),
                "message": "Account created successfully"
            }
        except DuplicateKeyError as e:
            if "email" in str(e):
                return {"success": False, "error": "Email already registered"}
            elif "username" in str(e):
                return {"success": False, "error": "Username already taken"}
            else:
                return {"success": False, "error": "Account already exists"}
        except Exception as e:
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def authenticate_user(self, identifier: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user by email/username and password.
        
        Args:
            identifier: Email or username
            password: Plain text password
            
        Returns:
            Dict with success status, session token, and user info
        """
        if self.users is None or self.sessions is None:
            return {"success": False, "error": "Database not available"}
        
        try:
            identifier = identifier.lower().strip()
            password_hash = hash_password(password)
            
            # Find user by email or username
            user = self.users.find_one({
                "$or": [
                    {"email": identifier},
                    {"username": identifier}
                ],
                "password_hash": password_hash
            })
            
            if not user:
                return {"success": False, "error": "Invalid credentials"}
            
            # Update last login
            self.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Create session
            session_token = generate_session_token()
            expires_at = datetime.utcnow() + timedelta(days=7)  # 7 day session
            
            self.sessions.insert_one({
                "token": session_token,
                "user_id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "created_at": datetime.utcnow(),
                "expires_at": expires_at
            })
            
            return {
                "success": True,
                "session_token": session_token,
                "user": {
                    "user_id": str(user["_id"]),
                    "email": user["email"],
                    "username": user["username"],
                    "full_name": user.get("full_name", ""),
                    "connected_bank": user.get("connected_bank"),
                    "bank_connected_at": user.get("bank_connected_at")
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """
        Validate a session token and return user info.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Dict with success status and user info
        """
        if self.sessions is None or self.users is None:
            return {"success": False, "error": "Database not available"}
        
        try:
            session = self.sessions.find_one({
                "token": session_token,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if session is None:
                return {"success": False, "error": "Invalid or expired session"}
            
            # Get user data
            user = self.users.find_one({"email": session["email"]})
            
            if user is None:
                return {"success": False, "error": "User not found"}
            
            return {
                "success": True,
                "user": {
                    "user_id": str(user["_id"]),
                    "email": user["email"],
                    "username": user["username"],
                    "full_name": user.get("full_name", ""),
                    "connected_bank": user.get("connected_bank"),
                    "bank_connected_at": user.get("bank_connected_at")
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Session validation failed: {str(e)}"}
    
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """
        Logout a user by deleting their session.
        
        Args:
            session_token: Session token to delete
            
        Returns:
            Dict with success status
        """
        if self.sessions is None:
            return {"success": False, "error": "Database not available"}
        
        try:
            result = self.sessions.delete_one({"token": session_token})
            
            if result.deleted_count > 0:
                return {"success": True, "message": "Logged out successfully"}
            else:
                return {"success": False, "error": "Session not found"}
        except Exception as e:
            return {"success": False, "error": f"Logout failed: {str(e)}"}
    
    def connect_bank_account(self, session_token: str, bank_profile: str) -> Dict[str, Any]:
        """
        Connect a bank account profile to a user's account.
        
        Args:
            session_token: User's session token
            bank_profile: Name of the bank profile (e.g., "bad_habit_user")
            
        Returns:
            Dict with success status
        """
        if self.sessions is None or self.users is None:
            return {"success": False, "error": "Database not available"}
        
        try:
            # Validate session
            session = self.sessions.find_one({
                "token": session_token,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not session:
                return {"success": False, "error": "Invalid or expired session"}
            
            # Update user's connected bank
            result = self.users.update_one(
                {"email": session["email"]},
                {
                    "$set": {
                        "connected_bank": bank_profile,
                        "bank_connected_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": f"Successfully connected {bank_profile}",
                    "bank_profile": bank_profile
                }
            else:
                return {"success": False, "error": "Failed to update user"}
        except Exception as e:
            return {"success": False, "error": f"Bank connection failed: {str(e)}"}
    
    def disconnect_bank_account(self, session_token: str) -> Dict[str, Any]:
        """
        Disconnect bank account from user's account.
        
        Args:
            session_token: User's session token
            
        Returns:
            Dict with success status
        """
        if self.sessions is None or self.users is None:
            return {"success": False, "error": "Database not available"}
        
        try:
            session = self.sessions.find_one({
                "token": session_token,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if session is None:
                return {"success": False, "error": "Invalid or expired session"}
            
            result = self.users.update_one(
                {"email": session["email"]},
                {
                    "$set": {
                        "connected_bank": None,
                        "bank_connected_at": None
                    }
                }
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "Bank account disconnected"}
            else:
                return {"success": False, "error": "Failed to update user"}
        except Exception as e:
            return {"success": False, "error": f"Disconnection failed: {str(e)}"}


# Global user manager instance
user_manager = UserManager() if db is not None else None

