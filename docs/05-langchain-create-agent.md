# POC 05: Automatic Tool Execution with `create_agent()`

## Purpose

Demonstrate how LangChain's `create_agent()` runs the tool-calling loop for
the application. The LLM can request a tool, the agent executes it, and its
result is returned to the LLM so the model can continue toward a final answer.

## Problem

In POC 04, the application manually inspects tool calls, selects a tool from a
registry, invokes it, creates tool-result messages, and calls the LLM again.
That gives the application direct control, but requires it to implement and
maintain the orchestration loop.

## Solution

This POC defines the same two tools as POC 04:

- `calculate_word_count`, a custom Python word-count tool.
- `wikipedia`, a LangChain Wikipedia query tool.

It passes the tools and the Groq chat model to `create_agent()`. The
application invokes the agent with the user's message. When the model requests
a tool, the agent matches the request to a registered tool, runs it, and adds
the result to the conversation. The model can then use that result to answer
or request another tool. The loop continues until the agent returns a final
response.

Compared with POC 04, the application no longer manually dispatches tools or
constructs the tool-result conversation. It still defines and supplies the
tools, starts the agent invocation, and decides what output to display.

## How to Run

From the project root, install the project dependencies and make the Groq API
key available as `GROQ_API_KEY` in the environment, then run:

```bash
uv sync
uv run python "poc05_langchain_tool_via_create_agent copy.py"
```

The script sends two example prompts: one asks Wikipedia about Alan Turing,
and one asks for a word count. The Wikipedia tool requires network access.

## Sample Output

Exact wording and Wikipedia content vary by model and live search results.
The custom-tool example follows this shape:

```text
User: Count how many words are in this string: 'LangChain automation rocks!'
Agent Final Answer: There are 3 words in the string.
```

The Wikipedia example prints a short summary of Alan Turing based on the
tool's result.

## Expected Output

The script should print a final answer for both prompts. The word-count
response should report three words. For the Wikipedia prompt, the agent should
use the Wikipedia tool and produce a summary; the exact text depends on the
tool result and model response.

## Lessons Learned

- `create_agent()` provides an execution loop around tool-enabled model calls.
- The model requests tools, but the agent executes registered implementations
  and returns their results to the model.
- The model may make more than one tool call before producing its final
  response.
- Compared with POC 04, the application avoids writing the dispatch and
  tool-message round trip itself.
- Automation does not remove the need to choose trusted tools and expose only
  the tools the agent is allowed to use.

## Limitations

- The agent can execute a requested tool without asking the user for approval.
- The example does not configure persistent conversation history or retain
  state between separate invocations.
- Wikipedia results depend on network availability and may be incomplete or
  change over time.
- Model and tool errors are not handled with custom retries or recovery logic
  in this small demo.
- The API key must be available in the process environment; this script does
  not load a `.env` file itself.

## What the Next POC Solves

POC 06 adds a human-in-the-loop approval step before a tool executes. This
keeps the agent's automatic orchestration while letting the user approve or
reject each proposed tool call.
