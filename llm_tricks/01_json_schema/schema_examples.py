#!/usr/bin/env python3
"""
Examples of using JSON schemas with LLMs to get structured responses.
"""
import json
import os
from typing import Any, Dict

# Optional: If you have an API client installed
try:
    import anthropic  # Claude
    CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    has_anthropic = True
except ImportError:
    has_anthropic = False

try:
    import openai  # GPT models
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    has_openai = False if not OPENAI_API_KEY else True
except ImportError:
    has_openai = False


def load_schema(file_path: str) -> Dict[str, Any]:
    """Load a JSON schema from a file."""
    with open(file_path, "r") as f:
        return json.load(f)


def schema_as_prompt_instruction(schema: Dict[str, Any]) -> str:
    """
    Convert a JSON schema to a prompt instruction that can be used
    in a conversation with an LLM.
    """
    schema_str = json.dumps(schema, indent=2)
    
    instruction = f"""
I need you to respond with JSON that matches the following schema:

```json
{schema_str}
```

Important guidelines:
1. Your response must be valid JSON that strictly conforms to this schema
2. Don't include any explanatory text before or after the JSON
3. Required fields must be included
4. Respect all type constraints, formats, and validations

Respond only with the JSON.
"""
    return instruction


def api_example_claude(schema: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Example of using JSON schema with Claude API."""
    if not has_anthropic:
        return {"error": "anthropic package not installed"}
    
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        system=f"When asked to generate information, you must respond with JSON that follows this schema: {json.dumps(schema)}",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    
    try:
        # Attempt to parse the response as JSON
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        return {"error": "Failed to parse response as JSON", "raw_response": response.content[0].text}


def api_example_openai(schema: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Example of using JSON schema with OpenAI API (with response format)."""
    if not has_openai:
        return {"error": "openai package not installed or API key not set"}
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that always replies with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {"error": str(e)}


def prompt_example() -> str:
    """
    Example of a prompt that can be copied into Cursor or other LLM interface,
    to get a structured response based on a schema.
    """
    # Load the basic schema
    basic_schema = load_schema("llm_tricks/01_json_schema/basic_schema.json")
    
    # Create the prompt instruction
    schema_instruction = schema_as_prompt_instruction(basic_schema)
    
    # Full prompt example
    full_prompt = f"""
{schema_instruction}

Please generate the details of a fictional person who is a software engineer with at least 3 interests.
"""
    return full_prompt


def main():
    """Demonstrate different ways to use JSON schemas with LLMs."""
    print("== JSON Schema LLM Examples ==")
    
    # Load example schemas
    basic_schema = load_schema("llm_tricks/01_json_schema/basic_schema.json")
    complex_schema = load_schema("llm_tricks/01_json_schema/complex_schema.json")
    
    # Print a prompt example
    print("\n=== Prompt Example ===")
    print("Copy this prompt into Cursor or ChatGPT:")
    print(prompt_example())
    
    # Optional API examples if libraries are installed
    if has_anthropic and CLAUDE_API_KEY:
        print("\n=== Claude API Example ===")
        prompt = "Generate a fictional person who loves coding"
        result = api_example_claude(basic_schema, prompt)
        print(json.dumps(result, indent=2))
    
    if has_openai and OPENAI_API_KEY:
        print("\n=== OpenAI API Example ===")
        prompt = "Generate a fictional person who loves coding"
        result = api_example_openai(basic_schema, prompt)
        print(json.dumps(result, indent=2))
    
    print("\nDone! These examples show different approaches to using JSON schemas with LLMs.")


if __name__ == "__main__":
    main() 