#!/usr/bin/env python3
"""
Direct comparison script for showing the difference in OpenAI's responses
to differently formatted JSON schemas.

This script runs the comparison of complex schemas immediately without any prompts.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from openai import AsyncOpenAI
from phoenix.otel import register

# Add project root to path for imports
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
sys.path.append(str(project_root))

from settings import Settings

settings = Settings(
    openai_model="gpt-4-turbo",
    phoenix_project_name="llm-tricks-01-json-schema",
)
settings.setup_phoenix_environment()

# The environment variables required by Phoenix are already set by settings.setup_phoenix_environment()
tracer_provider = register(
    project_name=settings.phoenix_project_name,
    auto_instrument=True,
)

# Add parent directory to path for imports
sys.path.append(str(script_dir))

# Import the complex model
from complex_pydantic_model import get_complex_schema, EnterpriseSystemRegistry


async def compare_schema_formats_with_openai():
    # Get the schema
    schema = get_complex_schema()

    # Create directory for outputs
    output_dir = script_dir / settings.generated_dir
    output_dir.mkdir(exist_ok=True)

    # Create differently formatted versions
    unformatted_schema = json.dumps(schema)
    formatted_schema = json.dumps(schema, indent=2)

    base_prompt = """Generate a JSON object that corresponds to that story:
```
{story}
```

and that matches this schema:
```json
{schema}
```
Do not include any other text or comments
Do Not leave blank fileds empty!
Just output the JSON object
"""
    story = Path(script_dir / "story.md").read_text()
    # Create prompts
    bad_prompt = base_prompt.format(schema=unformatted_schema, story=story)
    good_prompt = base_prompt.format(schema=formatted_schema, story=story)

    print("Calling OpenAI API with different complex schema formats...")

    # Initialize the AsyncOpenAI client
    # print(f"Using OpenAI API key: {settings.openai_api_key}")
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Helper function for API calls
    async def call_openai(prompt, format_name):
        print(f"  Calling API with {format_name} format...")

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.openai_temperature,
        )

        content = response.choices[0].message.content

        # Save response to file
        response_file = output_dir / f"complex_comparison_{format_name}_response.txt"
        with open(response_file, "w") as f:
            f.write(content)

        print(f"    Response saved to {response_file}")
        return content.split("```json")[-1].split("```")[0]

    # Make API calls for each format
    for prompt, name in [(bad_prompt, "bad"), (good_prompt, "good")]:
        try:
            response = await call_openai(prompt, name)

            # load the back into a Pydantic model
            json_data = json.loads(response)
            data = EnterpriseSystemRegistry(**json_data)

            # print the data
            # print(data)
            print("-" * 80)
            print(f"Successfully loaded data into Pydantic model: {name}")
        except Exception as e:
            print(f"Error for {name}: {e}")


async def main():
    await compare_schema_formats_with_openai()


if __name__ == "__main__":
    asyncio.run(main())
