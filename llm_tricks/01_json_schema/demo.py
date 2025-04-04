#!/usr/bin/env python3
"""
Demo script showing how to use JSON schemas with LLMs in practice.
This script runs without requiring API keys by generating the prompts
for you to use in the Cursor UI.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any


def load_schema(file_path: str) -> Dict[str, Any]:
    """Load a JSON schema from a file."""
    with open(file_path, "r") as f:
        return json.load(f)


def generate_cursor_prompt(schema: Dict[str, Any], user_request: str) -> str:
    """
    Generate a prompt for Cursor that includes the JSON schema and
    instructions for generating a conforming response.
    """
    schema_str = json.dumps(schema, indent=2)
    
    prompt = f"""
I need you to respond with JSON that matches the following schema:

```json
{schema_str}
```

Important guidelines:
1. Your response must be valid JSON that strictly conforms to this schema
2. Don't include any explanatory text before or after the JSON
3. Required fields must be included
4. Respect all type constraints, formats, and validations

User request: {user_request}

Respond only with the JSON.
"""
    return prompt


def save_prompt_to_file(prompt: str, filename: str) -> str:
    """Save a prompt to a file and return the file path."""
    output_dir = Path("llm_tricks/01_json_schema/generated")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, "w") as f:
        f.write(prompt)
    
    return str(filepath)


def verify_json(json_str: str, schema: Dict[str, Any]) -> bool:
    """
    Verify that a JSON string matches a schema.
    Note: This is a simplified validation. In production, use a proper
    JSON Schema validator like jsonschema.
    """
    try:
        data = json.loads(json_str)
        
        # Simple validation - check required fields
        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    print(f"Missing required field: {field}")
                    return False
        
        print("JSON validation passed (basic checks only)")
        return True
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False


def process_llm_response(response_file: str, schema: Dict[str, Any]) -> None:
    """Process an LLM response saved to a file."""
    try:
        with open(response_file, "r") as f:
            response = f.read()
        
        # Try to extract JSON from the response
        # (in case the LLM included explanatory text)
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            
            # Verify and process the JSON
            if verify_json(json_str, schema):
                data = json.loads(json_str)
                print("\nParsed JSON response:")
                print(json.dumps(data, indent=2))
                
                # Example of using the structured data
                if "name" in data:
                    print(f"\nHello, {data['name']}!")
        else:
            print("No JSON found in the response.")
    except Exception as e:
        print(f"Error processing response: {e}")


def run_demo() -> None:
    """Run the JSON schema demo."""
    print("=== JSON Schema Demo ===")
    print("This demo shows how to use JSON schemas with LLMs to get structured responses.")
    
    # Load the person schema
    schema_file = "llm_tricks/01_json_schema/basic_schema.json"
    schema = load_schema(schema_file)
    
    # Generate prompt
    user_request = "Create a profile for a fictional software developer who loves AI and machine learning."
    prompt = generate_cursor_prompt(schema, user_request)
    
    # Save prompt to file
    prompt_file = save_prompt_to_file(prompt, "demo_prompt.txt")
    print(f"\nPrompt saved to: {prompt_file}")
    print("Open this file and copy its contents to Cursor or your preferred LLM interface.")
    
    # Instructions for processing the response
    print("\nAfter getting a response from the LLM:")
    print("1. Save the response to a file named 'llm_response.txt' in the same directory")
    print("2. Run this script again with the --process flag")
    print("\nExample:")
    print(f"python {__file__} --process llm_tricks/01_json_schema/generated/llm_response.txt")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--process":
        if len(sys.argv) > 2:
            response_file = sys.argv[2]
            schema = load_schema("llm_tricks/01_json_schema/basic_schema.json")
            process_llm_response(response_file, schema)
        else:
            print("Error: Please provide a file with the LLM's response")
            print("Example: python demo.py --process llm_response.txt")
    else:
        run_demo() 