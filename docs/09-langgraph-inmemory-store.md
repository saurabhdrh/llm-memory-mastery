# POC 09: LangGraph In-Memory Store

## Problem

A checkpointer saves thread state. A fact stored only in one chat thread is
not automatically available in another thread. Durable user preferences and
other cross-chat facts need a separate memory layer.

## Solution

`InMemoryStore` stores key-value items under a namespace. This example uses
`(user_id, "profile")` as the namespace and saves two small facts under
stable keys. Searching the same namespace returns those facts; searching a
different user's namespace returns none.

The namespace is a scope boundary, not an authorization system. An
application must authenticate the user and choose the correct user ID before
reading or writing memory.

Unlike the POCs that use an LLM, this file needs no API key. It isolates the
store operations so the scope and behavior are easy to see. In an agent,
application or graph-node code can look up relevant items and add them to the
model's context.

## Run

```bash
uv run python poc09_langgraph_inmemory_store.py
```

## Expected result

Two facts are printed for `learner-1`, and no facts are found for `learner-2`.

## Limitations

- `InMemoryStore` is volatile and is empty after a process restart.
- The sample uses exact namespace lookup, not semantic/vector search.
- There is no automatic fact extraction, conflict resolution, expiry, or
  deletion workflow.
- Namespaces do not prevent an application from accidentally accessing the
  wrong user's data.

## Next

POC 10 uses LangGraph's `SqliteStore` to persist key-value memory across
process restarts.
