from pathlib import Path

from langgraph.store.sqlite import SqliteStore


DATABASE_PATH = Path("poc10_long_term_memory.db")


def main() -> None:
    user_id = "learner-1"
    namespace = (user_id, "profile")

    with SqliteStore.from_conn_string(str(DATABASE_PATH)) as store:
        store.setup()
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

        print(f"SQLite file: {DATABASE_PATH.resolve()}")
        print(f"Facts saved for {user_id}:")
        for item in store.search(namespace):
            print(f"- {item.key}: {item.value['fact']}")

        other_user_items = store.search(("learner-1", "profile"))
        print("\nFacts for a different user:")
        print(f"- {len(other_user_items)} found")

    print("\nRun the script again to read the same facts after a restart.")


if __name__ == "__main__":
    main()
