# Trick 1: Properly Formatting JSON Schemas for LLMs

This trick demonstrates how formatting matters when sending JSON schemas (especially from Pydantic models) to LLMs like Claude or GPT models.

## The Problem

When working with Pydantic models and LLMs, developers often:
1. Generate a schema from a Pydantic model using `model_json_schema()`
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
1. A complex enterprise-grade Pydantic model with deep nesting and relationships
2. Tools to generate both unformatted and formatted JSON schemas
3. Scripts to compare LLM responses to different schema formats

## Best Practices

1. **Always use indentation** - Use `json.dumps(schema, indent=2)` instead of just `json.dumps(schema)`
2. **Triple backticks** - Wrap schemas in ```json code blocks when sending to LLMs
3. **Include clear instructions** - Tell the LLM explicitly to respect the schema structure
4. **Validate responses** - Always validate responses against the schema after receiving them

## Examples

This folder contains:

- `complex_pydantic_model.py`: An extremely complex enterprise model that generates a massive schema (over 3,400 lines when formatted)
- `compare_complex_schema.py`: Tool to generate schema files and compare OpenAI's responses with the complex schema
- `compare_openai.py`: Direct script that calls OpenAI with different formatting styles and compares results

## How to Run the Demo

### Option 1: Generate the Complex Schema Files

```bash
# Simply generate the schema files without testing
python llm_tricks/01_json_schema/compare_complex_schema.py --generate-only
```

This will create:
- `complex_schema_unformatted.json`: A single-line ~42KB schema (virtually unreadable)
- `complex_schema_formatted.json`: The same schema with indentation (~76KB, ~3,400 lines)
- Example prompt files with both formats

### Option 2: Compare with OpenAI API 

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# Run the direct comparison script
python llm_tricks/01_json_schema/compare_openai.py
```

This will call the OpenAI API three times with the same request but different formatting:
1. Bad format: Schema as one long string without indentation
2. Good format: Schema with proper indentation in a code block
3. Best format: Schema with indentation, code block, and explicit instructions

The script analyzes and compares the responses, showing which format produces better understanding of the schema.

### Option 3: Compare OpenAI responses to the Complex Schema

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# Run the complex schema comparison
python llm_tricks/01_json_schema/compare_complex_schema.py --openai
```

This performs a focused test with the extremely complex schema, asking OpenAI to identify required fields and components in the schema.

## The Complex Model

The complex Pydantic model demonstrates:
- Over 30 deeply nested models with inheritance
- Circular references and complex relationships
- Various field types and validation rules
- Multiple levels of validation and dependencies

When converted to JSON schema, it produces:
- Unformatted: ~42KB single-line JSON string (virtually unreadable)
- Formatted: ~76KB with ~3,400 lines (clear structure)

The difference in LLM comprehension between these formats becomes dramatically obvious with such complex schemas. 