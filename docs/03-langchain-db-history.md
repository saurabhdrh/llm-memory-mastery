# POC 03: Persistent Multi-Thread Chat History

## Purpose

Show how chat history can persist across conversations and thread boundaries.

## Problem

In-memory history does not survive restarts and is not multi-thread by default.

## Solution

Use `SQLChatMessageHistory` with SQLite and `RunnableWithMessageHistory`.

## How to Run

```bash
uv run python poc03_langchain_db_history.py
```

## Sample Output

[View the POC 03 output screenshot](images/poc03-sample.svg)

## Expected Output

The script should show two different threads with different memory states and confirm that thread_1 remembers its own facts while thread_2 is separate.

## Test data

The script starts with these three turns:

| Thread | Prompt |
| --- | --- |
| `thread_1` | `My name is Mukul. I work on OLMS.` |
| `thread_2` | `What is my name?` |
| `thread_1` | `What is my name and which project do I work on?` |

For an interactive test, answer `y`, enter `thread_1`, then ask:

```text
What project did I say I work on?
```

At startup, the script clears `thread_1` and `thread_2` so the initial output
is repeatable. The database shows stored messages during the run, but this
script does not test those thread IDs surviving a restart.

## Lesson

This supports multiple persistent chat threads, but it stores raw messages, not durable extracted memories.

## Limitation

It does not automatically save long-term facts across different chats or tasks.

## Next POC Solves

POC 04 introduces tool-calling history, showing what a simple chat-history wrapper does and does not persist.

## Troubleshooting

- Delete `chat_history.db` to reset all thread history.
- Check that SQLite can write in the project folder.
