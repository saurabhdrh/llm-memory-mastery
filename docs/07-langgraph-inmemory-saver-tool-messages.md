# POC 07: LangGraph In-Memory Checkpoints and Tool Messages

## Problem

Binding or executing a tool does not, by itself, create durable conversation
history. A later model call can only use earlier tool results if the
application sends those messages again or stores them in conversation state.
POC 04 manually builds a `ToolMessage`; POC 05's agent has no checkpointer.

## Solution

This example gives a LangChain `create_agent()` an `InMemorySaver` and a
stable `thread_id`. The agent runs a local word-count tool, then handles a
follow-up in the same thread. At the end, `agent.get_state(config)` reads the
saved `messages` state and the script counts its `ToolMessage` objects.

The flow is:

1. The model returns an assistant message containing a structured tool call.
2. The agent runs `calculate_word_count`.
3. The agent adds the tool result as a `ToolMessage` linked to the tool-call
   ID, then sends it to the model.
4. LangGraph checkpoints the agent state at graph steps. Because the agent's
   messages are in that state, the tool-call request and result are included.
5. A later invocation with the same `thread_id` loads and continues that
   thread's messages.

The checkpointer does not independently discover or save every tool result.
The agent must put the `ToolMessage` in graph state; the checkpointer then
saves that state.

## Run

Set `GROQ_API_KEY` in `.env`, then run:

```bash
uv run python poc07_langgraph_inmemory_saver_tool_messages.py
```

The model is instructed to call the tool. Model behavior can vary; if the
model does not call it, the script reports that there is no `ToolMessage` to
inspect.

## Expected result

The script prints the two turns and the `ToolMessage` found in the thread's
current state. The follow-up can refer to the first result because both
invocations use the same `thread_id`.

## Limitations

- `InMemorySaver` stores checkpoints only in this process. Restarting the
  program loses the thread.
- This example has one hard-coded thread and no user or tenant isolation.
- The model must actually request the tool for a `ToolMessage` to exist.
- The full conversation grows over time; there is no trimming or retention
  policy.
- In-memory persistence is useful for learning and tests, not durable
  production state.

## Next

POC 08 keeps the same agent flow but writes thread checkpoints to a SQLite
file, so the state can survive a process restart.
