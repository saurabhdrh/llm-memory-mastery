# POC 06: Human-in-the-Loop Tool Approval with LangGraph

## Purpose

Show how an agent can pause before executing a tool, ask a person to approve
or reject the request, and then continue its workflow. LangGraph's
`InMemorySaver` checkpoints the agent state while it is paused.

## Problem

An automatically running agent can execute tools as soon as the model asks
for them. For tools with meaningful side effects or sensitive results, the
application may need a person to review the requested tool and arguments
before execution.

## Solution

The POC creates an agent with the custom `calculate_word_count` tool and the
LangChain Wikipedia tool. `HumanInTheLoopMiddleware` is configured to
interrupt on every call to either tool, with `approve` and `reject` as the
allowed decisions. `InMemorySaver` is passed as the agent checkpointer.

`run_agent_query()` manages the pause-and-resume flow:

1. It invokes the agent with the user's message and a configurable
   `thread_id`.
2. If the agent returns interrupts, it displays each requested tool and its
   arguments, then `ask_for_approval()` prompts for `y`/`yes` or `n`/`no`.
3. It maps each decision to its interrupt ID and resumes the same agent
   thread by invoking the agent with `Command(resume=decisions)` and the same
   config.
4. On approval, the agent executes the tool and continues the model/tool
   loop. On rejection, it returns the rejection message to the agent instead
   of running that tool.
5. If another tool call is interrupted, the `while` loop asks for another
   decision. Once there are no interrupts left, the function prints the final
   answer from the result.

The saver preserves the paused workflow state only in process memory. The
same `thread_id` must be used for resumption; this script hard-codes
`poc05-human-approval` for both sample queries.

## How to Run

From the project root, install the dependencies and set `GROQ_API_KEY` in
`.env`. The script calls `load_dotenv()`, so it loads that file when present.
Then run:

```bash
uv sync
uv run python poc06_langchain_tool__human_in_loop_langgraph_inmemorysaver.py
```

For each query, enter `y` or `yes` to approve the displayed tool call, or `n`
or `no` to reject it. Invalid input is prompted again. The two example
queries use Wikipedia and the custom word-count tool, respectively.

## Sample Output

This is illustrative output; model wording and tool arguments can vary:

```text
User: Summarise who Alan Turing was based on Wikipedia data.

Tool requested: wikipedia
Arguments: {'query': 'Alan Turing'}
Execute this tool? (y/n): y
Agent Final Answer: Alan Turing was a British mathematician and computer scientist...

User: Count how many words are in this string: 'LangChain automation rocks!'

Tool requested: calculate_word_count
Arguments: {'text': 'LangChain automation rocks!'}
Execute this tool? (y/n): n
Agent Final Answer: I could not count the words because the tool request was rejected.
```

The rejection response is supplied to the agent; the exact final wording is
up to the model.

## Expected Output

Each example should display the user's query and, when the model requests a
tool, its name and arguments. The program waits for a decision before the
tool runs. After approval, the tool result is returned to the agent and a
final answer is printed. After rejection, that tool is not executed and the
agent responds based on the rejection. If the model does not request a tool,
the workflow can complete without an approval prompt.

## Test data

The script runs these two requests automatically:

```text
Summarise who Alan Turing was based on Wikipedia data.
Count how many words are in this string: 'LangChain automation rocks!'
```

At each `Execute this tool? (y/n):` prompt, enter `y` to approve the tool or
`n` to reject it. To test both paths, approve the Wikipedia request with `y`
and reject the word-count request with `n`. The second sentence contains
**3 words**; when rejected, the tool must not run and the agent receives the
rejection message. The final model wording may vary.

## Lessons Learned

- Human approval can be inserted into an agent workflow without manually
  implementing every model/tool exchange.
- Middleware determines which tool calls interrupt and which decisions are
  accepted.
- A checkpoint lets the agent resume its pending workflow instead of
  starting the request over.
- The interrupt ID associates each approval decision with its pending call.
- Resumption needs the same checkpointer and thread configuration used for
  the initial invocation.

## Limitations

- `InMemorySaver` is volatile: checkpoint state is lost when the process
  exits, so it is not suitable for durable approval workflows.
- Both sample queries use the fixed thread ID `poc05-human-approval`; separate
  or concurrent conversations should use distinct thread IDs.
- The approval prompt is a synchronous terminal input, not a web or
  asynchronous review interface.
- Both tools require approval on every call; the example does not configure
  different approval policies for different tools.
- Wikipedia needs network access, and tool/model errors are not given custom
  retry or recovery handling.

## What the Next POC Solves

The next step is to retain the same interrupt-and-resume workflow while
replacing the in-memory checkpointer with durable storage. A persistent
checkpointer would allow a pending approval to survive a process restart and
support longer-lived workflows. The project's roadmap labels the following
checkpointing topic as POC 07.
