# LLM Tricks for Cursor

This repository contains a collection of tricks and techniques for working effectively with Large Language Models (LLMs) in Cursor, organized for presentation at a conference.

## Structure

Each trick is organized in its own numbered folder:

- `01_json_schema/`: Demonstrating the importance of proper formatting when sending JSON schemas to LLMs
- More tricks will be added...

## How to Use

Each folder contains:
- A README explaining the concept
- Example code and files demonstrating the trick
- Instructions on how to reproduce the demo

## Tricks List

1. **JSON Schema Formatting**: Showing how properly formatted schema JSON (with indentation and code blocks) dramatically improves LLMs' ability to follow complex schemas compared to unformatted, one-line schema dumps from Pydantic models.

## Running the Examples

To run any example, navigate to its directory and follow the instructions in its README file. For the first example:

```bash
cd llm_tricks/01_json_schema
python comparison_demo.py
```

This will generate example prompts that you can test with various LLMs to see the difference in response quality.
