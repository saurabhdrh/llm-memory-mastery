# POC 12: Hybrid SQLite Memory and a Production Upgrade Path

## Problem

POC 11 demonstrates the right separation between conversation state and
cross-thread facts, but both stores are in process memory. A restart loses
both types of data.

## Solution

This POC keeps the same scopes and writes them to separate local databases:

- LangGraph's official `SqliteSaver` checkpoints the conversation for a
  `thread_id`.
- LangGraph's `SqliteStore` saves selected facts in a `user_id` namespace.

The graph node uses the same logic as POC 11: a message beginning with
`Remember:` updates the user's latest fact through `runtime.store.put()`;
another message reads facts through `runtime.store.search()`. Each run prints
the checkpointed messages for both threads and the user's stored facts. The
script runs a save in `chat-a` followed by a recall in `chat-b`, using fixed
demo inputs and IDs:

```bash
uv run python poc12_hybrid_sqlite_memory.py
```

Rerunning the script continues the same threads and reads/writes the same
user fact. The thread database and the user-facts database are intentionally
separate because they have different retention and access requirements.

## Test data

No command-line arguments are required. The script runs:

| Thread | Prompt |
| --- | --- |
| `chat-a` | `Remember: I prefer Python.` |
| `chat-b` | `What language do I prefer?` |

Verify that `chat-b` recalls the preference, that both thread histories are
printed, and that the user fact appears in the long-term memory output. The
database files are `poc12_threads.db` and `poc12_user_facts.db`; rerunning the
script should preserve the saved state.

## This is not production-ready

The Python example is a local architecture demonstration. A production
hybrid design typically includes:

```text
authenticated user + thread
        |                     |
        v                     v
PostgresSaver             PostgresStore
thread checkpoints        user-scoped durable facts
        \                     /
         model context assembly
                  |
             LLM / tools
```

For production, replace the local SQLite checkpointer and store with shared
backends such as `PostgresSaver` and `PostgresStore`.
Validate the current integration packages and their migration/setup
instructions before deployment. Add, at minimum:

- Authentication and authorization that derive user IDs on the server.
- Tenant isolation and access tests for both thread and user namespaces.
- Schema migrations, backups, restore drills, and database connection
  management.
- Retention, user export, and deletion policies for messages, tool results,
  and extracted facts.
- A review policy for what the model may store; do not save secrets or
  arbitrary tool output as durable memory.
- Memory size limits, summarization or retrieval, and prompt-injection
  defenses for retrieved content.
- Observability, error handling, retries where safe, rate limits, and
  concurrency testing.

## Limitations

- The example does not configure semantic/vector search on `SqliteStore`.
- The example has no model, automatic fact extraction, user authentication,
  or deletion controls.
- SQLite files are local to one machine; they are not appropriate for
  multiple application instances that need shared state.
- Tool messages are part of agent thread state only when the agent writes
  them to its `messages` channel. This POC focuses on the two persistence
  scopes rather than running tools.
- Reusing a `thread_id` continues that thread; use a new one for a new
  conversation.

## Learning summary

| Need | Use | Scope |
| --- | --- | --- |
| Continue an agent conversation or resume a workflow | Checkpointer | `thread_id` |
| Recall a selected user fact in another conversation | Store | `user_id` namespace |
| Save tool requests and results | Put the tool messages in graph state; checkpoint that state | `thread_id` |

Neither a checkpointer nor a store replaces the other. The application must
decide which information belongs in each layer and enforce who can access it.

## References

- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [LangGraph stores](https://docs.langchain.com/oss/python/langgraph/stores)
- [Store integrations](https://docs.langchain.com/oss/python/integrations/long-term-memory/index)
