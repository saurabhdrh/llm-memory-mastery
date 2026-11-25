from langgraph.store.memory import InMemoryStore


def main() -> None:
    store = InMemoryStore()
    user_id = "learner-1"
    namespace = (user_id, "profile")

    store.put(
        namespace,
        "learning-goal",
        {"fact": "I am learning LangGraph memory."},
    )
    store.put(
        namespace,
        "preferred-language",
        {"fact": "I prefer Python examples."},
    )

    print("Facts saved for learner-1:")
    for item in store.search(namespace):
        print(f"- {item.key}: {item.value['fact']}")

    print("\nFacts for a different user:")
    other_user_items = store.search(("learner-2", "profile"))
    print(f"- {len(other_user_items)} found")

    print(
        "\nThe store is shared across threads in this process, "
        "but disappears when the process exits."
    )


if __name__ == "__main__":
    main()
