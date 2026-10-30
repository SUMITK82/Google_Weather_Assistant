import os

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from tool import ALL_TOOLS

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

SYSTEM_PROMPT = """You are a research assistant with two tools:
- google_search_tool: use it for current information or factual details that may have changed.
- weather_tool: use it when the user asks about the weather of a city.

Rules:
1. Reply directly to greetings and casual conversation; do not call a tool for them.
2. Use google_search_tool only when the user needs current information or factual information that may have changed.
3. Base factual answers on tool results. Do not make up facts.
4. If the search results do not contain the answer, say so.
5. When you use search results, mention the source (website/URL) briefly.
6. For weather questions, call weather_tool and report temperature (°C), humidity and conditions.
7. Keep answers clear and short."""


def get_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        timeout=60,
        max_retries=2,
    )


def get_agent(model: ChatGoogleGenerativeAI | None = None):
    """Create an agent that can search Google and fetch real-time weather."""
    return create_agent(
        model=model or get_model(),
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )