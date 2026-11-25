# POC 10: SQLite Long-Term Memory Store

## Problem

POC 09's `InMemoryStore` is convenient, but does not survive a process
restart. This POC uses LangGraph's SQLite-backed store to keep the same
namespace/key/value memory available across process restarts.

## Solution

The example uses `SqliteStore` from `langgraph.store.sqlite`, the durable
counterpart to POC 09's `InMemoryStore`. It calls `setup()` to initialize the
store schema, then uses `put()` and `search()` with a `(user_id, "profile")`
namespace. The namespace scopes each user's facts; it is not an authorization
system.

## Run

```bash
uv run python poc10_sqlite_long_term_memory_custom_store.py
```

The file `poc10_long_term_memory.db` is created in the current working
directory. Run the script again to read the same stored values. The demo
updates the same two keys on each run rather than creating duplicate entries.

## Expected result

The same two user facts appear on each run. Saving a fact under an existing
key updates that value instead of creating a duplicate row.

## Test data

No user input is required. The script writes the following values into
`("learner-1", "profile")`:

| Key | Fact |
| --- | --- |
| `learning-goal` | `I am learning LangGraph memory.` |
| `preferred-language` | `I prefer Python examples.` |

Verify that the output lists both facts, reports `0 found` for `learner-2`,
and prints the `poc10_long_term_memory.db` path. Run it a second time to
confirm the same facts remain in the SQLite store.

## Limitations

- Semantic search is disabled unless an embedding/index configuration is
  provided.
- This standalone example does not automatically connect the store to an
  agent; application or graph code must retrieve relevant items.
- SQLite is a local learning backend, not a production multi-instance
  database or a complete concurrency strategy.
- The user ID must come from trusted authentication; do not accept it
  unverified from a model prompt.

## Next

POC 11 combines a thread checkpointer and an in-memory long-term store. The
code shows that these solve different memory problems and need different IDs.

## References

- [LangGraph persistence concepts](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph store integrations](https://docs.langchain.com/oss/python/integrations/long-term-memory/index)
- [SQLite store package](https://pypi.org/project/langgraph-checkpoint-sqlite/)
