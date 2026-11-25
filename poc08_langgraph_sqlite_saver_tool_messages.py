import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()


@tool
def calculate_word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


def print_database_summary(database_path: Path, thread_id: str) -> None:
    with sqlite3.connect(database_path) as connection:
        checkpoint_count = connection.execute(
            "SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()[0]
        write_count = connection.execute(
            "SELECT COUNT(*) FROM writes WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()[0]

    print("\nSQLite database contents:")
    print(f"Checkpoints for thread {thread_id}: {checkpoint_count}")
    print(f"Stored writes for thread {thread_id}: {write_count}")


def main() -> None:
    database_path = Path("poc08_checkpoints.db").resolve()
    thread_id = "poc08-tool-messages"
    config = {"configurable": {"thread_id": thread_id}}

    with SqliteSaver.from_conn_string(str(database_path)) as checkpointer:
        agent = create_agent(
            model=ChatGroq(model="qwen/qwen3.8-27b", temperature=0),
            tools=[calculate_word_count],
            checkpointer=checkpointer,
            system_prompt=(
                "When the user asks for an exact word count, you must call "
                "calculate_word_count before answering."
            ),
        )
        questions = [
            "Use the word-count tool for this exact text: SQLite keeps tool results.",
            "What exact word count did the tool return?",
        ]
        for question in questions:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": question}]},
                config=config,
            )
            print(f"\nUser: {question}")
            print(f"Assistant: {result['messages'][-1].content}")

        saved_messages = agent.get_state(config).values["messages"]
        tool_messages = [
            message for message in saved_messages if isinstance(message, ToolMessage)
        ]
        print(f"\nCheckpoint database: {database_path}")
        print(f"Tool messages in the saved thread: {len(tool_messages)}")
        for message in tool_messages:
            print(f"ToolMessage: {message.content}")

        if not tool_messages:
            print("The model did not call the tool in this run.")

    print_database_summary(database_path, thread_id)


if __name__ == "__main__":
    main()
