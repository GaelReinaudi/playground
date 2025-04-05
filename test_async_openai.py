#!/usr/bin/env python3
"""
Test script for AsyncOpenAI functionality
"""

import asyncio
import os

from openai import AsyncOpenAI


async def test_async_openai():
    """Simple test function for AsyncOpenAI client"""
    # Try to get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        print("No API key found. Set the OPENAI_API_KEY environment variable.")
        print("This is just a test of imports and async functionality.")
        return

    # Initialize the AsyncOpenAI client
    client = AsyncOpenAI(api_key=api_key)

    try:
        # Make a simple test call - won't run without an API key
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            temperature=0.0,
        )

        print("Successfully called the OpenAI API asynchronously!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {e}")
        print("This is expected if no valid API key is provided.")


async def main():
    """Main entry point for testing AsyncOpenAI"""
    print("Testing AsyncOpenAI functionality...")
    await test_async_openai()
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
