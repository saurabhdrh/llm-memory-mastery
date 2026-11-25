from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


@tool
def calculate_word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())


def main() -> None:
    checkpointer = InMemorySaver()
    agent = create_agent(
        model=ChatGroq(model="qwen/qwen3.8-27b", temperature=0),
        tools=[calculate_word_count],
        checkpointer=checkpointer,
        system_prompt=(
            "When the user asks for an exact word count, you must call "
            "calculate_word_count before answering."
        ),
    )
    config = {"configurable": {"thread_id": "poc07-tool-messages"}}

    questions = [
        "Use the word-count tool for this exact text: LangGraph saves tool messages.",
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
    print(f"\nTool messages in the current checkpoint: {len(tool_messages)}")
    for message in tool_messages:
        print(f"ToolMessage: {message.content}")

    if not tool_messages:
        print("The model did not call the tool in this run.")


if __name__ == "__main__":
    main()
