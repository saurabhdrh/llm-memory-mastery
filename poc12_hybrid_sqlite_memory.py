from dataclasses import dataclass
from pathlib import Path

from langchain_core.messages import AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.sqlite import SqliteStore


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
    checkpointer_path = Path("poc12_threads.db").resolve()
    store_path = Path("poc12_user_facts.db").resolve()
    user_id = "learner-1"
    context = UserContext(user_id=user_id)
    conversations = [
        ("chat-a", "Remember: I prefer Python."),
        ("chat-b", "What language do I prefer?"),
    ]

    builder = StateGraph(MessagesState, context_schema=UserContext)
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)

    namespace = (user_id, "facts")
    thread_snapshots = []
    with (
        SqliteSaver.from_conn_string(str(checkpointer_path)) as checkpointer,
        SqliteStore.from_conn_string(str(store_path)) as store,
    ):
        store.setup()
        graph = builder.compile(checkpointer=checkpointer, store=store)
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
            thread_snapshots.append((thread_id, graph.get_state(config)))

        long_term_items = store.search(namespace, limit=10)

    print(f"Thread checkpoint database: {checkpointer_path}")
    print(f"User facts database: {store_path}")

    print("\nShort-term memory (checkpointed messages by thread):")
    for thread_id, snapshot in thread_snapshots:
        print(f"{thread_id}:")
        for message in snapshot.values.get("messages", []):
            print(f"- {message.type}: {message.content}")

    print(f"\nLong-term memory (facts for {user_id}):")
    for item in long_term_items:
        print(f"- {item.key}: {item.value['fact']}")


if __name__ == "__main__":
    main()
