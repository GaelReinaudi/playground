import base64
import time
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

from openai import OpenAI
from PIL import Image

from config import Settings, ImageAnalysisRequest, ImageAnalysisResponse


class VisionAnalyzer:
    """A class to handle image analysis using OpenAI's GPT-4 Vision API."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the vision analyzer with settings."""
        self.settings = settings or Settings()
        self.client = OpenAI()  # Will use OPENAI_API_KEY from environment

    def _is_url(self, path: str) -> bool:
        """Check if the given path is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _prepare_image_content(self, image_path: Union[str, Path]) -> dict:
        """
        Prepare image content for the API request.
        Handles both URLs and local files.
        """
        image_path_str = str(image_path)
        
        if self._is_url(image_path_str):
            return {"url": image_path_str}
        
        # For local files, validate and encode
        path = Path(image_path)
        self._validate_image(path)
        base64_image = self._encode_image(path)
        return {"url": f"data:image/jpeg;base64,{base64_image}"}

    def _encode_image(self, image_path: Path) -> str:
        """
        Encode an image file to base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _validate_image(self, image_path: Path) -> None:
        """
        Validate the image file.
        
        Args:
            image_path: Path to the image file
            
        Raises:
            ValueError: If the image is invalid or too large
        """
        if not image_path.exists():
            raise ValueError(f"Image file not found: {image_path}")

        if image_path.suffix[1:].lower() not in self.settings.supported_image_formats:
            raise ValueError(
                f"Unsupported image format. Supported formats: {self.settings.supported_image_formats}"
            )

        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.settings.max_image_size_mb:
            raise ValueError(
                f"Image size ({file_size_mb:.1f}MB) exceeds maximum allowed size "
                f"({self.settings.max_image_size_mb}MB)"
            )

        # Validate image can be opened
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")

    def analyze_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        max_tokens: int = 300
    ) -> ImageAnalysisResponse:
        """
        Analyze an image using GPT-4 Vision.
        
        Args:
            image_path: Path to the image file or URL
            prompt: The prompt to guide the image analysis
            max_tokens: Maximum tokens in the response
            
        Returns:
            ImageAnalysisResponse with the analysis results
        """
        request = ImageAnalysisRequest(
            image_path=str(image_path),
            prompt=prompt,
            max_tokens=max_tokens
        )
        
        image_content = self._prepare_image_content(image_path)
        start_time = time.time()
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": request.prompt},
                        {
                            "type": "image_url",
                            "image_url": image_content
                        }
                    ]
                }
            ],
            max_tokens=request.max_tokens
        )
        
        processing_time = time.time() - start_time
        
        return ImageAnalysisResponse(
            analysis=response.choices[0].message.content,
            model_used=response.model,
            processing_time=processing_time
        ) 