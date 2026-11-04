# POC 01: No Memory

## Purpose

Show the baseline behavior of a stateless LLM call.

## Problem

The LLM forgets earlier messages because it does not keep conversation state automatically.

## Solution

Call `ChatGroq` directly without any memory layer.

## How to Run

```bash
uv run python poc01_no_memory.py
```

## Sample Output

[View the POC 01 output screenshot](images/poc01-sample.svg)

## Expected Output

The script prints the first answer and then a second answer to a follow-up question. The second answer should not correctly remember the earlier fact unless memory is added.

## Lesson

An LLM call is stateless unless you provide memory.

## Limitation

This does not support multi-turn conversation continuity.

## Next POC Solves

POC 02 adds short-term chat memory with LangChain history.

## Troubleshooting

- Make sure `.env` has `GROQ_API_KEY`.
- Run `uv sync` first.
- Ensure the model is `qwen/qwen3.8-27b`.
