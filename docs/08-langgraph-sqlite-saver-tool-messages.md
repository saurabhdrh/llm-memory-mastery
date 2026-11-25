# POC 08: SQLite Checkpoints and Tool Messages

## Problem

POC 07 demonstrates that LangGraph can retain tool messages in thread state,
but its `InMemorySaver` loses every checkpoint when the process exits.

## Solution

This POC uses the SQLite `SqliteSaver` checkpointer from
`langgraph-checkpoint-sqlite`. It otherwise follows POC 07: `create_agent()`
runs a local word-count tool, and the script inspects the messages saved for
one stable `thread_id`.

The important distinction is that a checkpointer persists the graph's state,
not an independent tool-history database. Tool requests and results are
available after restart when the agent has appended them to its `messages`
state and the invocation used a consistent `thread_id`.

The script uses Python's built-in `sqlite3` module to print checkpoint and
write counts for its thread, so a separate database viewer is not required.

## Run

The project dependency includes `langgraph-checkpoint-sqlite`. Set
`GROQ_API_KEY` in `.env`, then run:

```bash
uv sync
uv run python poc08_langgraph_sqlite_saver_tool_messages.py
```

The database file `poc08_checkpoints.db` is created in the current working
directory. Run the program again with the same thread ID to continue its
conversation. The script does not clear the database at startup.

## Expected result

The program prints the saved thread's `ToolMessage` entries and the location
of the checkpoint database. With the same database and thread ID, earlier
messages remain available to the agent in later runs.

## Limitations

- SQLite is suitable for local learning and small single-machine uses; it is
  not a substitute for a production database in a concurrent, multi-instance
  service.
- The script uses one hard-coded thread ID. Real applications must assign
  authorized, collision-resistant IDs.
- Checkpoint history grows; production systems need retention and data
  deletion policies.
- The LLM call still requires a valid Groq key and network access.
- The model may decide not to call the tool in a given run; without a tool
  call, that run has no `ToolMessage` to inspect.
- A tool result is only in the checkpoint if the agent records it in state.

## Next

POC 09 switches concepts: it demonstrates LangGraph's `InMemoryStore`, which
holds user-scoped long-term facts across different conversation threads.
