import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.vision_analyzer import VisionAnalyzer
from src.config import Settings, ImageAnalysisResponse


@pytest.fixture
def mock_settings():
    return Settings(
        OPENAI_API_KEY="test_key",
        MAX_IMAGE_SIZE_MB=5,
        SUPPORTED_IMAGE_FORMATS=["jpg", "jpeg", "png"]
    )


@pytest.fixture
def analyzer(mock_settings):
    return VisionAnalyzer(settings=mock_settings)


def test_validate_image_file_not_found(analyzer):
    with pytest.raises(ValueError, match="Image file not found"):
        analyzer._validate_image(Path("nonexistent.jpg"))


@patch("src.vision_analyzer.Image")
def test_analyze_image_success(mock_pil, analyzer):
    # Mock image file and PIL
    mock_image = Mock()
    mock_pil.open.return_value.__enter__.return_value = mock_image
    
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="Test analysis"))
    ]
    mock_response.model = "gpt-4-vision-preview"
    
    with patch.object(analyzer.client.chat.completions, "create") as mock_create:
        mock_create.return_value = mock_response
        
        # Create a temporary test image file
        test_image = Path("test_image.jpg")
        test_image.touch()
        
        try:
            result = analyzer.analyze_image(
                test_image,
                "Describe this image",
                max_tokens=100
            )
            
            assert isinstance(result, ImageAnalysisResponse)
            assert result.analysis == "Test analysis"
            assert result.model_used == "gpt-4-vision-preview"
            assert isinstance(result.processing_time, float)
            
        finally:
            # Clean up
            test_image.unlink() 