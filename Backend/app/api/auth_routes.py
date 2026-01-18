"""
Authentication Routes

Dummy authentication endpoints for sandbox/demo use
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.core.auth import DummyAuthService
from app.models.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    user: UserResponse
    token: str
    message: str


class RegisterRequest(BaseModel):
    """Register request"""
    email: EmailStr
    name: str
    password: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Dummy login endpoint

    For sandbox/demo purposes, any credentials will log you in
    as the sandbox user. This user is automatically connected
    to Plaid sandbox environment.

    Args:
        request: Login credentials (any email/password accepted)

    Returns:
        Login response with sandbox user and token
    """
    user = DummyAuthService.login(request.email, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = DummyAuthService.create_token(user.id)

    return LoginResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        ),
        token=token,
        message="Logged in as sandbox user. Connected to Plaid sandbox environment."
    )


@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """
    Dummy register endpoint

    For sandbox/demo purposes, registration always returns the
    sandbox user. This user is automatically connected to Plaid
    sandbox environment.

    Args:
        request: Registration details (ignored in sandbox mode)

    Returns:
        Login response with sandbox user and token
    """
    user = DummyAuthService.register(request.email, request.name, request.password)

    token = DummyAuthService.create_token(user.id)

    return LoginResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        ),
        token=token,
        message="Registered as sandbox user. Connected to Plaid sandbox environment."
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """
    Get current authenticated user

    For sandbox/demo purposes, always returns the sandbox user.

    Returns:
        Current user (sandbox user)
    """
    user = DummyAuthService.get_current_user()

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at
    )
