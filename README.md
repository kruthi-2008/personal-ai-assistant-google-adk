
# Personal AI Assistant using Google ADK

## Overview

A personal AI assistant developed using Google's Agent Development Kit (ADK) as part of a hands-on AI development workshop. This project explores AI agent configuration, instruction design, and tool integration.

## Features

- **Calculator Tool:** Performs mathematical calculations.
- **Text Analyzer Tool:** Analyzes text and provides statistics such as character count, word count, and sentence count.
- **AI Agent:** Uses a configured Gemini model to respond to user queries and work with integrated tools.

## Technologies Used

- Python
- Google Agent Development Kit (ADK)
- Google Gemini
- API integration

## Project Structure

```text
personal_ai_assistant/
├── agent.py
├── tools.py
├── __init__.py
├── .gitignore
└── README.md
```

## Setup and Usage

1. Install Python 3.11 or a compatible version supported by your installed ADK release.
2. Install Google ADK:

   ```bash
   pip install google-adk
   ```

3. Configure your Gemini API key in a local `.env` file. Never publish your actual API key.
4. From the parent directory containing the `personal_ai_assistant` folder, run:

   ```bash
   adk web
   ```

5. Open the local URL displayed in the terminal to interact with the assistant.

## Learning Outcomes

- AI agent configuration and instruction design
- Integrating custom tools with an AI agent
- Python development and debugging
- API configuration and environment variable management

## Security

API keys, `.env` files, virtual environments, and local generated state should not be committed to the public repository.

## Acknowledgement

Developed as part of a hands-on workshop on building AI agents with Google ADK.
