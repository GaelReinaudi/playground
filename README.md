# LLM Tricks

A collection of tricks and techniques for improving interactions with LLMs.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the `.env.example` file to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred editor
   ```
4. Set your OpenAI API key in the `.env` file

## Usage

The project uses `pydantic-settings` to manage configuration through environment variables. 
All settings can be configured either through the `.env` file or by setting environment variables.

To view your current settings:
```bash
python settings.py
```

### Running the JSON Schema Formatting Demo

```bash
cd llm_tricks/01_json_schema
python compare_openai.py
```

Command-line options:
- `-m, --model MODEL`: Override the OpenAI model defined in settings
- `-t, --temperature TEMP`: Override the temperature setting
- `--no-phoenix`: Disable Phoenix telemetry
- `-v, --verbose`: Enable verbose output
- `-h, --help`: Show help message

## Features

### JSON Schema Formatting (01_json_schema)

Demonstrates how proper formatting of JSON schemas significantly improves LLM comprehension:

1. Creates complex Pydantic models with deep nesting
2. Generates differently formatted JSON schemas
3. Compares LLM responses to each format
4. Provides quantitative analysis of the improvements