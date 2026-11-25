# POC 13: Letting the Agent Manage Long-Term Memory with LangMem

## Problem

In the earlier hybrid-memory examples, application code decides exactly when
to write a fact and when to look it up. That is easy to understand, but it
adds memory-specific branching to business logic.

## Is LangMem the right tool?

Yes, for reducing that hot-path memory orchestration. LangMem provides
memory-management tools that an agent can use to create, update, and delete
memories, plus a search tool for retrieving them. The agent can decide when
those tools are relevant during a conversation.

LangMem does **not** make memory completely automatic or remove application
responsibility. The developer still chooses the store, persistence backend,
namespace and user identity, tool instructions, and policies for what may be
saved. The model may also make a poor decision or fail to call a memory tool.

This POC uses LangMem's **hot-path tools**. LangMem also offers a background
memory manager that can extract and consolidate memories from conversation
messages outside the agent's immediate response path. That pattern still
needs application code to choose when to run the manager, what conversation
data to give it, and how the agent retrieves those memories.

## Solution

The script creates:

- An `InMemoryStore` for long-term items.
- `create_manage_memory_tool()` to create, update, or delete user memories.
- `create_search_memory_tool()` to search saved items.
- A LangChain `create_agent()` that receives both tools and the store.
- An `InMemorySaver` for the agent's short-term thread state.

The namespace template `("memories", "{user_id}")` scopes memories by the
`user_id` passed in invocation config. The script asks the agent to save a
preference in one thread, then asks about it in a second thread for the same
user. It also prints the tool messages and stored item so you can see the
agent's memory actions.

```text
Business request -> agent decides whether memory tools are needed
                 -> LangMem tool manages/searches items in the Store
                 -> agent responds with the result
```

The example uses a plain `InMemoryStore` to avoid requiring an embeddings
provider or another API key. It is intentionally a one-memory learning
example; semantic ranking is not configured.

## Run

Set `GROQ_API_KEY` in `.env`, then run:

```bash
uv sync
uv run python poc13_langmem_agent_managed_memory.py
```

The agent makes live Groq calls. It should save the stated preference, then
find it in the second thread. Wording and whether the model follows its tool
instructions can vary. If no memory was saved, the script raises a clear
error instead of claiming success.

## Test data

The script sends a save request in one thread:

```text
Remember that I prefer concise Python explanations.
```

It then asks in a second thread:

```text
How should you explain Python concepts to me? Search my saved memories first.
```

Verify that the output shows the memory-management tool result, the assistant
response, and the stored item in the `learner-1` namespace. The exact tool
calls and wording depend on the model. The store is in memory, so it is
cleared when the script exits.

## What changed for the developer?

Without LangMem, application code commonly needs to:

1. Detect memory-worthy user input.
2. Select a memory key and create or update a store item.
3. Decide whether the current question needs a lookup.
4. Search the correct user namespace.
5. Add retrieved memories to the model's context.

With the hot-path tools, the application gives the agent a configured Store
and memory tools. The agent can choose to call them as part of its normal
tool loop. That shifts routine create/update/search decisions away from
hand-written branches, while leaving the storage and safety policy with the
application.

## Limitations

- `InMemoryStore` loses long-term items on process restart; the checkpointer
  and Store have separate lifecycles.
- The model chooses whether to save or search and can miss, misinterpret, or
  incorrectly update a fact. Tool instructions are guidance, not a
  deterministic policy.
- This sample has no semantic embeddings, retention, approval workflow,
  tenant authorization, or user deletion/export controls.
- The `user_id` namespace must come from trusted authentication. It must not
  be accepted directly from untrusted user text or model output.
- Tool calls add model latency and token cost. Avoid sending every transient
  detail to long-term memory.
- LangMem supplies tools and memory-management primitives; it does not
  provide a durable database by itself. Use a persistent LangGraph Store
  implementation when memories must survive restarts or be shared across
  application instances.
- Do not treat retrieved memory as trusted instructions. Validate or
  constrain stored content and defend against prompt injection.

## When to use it

Use the hot-path approach when the agent should decide during the
conversation whether a user preference is worth remembering or whether a
past fact is relevant. Consider a background manager when extraction should
happen separately from the reply path or when you want a dedicated memory
processing workflow.

## References

- [LangMem overview](https://langchain-ai.github.io/langmem/)
- [LangMem memory tools guide](https://langchain-ai.github.io/langmem/guides/memory_tools/)
- [LangMem hot-path quickstart](https://langchain-ai.github.io/langmem/hot_path_quickstart/)
- [LangMem background quickstart](https://langchain-ai.github.io/langmem/background_quickstart/)
- [LangMem tool API reference](https://langchain-ai.github.io/langmem/reference/tools/)
