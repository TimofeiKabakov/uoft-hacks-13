"""
Dummy Authentication System

Simple authentication for demo/sandbox purposes.
Uses a single hardcoded sandbox user that automatically connects to Plaid sandbox.
"""
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class DummyUser(BaseModel):
    """Dummy user for sandbox/demo"""
    id: str = "sandbox-user-001"
    email: str = "sandbox@demo.com"
    name: str = "Sandbox User"
    created_at: datetime = datetime.now()


class DummyAuthService:
    """
    Simple authentication service for demo purposes

    This is a minimal auth system that returns a hardcoded sandbox user.
    In production, this would be replaced with proper JWT authentication.
    """

    SANDBOX_USER = DummyUser()

    @classmethod
    def login(cls, email: str, password: str = None) -> Optional[DummyUser]:
        """
        Dummy login that always returns the sandbox user

        Args:
            email: Any email (ignored)
            password: Any password (ignored)

        Returns:
            Sandbox user
        """
        # For demo purposes, any login succeeds with sandbox user
        return cls.SANDBOX_USER

    @classmethod
    def register(cls, email: str, name: str, password: str = None) -> DummyUser:
        """
        Dummy registration that always returns the sandbox user

        Args:
            email: Any email (ignored)
            name: Any name (ignored)
            password: Any password (ignored)

        Returns:
            Sandbox user
        """
        # For demo purposes, registration always returns sandbox user
        return cls.SANDBOX_USER

    @classmethod
    def get_current_user(cls) -> DummyUser:
        """
        Get the current authenticated user (always sandbox user)

        Returns:
            Sandbox user
        """
        return cls.SANDBOX_USER

    @classmethod
    def create_token(cls, user_id: str) -> str:
        """
        Create a dummy auth token

        Args:
            user_id: User ID (ignored)

        Returns:
            Dummy token string
        """
        return f"sandbox-token-{datetime.now().timestamp()}"
