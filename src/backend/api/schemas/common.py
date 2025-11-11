"""
Common API Schemas.

Base schemas used across multiple endpoints.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """
    Simple message response.
    """

    message: str = Field(..., description="Response message")
    success: bool = Field(True, description="Whether operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class ErrorResponse(BaseModel):
    """
    Error response.
    """

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class PaginationParams(BaseModel):
    """
    Pagination parameters.
    """

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field(
        "asc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"
    )


class PaginatedResponse(BaseModel):
    """
    Paginated response wrapper.
    """

    items: list = Field(..., description="Items in current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
