"""
Pydantic models / schemas for request and response validation.
"""
from typing import Optional

from pydantic import BaseModel, Field


# ─── Auth Schemas ────────────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    """Schema for user login request."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=4, max_length=100, description="Password")


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    username: Optional[str] = None


# ─── Analysis Schemas ────────────────────────────────────────────────────────────
class AnalysisResponse(BaseModel):
    """Schema for the analysis endpoint response."""
    sector: str
    report: str                       # markdown report content
    generated_at: str
    sources_count: int
    status: str = "success"


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    status: str = "error"


class HealthResponse(BaseModel):
    """Schema for health check."""
    status: str = "healthy"
    version: str
    timestamp: str
