from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI settings
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    
    # Application settings
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    max_image_size_mb: int = Field(5, alias="MAX_IMAGE_SIZE_MB")
    supported_image_formats: List[str] = Field(
        ["jpg", "jpeg", "png", "gif"],
        alias="SUPPORTED_IMAGE_FORMATS"
    )
    
    model_config = SettingsConfigDict(
        env_file="../../config/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class ImageAnalysisRequest(BaseModel):
    """Model for image analysis request parameters."""
    
    image_path: Path
    prompt: str = Field(..., description="The prompt to guide the image analysis")
    max_tokens: int = Field(300, description="Maximum tokens in the response")


class ImageAnalysisResponse(BaseModel):
    """Model for image analysis response."""
    
    analysis: str
    model_used: str
    processing_time: float 