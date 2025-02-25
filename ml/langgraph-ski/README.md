# Ski Status Social Media Generator

A proof-of-concept application that aggregates ski resort status information from multiple sources and generates social media content using LangChain and LLMs.

## Features

- Scrapes data from multiple ski resorts (Niseko United and Rusutsu)
- Integrates with the Yukiyama API for real-time lift status
- Uses LangChain and OpenAI to analyze conditions and generate content
- Creates both detailed reports and social media posts
- Includes workflow visualization using GraphViz

## Requirements

- Python 3.8+
- OpenAI API key (set in .env file)
- Required packages: see requirements.txt

## Usage

1. Set up your environment variables in `.env`: 