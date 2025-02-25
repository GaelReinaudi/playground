# GPT Vision Analysis Example

This project demonstrates how to use OpenAI's GPT-4 Vision API to analyze images using Python, with proper configuration management using Pydantic.

## Features

- Image analysis using GPT-4 Vision API
- Type-safe configuration using Pydantic
- Environment variable management
- Error handling and validation
- Sample images and example usage

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the environment file:
```bash
cp ../../config/.env.example ../../config/.env
```

4. Edit `../../config/.env` and add your OpenAI API key

## Usage

```python
from src.vision_analyzer import VisionAnalyzer
from src.config import Settings

# Initialize the analyzer
analyzer = VisionAnalyzer()

# Analyze an image
result = analyzer.analyze_image("data/sample_images/your_image.jpg", "Describe this image in detail")
print(result)
```

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── config.py          # Pydantic settings and configuration
│   ├── vision_analyzer.py # Main GPT Vision implementation
│   └── models.py         # Pydantic models
├── tests/
│   └── test_vision_analyzer.py
├── data/
│   └── sample_images/    # Sample images for testing
├── requirements.txt
└── README.md
```

## Running Tests

```bash
pytest tests/
```

## License

This project is for educational purposes. 