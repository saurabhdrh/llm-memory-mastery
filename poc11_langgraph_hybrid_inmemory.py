from dataclasses import dataclass

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


@dataclass
class UserContext:
    user_id: str


def respond(state: MessagesState, runtime: Runtime[UserContext]) -> dict:
    text = str(state["messages"][-1].content)
    namespace = (runtime.context.user_id, "facts")

    if text.lower().startswith("remember:"):
        fact = text.split(":", maxsplit=1)[1].strip()
        runtime.store.put(namespace, "latest-fact", {"fact": fact})
        answer = f"Saved this long-term fact: {fact}"
    else:
        items = runtime.store.search(namespace, limit=10)
        facts = [item.value["fact"] for item in items]
        answer = "Long-term facts: " + ("; ".join(facts) if facts else "none")

    return {"messages": [AIMessage(content=answer)]}


def main() -> None:
    builder = StateGraph(MessagesState, context_schema=UserContext)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)

    store = InMemoryStore()
    graph = builder.compile(checkpointer=InMemorySaver(), store=store)
    context = UserContext(user_id="learner-1")

    conversations = [
        ("chat-a", "Remember: I am learning LangGraph memory."),
        ("chat-b", "What do you know about my learning goal?"),
    ]
    for thread_id, message in conversations:
        config = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            context=context,
        )
        print(f"\nThread {thread_id}")
        print(f"User: {message}")
        print(f"Assistant: {result['messages'][-1].content}")

    print("\nShort-term memory (checkpointed messages by thread):")
    for thread_id, _ in conversations:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = graph.get_state(config)
        print(f"{thread_id}:")
        for message in snapshot.values.get("messages", []):
            print(f"- {message.type}: {message.content}")

    print(f"\nLong-term memory (facts for {context.user_id}):")
    namespace = (context.user_id, "facts")
    for item in store.search(namespace, limit=10):
        print(f"- {item.key}: {item.value['fact']}")

    print("\nThread history and user memory are separate layers.")
    print("Both are in memory and disappear when this process exits.")


if __name__ == "__main__":
    main()
