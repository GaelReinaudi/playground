# Trick 1: Properly Formatting JSON Schemas for LLMs

This trick demonstrates how formatting matters when sending JSON schemas (especially from Pydantic models) to LLMs like Claude or GPT models.

## The Problem

When working with Pydantic models and LLMs, developers often:
1. Generate a schema from a Pydantic model using `model_schema()`
2. Convert it to a string with `json.dumps(schema)`
3. Include this schema string in the prompt

However, when the schema is sent without proper formatting (all on one line, no indentation), LLMs struggle to understand the structure, resulting in:
- Incorrect responses that don't match the schema
- Missing required fields
- Invalid data types
- General confusion in the model's understanding of what's required

## The Solution: Proper Schema Formatting

By properly formatting the JSON schema (with indentation and line breaks), LLMs can much more easily parse, understand, and respect the schema when generating responses.

## Demonstration

This folder contains examples that show:
1. How to generate schemas from Pydantic models
2. The difference between sending unformatted vs. formatted schemas
3. How to properly format schemas for optimal LLM comprehension

## Best Practices

1. **Always use indentation** - Use `json.dumps(schema, indent=2)` instead of just `json.dumps(schema)`
2. **Triple backticks** - Wrap schemas in ```json code blocks when sending to LLMs
3. **Include clear instructions** - Tell the LLM explicitly to respect the schema structure
4. **Validate responses** - Always validate responses against the schema after receiving them

## Examples

This folder contains:

- `pydantic_schema_examples.py`: Demonstrates proper vs. improper formatting of Pydantic schemas
- `comparison_demo.py`: A side-by-side comparison showing response quality differences
- `basic_schema.json` and `complex_schema.json`: Example schemas for testing

## How to Run the Demo

```bash
python llm_tricks/01_json_schema/comparison_demo.py
``` 