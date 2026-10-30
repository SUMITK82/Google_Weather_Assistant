# Nexus AI

Nexus AI is a Streamlit-powered AI assistant that combines conversational intelligence with real-time web search and weather updates. It helps users ask general questions, fetch current information, and get quick weather details for cities around the world.

## Overview

This project uses:

- Streamlit for the web interface
- LangChain and LangGraph for orchestration and tool calling
- Google Gemini for natural-language reasoning
- Nimble Search for live web search results
- OpenWeatherMap for current weather data

The assistant is designed for fast, helpful responses while keeping the interface lightweight and easy to use.

## Features

- Conversational chat interface with persistent chat history
- Smart routing between direct answers and tool-based research
- Live web search for current or changing facts
- Real-time weather lookup by city name
- Quick-start example prompts
- Lightweight multi-thread chat experience in a single app

## Tech Stack

- Python 3.14+
- Streamlit
- LangChain
- LangGraph
- Google Generative AI
- Nimble Search API
- OpenWeatherMap API

## Project Structure

```text
.
├── app.py              # Main Streamlit application
├── agent.py            # Model and agent setup
├── tool.py             # Search and weather tools
├── pyproject.toml      # Python dependencies
├── uv.lock             # Lockfile for reproducible installs
├── .env                # Local environment variables (not committed)
├── .gitignore          # Ignored files and secrets
└── README.md           # Project documentation
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.14 or later
- A Google AI API key
- A Nimble Search API key
- An OpenWeatherMap API key

## Environment Setup

Create a `.env` file in the project root with the following variables:

```env
GOOGLE_API_KEY=your_google_api_key
NIMBLE_API_KEY=your_nimble_api_key
WEATHER_API_KEY=your_openweather_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Important:

- Keep your `.env` file local and never commit it to version control.
- Store all API keys in a secure environment or secret manager for production use.

## Installation

Using `uv` (recommended):

```bash
uv sync
```

Or using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

## Running the App

Start the application with:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## Example Queries

- What are the latest tech news today?
- Weather in Bengaluru right now
- Is it a good day for a trip to Goa?
- What is the capital of Japan?
- Give me a quick overview of the latest AI trends

## How It Works

1. The user enters a question in the Streamlit UI.
2. The app decides whether the request can be answered directly or requires tools.
3. If needed, the agent calls the relevant tool:
   - `google_search_tool` for live web results
   - `weather_tool` for current city weather
4. The model synthesizes the final answer and returns it to the frontend.

## Security Notes

- Never hardcode API keys in the source code.
- Keep environment variables in `.env` or a managed secrets store.
- Ensure `.env` is excluded from version control.

## Future Enhancements

Potential improvements for this project include:

- Support for multilingual conversations
- More specialized tools such as finance, travel, and news summaries
- Better answer citations and source links
- User authentication and personal chat history
- Deployment to Streamlit Cloud, Docker, or a production web server

## License

This project does not currently specify a license. If you plan to distribute or share it publicly, add an appropriate open-source license such as MIT or Apache 2.0.

## Contributing

Contributions are welcome. If you want to improve the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request with a clear description

## Contact

For questions, improvements, or collaboration opportunities, reach out through the project repository or maintainers.
