from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
import re


class UserCreate(BaseModel):
    """Schema for creating a new user with comprehensive validation."""
    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username: 3-20 chars, alphanumeric, underscore, hyphen only"
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password: min 8 chars, must contain uppercase, lowercase, and number"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username doesn't start with special chars."""
        if v[0] in "_-":
            raise ValueError("Username cannot start with underscore or hyphen")
        return v.strip()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength (uppercase, lowercase, number)."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRead(BaseModel):
    """Schema for reading user data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0, description="User ID must be positive")
    username: str
    email: EmailStr
    avatar_url: str | None = Field(None, description="URL to user's avatar image")
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating user data with optional fields."""
    username: str | None = Field(
        None,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]*$",
        description="Username: 3-20 chars, alphanumeric, underscore, hyphen"
    )
    email: EmailStr | None = None
    password: str | None = Field(
        None,
        min_length=8,
        max_length=128,
        description="Password: min 8 chars, must contain uppercase, lowercase, and number"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate username format when provided."""
        if v and v[0] in "_-":
            raise ValueError("Username cannot start with underscore or hyphen")
        return v.strip() if v else None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """Validate password strength when provided."""
        if not v:
            return None
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    @model_validator(mode="after")
    def check_at_least_one_field(self):
        """Ensure at least one field is provided for update."""
        if not any([self.username, self.email, self.password]):
            raise ValueError("At least one field must be provided for update")
        return self


class AvatarUploadResponse(BaseModel):
    """Response after uploading user avatar."""
    message: str
    avatar_url: str = Field(description="URL to the uploaded avatar")
    file_size: int = Field(description="Size of uploaded file in bytes")