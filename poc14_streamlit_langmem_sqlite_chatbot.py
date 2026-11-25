import os
from pathlib import Path
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore
from langmem import create_manage_memory_tool, create_search_memory_tool


USER_ID = "learner-1"
DEFAULT_THREAD_ID = "poc14-chat"
MEMORY_NAMESPACE = ("memories", "{user_id}")
CHECKPOINT_DB = Path("poc14_threads.db")
STORE_DB = Path("poc14_memories.db")


def build_agent(checkpointer: SqliteSaver, store: SqliteStore):
    tools = [
        create_manage_memory_tool(
            namespace=MEMORY_NAMESPACE,
            instructions=(
                "Save stable user preferences and facts, especially when the "
                "user explicitly asks you to remember them. Update outdated "
                "facts instead of keeping conflicting versions."
            ),
        ),
        create_search_memory_tool(
            namespace=MEMORY_NAMESPACE,
            instructions=(
                "Search before answering questions about the user's "
                "preferences or previously shared facts."
            ),
        ),
    ]
    return create_agent(
        model=ChatGroq(model="qwen/qwen3.8-27b", temperature=0),
        tools=tools,
        store=store,
        checkpointer=checkpointer,
        system_prompt=(
            "You are a helpful learning assistant. Use manage_memory to save "
            "stable facts the user asks you to remember. Use search_memory "
            "when the user asks about remembered facts. Do not claim a fact "
            "was saved unless the memory tool confirms it."
        ),
    )


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="POC 14: Persistent Memory Chatbot")
    st.title("POC 14: LangMem Chatbot with SQLite")
    st.caption(
        "LangMem manages long-term facts; SQLite persists chat threads and memories."
    )

    if not os.getenv("GROQ_API_KEY"):
        st.error("Set GROQ_API_KEY in the project .env file, then restart Streamlit.")
        st.stop()

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = DEFAULT_THREAD_ID

    with st.sidebar:
        st.subheader("Chat")
        if st.button("Start a new chat"):
            st.session_state.thread_id = f"chat-{uuid4().hex[:10]}"
            st.rerun()
        st.caption(f"Thread: {st.session_state.thread_id}")
        st.caption(f"User: {USER_ID}")
        st.caption(f"Checkpoint DB: {CHECKPOINT_DB.resolve()}")
        st.caption(f"Memory DB: {STORE_DB.resolve()}")

    with (
        SqliteSaver.from_conn_string(str(CHECKPOINT_DB.resolve())) as checkpointer,
        SqliteStore.from_conn_string(str(STORE_DB.resolve())) as store,
    ):
        store.setup()
        agent = build_agent(checkpointer, store)
        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
                "user_id": USER_ID,
            }
        }

        snapshot = agent.get_state(config)
        saved_messages = snapshot.values.get("messages", [])
        for message in saved_messages:
            if message.type == "human":
                role = "user"
            elif message.type == "ai":
                role = "assistant"
            else:
                continue

            if message.content:
                with st.chat_message(role):
                    st.markdown(str(message.content))

        prompt = st.chat_input("Ask a question or tell me what to remember")
        if prompt:
            previous_message_count = len(saved_messages)
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("Thinking..."):
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config=config,
                )

            new_messages = result["messages"][previous_message_count:]
            tool_messages = [
                message for message in new_messages if isinstance(message, ToolMessage)
            ]
            if tool_messages:
                with st.expander("LangMem tool activity"):
                    for message in tool_messages:
                        st.write(message.content)

            with st.chat_message("assistant"):
                st.markdown(str(result["messages"][-1].content))

        with st.sidebar:
            st.subheader("Long-term memories")
            memories = store.search(("memories", USER_ID), limit=20)
            if memories:
                for item in memories:
                    st.write(item.value.get("content", item.value))
            else:
                st.info("No memories saved yet.")


if __name__ == "__main__":
    main()
