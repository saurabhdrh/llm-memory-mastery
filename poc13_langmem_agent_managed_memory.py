from collections.abc import Sequence

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool

load_dotenv()

USER_ID = "learner-1"
MEMORY_NAMESPACE = ("memories", "{user_id}")


def print_tool_messages(messages: Sequence[BaseMessage]) -> None:
    for message in messages:
        if isinstance(message, ToolMessage):
            print(f"Memory tool result: {message.content}")


def main() -> None:
    store = InMemoryStore()
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
    agent = create_agent(
        model=ChatGroq(model="qwen/qwen3.8-27b", temperature=0),
        tools=tools,
        store=store,
        checkpointer=InMemorySaver(),
        system_prompt=(
            "You are a helpful learning assistant. Use manage_memory to save "
            "stable facts the user asks you to remember. Use search_memory "
            "when the user asks about remembered facts. Do not claim a fact "
            "was saved unless the memory tool confirms it."
        ),
    )

    save_config = {
        "configurable": {"thread_id": "poc13-save", "user_id": USER_ID}
    }
    save_result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Remember that I prefer concise Python explanations."
                    ),
                }
            ]
        },
        config=save_config,
    )
    print("Save request:")
    print_tool_messages(save_result["messages"])
    print(f"Assistant: {save_result['messages'][-1].content}")

    namespace = ("memories", USER_ID)
    memories = store.search(namespace)
    if not memories:
        raise RuntimeError(
            "LangMem did not save a memory. Check the model response and "
            "whether it called the manage_memory tool."
        )

    search_config = {
        "configurable": {"thread_id": "poc13-search", "user_id": USER_ID}
    }
    search_result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "How should you explain Python concepts to me? "
                        "Search my saved memories first."
                    ),
                }
            ]
        },
        config=search_config,
    )
    print("\nRecall request in a different thread:")
    print_tool_messages(search_result["messages"])
    print(f"Assistant: {search_result['messages'][-1].content}")

    print("\nLong-term items in the user's namespace:")
    for item in store.search(namespace):
        print(f"- {item.value.get('content', item.value)}")


if __name__ == "__main__":
    main()
