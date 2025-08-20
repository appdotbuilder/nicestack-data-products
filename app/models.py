from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class DataProduct(SQLModel, table=True):
    """Data product model representing Unity Catalog schemas."""

    __tablename__ = "data_products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    schema_name: str = Field(max_length=255, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    owner: str = Field(max_length=255)
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for validation and API operations
class DataProductCreate(SQLModel, table=False):
    """Schema for creating new data products."""

    schema_name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    owner: str = Field(max_length=255)
    creation_date: Optional[datetime] = Field(default=None)


class DataProductUpdate(SQLModel, table=False):
    """Schema for updating existing data products."""

    schema_name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    owner: Optional[str] = Field(default=None, max_length=255)
    creation_date: Optional[datetime] = Field(default=None)


class DataProductResponse(SQLModel, table=False):
    """Schema for API responses containing data product information."""

    id: int
    schema_name: str
    description: Optional[str]
    owner: str
    creation_date: datetime
    created_at: datetime
    updated_at: datetime
