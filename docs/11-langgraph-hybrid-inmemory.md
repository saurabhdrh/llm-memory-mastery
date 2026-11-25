# POC 11: Hybrid Memory with an In-Memory Checkpointer and Store

## Problem

Thread history and long-term user memory have different scopes. Using only a
checkpointer keeps one conversation together, but does not make facts
available to another thread. Using only a store does not retain the complete
conversation or workflow state.

## Solution

This small LangGraph graph is compiled with both:

- `InMemorySaver` for graph state scoped to a `thread_id`.
- `InMemoryStore` for a fact scoped to a `user_id` namespace.

The graph node receives `Runtime[UserContext]`, writes a fact to the store
when the message begins with `Remember:`, and reads it for a different
thread. The script writes in `chat-a` and asks from `chat-b`, using the same
user ID. This is a deterministic demonstration of the two memory scopes; it
does not call an LLM.

```text
thread_id -> checkpointer -> messages and workflow state for one chat
user_id   -> store        -> selected facts shared by that user's chats
```

## Run

```bash
uv run python poc11_langgraph_hybrid_inmemory.py
```

## Expected result

The first thread reports that it saved the fact. The second thread can read
that fact even though it has a different `thread_id`. At the end, the script
prints each thread's checkpointed messages and the user's long-term facts
from the store.

## Test data

The script runs the following conversation turns for `learner-1`:

| Thread | Prompt |
| --- | --- |
| `chat-a` | `Remember: I am learning LangGraph memory.` |
| `chat-b` | `What do you know about my learning goal?` |

Verify that `chat-b` retrieves the fact saved by `chat-a`, and that the
printed short-term messages remain separate by thread. The store and
checkpointer are both in memory, so a fresh process starts over.

## Limitations

- Both memory layers are volatile and disappear when the process exits.
- The example stores one fixed fact key; a later `Remember:` replaces it.
- The sample deliberately omits LLM prompting, fact extraction, and semantic
  retrieval so the storage boundaries are visible.
- The graph context's `user_id` must be set by trusted application
  authentication, not by untrusted model output.
- Neither store has retention, export, or deletion controls.

## Next

POC 12 keeps the same split but persists thread checkpoints and user facts to
local SQLite files. It remains a learning setup, not a production deployment.
