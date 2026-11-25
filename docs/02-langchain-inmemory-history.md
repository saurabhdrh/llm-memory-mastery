# POC 02: LangChain In-Memory Chat History

## Purpose

Demonstrate session-local chat memory in LangChain.

## Problem

The LLM remains stateless without chat history.

## Solution

Use `InMemoryChatMessageHistory` with `RunnableWithMessageHistory`.

## How to Run

```bash
uv run python poc02_langchain_inmemory_history.py
```

## Sample Output

[View the POC 02 output screenshot](images/poc02-sample.svg)

## Expected Output

The assistant should answer that it knows the user's name and project from the same session.

## Test data

The first two turns run automatically in the same session:

```text
My name is Mukul. I work on OLMS.
What is my name and which project do I work on?
```

At the optional follow-up, enter `y`, then try:

```text
Can you remind me which project I said I work on?
```

The follow-up should use earlier turns from the current process. The model's
exact wording can vary.

## Lesson

In-memory history provides short-term memory within one application session.

## Limitation

The memory disappears after app restart or process restart.

## Next POC Solves

POC 03 adds persistent database-backed chat history for separate threads.

## Troubleshooting

- Keep the same `session_id` when testing continuity.
- Confirm your Groq key is configured.
