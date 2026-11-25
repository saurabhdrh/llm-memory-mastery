# POC 14: Streamlit Chatbot with LangMem and SQLite

## Purpose

Run the POC 13 LangMem save/search pattern in a browser UI, with SQLite
persistence for both thread checkpoints and long-term user memories.

## Storage

- `SqliteSaver` stores graph state and conversation messages in
  `poc14_threads.db`.
- `SqliteStore` stores LangMem items in `poc14_memories.db`.
- The demo uses the fixed user ID `learner-1`. **Start a new chat** creates
  another thread for that same user; it does not switch users.
- The default thread ID is `poc14-chat`, so its conversation can be restored
  after restarting the app. A newly-created thread has a generated ID.

The app is a single-user learning demo, not an authenticated multi-user
service.

## Run

From the project root, configure `GROQ_API_KEY` in `.env`, then run:

```bash
uv sync
uv run streamlit run poc14_streamlit_langmem_sqlite_chatbot.py
```

Open the local Streamlit URL shown in the terminal. The databases are created
in the current working directory. No separate SQLite viewer is required:
the app shows stored memories in the sidebar and restores checkpointed
messages into the chat.

## Test data

### Short-term memory in one thread

Click **Start a new chat**, then send:

```text
For this conversation only, my temporary code is TMP-7429. Do not save it as a long-term memory.
```

Then ask:

```text
What was my temporary code in this chat?
```

Verify that the chatbot recalls `TMP-7429` in that thread and that the
temporary code is not listed in the sidebar's long-term memories.

### Thread isolation

Click **Start a new chat** again and ask:

```text
What temporary code did I use in another chat? Don't guess; check my saved memories.
```

The new thread should not have access to the prior thread's short-term
conversation. Since the code was explicitly marked as temporary, it should
not appear in long-term memory either.

### Long-term memory across threads

Send:

```text
Please save this stable preference: I prefer concise explanations with Python examples.
```

Verify that the LangMem tool activity shows a save/update action and the
preference appears in the sidebar. Click **Start a new chat**, then ask:

```text
How should you explain Python concepts to me? Search my saved memories first.
```

The new thread should retrieve the preference from `SqliteStore`.

### Checkpoint persistence

In the default thread (before clicking **Start a new chat**), send:

```text
For this chat only, my checkpoint test phrase is blue lantern 58. Do not save it as a long-term memory.
```

Stop and restart the app, then ask in the default chat:

```text
What was my checkpoint test phrase in this chat?
```

Verify that the phrase is available from the `poc14-chat` checkpoint and that
the long-term preference remains visible in the sidebar. The exact model
wording and memory-tool choices can vary.

## Limitations

- Groq model calls require an active `GROQ_API_KEY` and network access.
- The model decides whether to call LangMem tools. The sidebar is the source
  of truth for which memories were actually stored.
- All users share the demo's fixed `learner-1` namespace. Do not expose this
  app as a multi-user service without adding authenticated user isolation.
- SQLite files are local to one machine and are not a production shared
  database configuration.
