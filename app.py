import re
import uuid

import streamlit as st

from agent import get_agent, get_model

st.set_page_config(page_title="Nexus AI", page_icon="⚡")

EXAMPLES = [
    "What are the latest tech news today?",
    "Weather in Bengaluru right now",
    "Is it a good day for a trip to Goa?",
]
TOOL_LABELS = {"google_search_tool": "Google Search", "weather_tool": "Weather"}
AVATARS = {"user": "🧑‍💻", "assistant": "✨"}
GREETINGS = {"good afternoon", "good evening", "good morning", "hello", "hey", "hi"}
TOOL_INTENT = re.compile(
    r"\b(weather|forecast|news|latest|current|currently|today|yesterday|"
    r"right now|search|look up|find sources|sources|citations?|"
    r"stock price|exchange rate|score|breaking)\b",
    re.IGNORECASE,
)
DIRECT_ANSWER_PROMPT = (
    "Answer the user's question directly using general knowledge. "
    "Keep the answer concise. Do not claim to have checked live information."
)


def greeting_response(query: str) -> str | None:
    normalized = query.strip().casefold().rstrip("!.,? ")
    return "Hello! How can I help you?" if normalized in GREETINGS else None


def needs_tools(query: str) -> bool:
    return bool(TOOL_INTENT.search(query))


def stream_model_text(model, messages):
    for chunk in model.stream(messages):
        text = getattr(chunk, "text", "")
        if text:
            yield text


def stream_agent_text(agent, query: str, thread_id: str, tool_sink: set):
    for chunk, _meta in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": thread_id}},
        stream_mode="messages",
    ):
        for tc in getattr(chunk, "tool_call_chunks", None) or []:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
            if name:
                tool_sink.add(name)

        if type(chunk).__name__ != "AIMessageChunk":
            continue

        content = chunk.content
        if isinstance(content, str):
            if content:
                yield content
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    if text:
                        yield text


# ---------- Session Setup ----------
if "model" not in st.session_state:
    st.session_state.model = get_model()

if "agent" not in st.session_state:
    st.session_state.agent = get_agent(st.session_state.model)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

if "thread_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.thread_id = new_id
    st.session_state.chat_history[new_id] = {"title": "New Chat", "messages": []}

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.thread_id = new_id
    st.session_state.chat_history[new_id] = {"title": "New Chat", "messages": []}


def switch_chat(thread_id):
    st.session_state.thread_id = thread_id


current_thread_id = st.session_state.thread_id
current_chat = st.session_state.chat_history[current_thread_id]

# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚡ Nexus AI")
    st.caption("Search Anything")
    st.button("➕ New chat", on_click=start_new_chat, use_container_width=True)

    st.divider()
    st.markdown("**Previous Conversations**")
    for tid, chat_data in reversed(list(st.session_state.chat_history.items())):
        label = chat_data["title"]
        if tid == current_thread_id:
            label = f"💬 {label}"
        st.button(label, key=tid, on_click=switch_chat, args=(tid,), use_container_width=True)

    st.divider()
    st.markdown("**Try asking**")
    for example in EXAMPLES:
        if st.button(example, key=f"ex_{example}", use_container_width=True):
            st.session_state.pending_query = example

    st.divider()
    st.markdown("**Quick weather**")
    city = st.text_input("City", placeholder="Bangalore", label_visibility="collapsed")
    if st.button("Get weather", use_container_width=True) and city.strip():
        st.session_state.pending_query = f"What is the current weather in {city.strip()}?"

# ---------- Chat Screen ----------
st.markdown(
    "<h1 style='text-align: center; font-weight: 600; margin-top: -5vh;'>Where should we start?</h1>",
    unsafe_allow_html=True,
)

for msg in current_chat["messages"]:
    with st.chat_message(msg["role"], avatar=AVATARS[msg["role"]]):
        st.markdown(msg["content"])
        if msg.get("tools"):
            st.caption("Used: " + ", ".join(msg["tools"]))

# ---------- Handle Input ----------
typed = st.chat_input("Ask Nexus")
query = typed or st.session_state.pending_query
st.session_state.pending_query = None

if query:
    if not current_chat["messages"]:
        current_chat["title"] = query[:25] + "..." if len(query) > 25 else query

    current_chat["messages"].append({"role": "user", "content": query})
    st.chat_message("user", avatar=AVATARS["user"]).markdown(query)

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        tools_used = []
        answer = greeting_response(query)

        if answer is None and not needs_tools(query):
            try:
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in current_chat["messages"][-8:]
                ]
                messages = [{"role": "system", "content": DIRECT_ANSWER_PROMPT}, *history]
                answer = st.write_stream(
                    stream_model_text(st.session_state.model, messages)
                )
            except Exception as e:
                answer = f"An error occurred while processing your request: {e}"

        elif answer is None:
            tool_sink: set[str] = set()
            try:
                answer = st.write_stream(
                    stream_agent_text(
                        st.session_state.agent,
                        query,
                        current_thread_id,
                        tool_sink,
                    )
                )
                tools_used = [TOOL_LABELS.get(n, n) for n in sorted(tool_sink)]
            except Exception as e:
                answer = f"An error occurred while processing your request: {e}"

        answer = answer or "I couldn't generate a response. Please try again."
        st.markdown(answer)
        if tools_used:
            st.caption("Used: " + ", ".join(tools_used))

    current_chat["messages"].append(
        {"role": "assistant", "content": answer, "tools": tools_used}
    )
    st.rerun()