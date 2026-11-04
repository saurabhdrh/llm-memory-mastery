from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()


# Define a custom tool.
@tool
def calculate_word_count(text: str) -> int:
    """Count the total number of words in a text string."""
    return len(text.split())


# Define a built-in Wikipedia tool.
wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wikipedia_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)
tools = [calculate_word_count, wikipedia_tool]

llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

# Pause before every tool call. Each call can be approved or rejected by the user.
agent = create_agent(
    model=llm,
    tools=tools,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                tool.name: {"allowed_decisions": ["approve", "reject"]}
                for tool in tools
            },
            interrupt_mode="per_call",
        )
    ],
    checkpointer=InMemorySaver(),
)


def ask_for_approval(tool_name: str, tool_args: dict) -> dict[str, str]:
    print(f"\nTool requested: {tool_name}")
    print(f"Arguments: {tool_args}")

    while True:
        choice = input("Execute this tool? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            return {"type": "approve"}
        if choice in {"n", "no"}:
            return {"type": "reject", "message": "Rejected by the user."}
        print("Please enter y/yes to execute or n/no to reject.")


def run_agent_query(user_query: str) -> None:
    print(f"\nUser: {user_query}")
    config = {"configurable": {"thread_id": "poc05-human-approval"}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_query}]},
        config=config,
        version="v2",
    )

    while result.interrupts:
        decisions = {
            interrupt.id: ask_for_approval(
                interrupt.value["name"],
                interrupt.value["args"],
            )
            for interrupt in result.interrupts
        }
        result = agent.invoke(
            Command(resume=decisions),
            config=config,
            version="v2",
        )

    print(f"Agent Final Answer: {result.value['messages'][-1].content}")


# Test Case 1: The agent proposes the Wikipedia tool and asks before running it.
run_agent_query("Summarise who Alan Turing was based on Wikipedia data.")

# Test Case 2: The agent proposes the custom tool and asks before running it.
run_agent_query("Count how many words are in this string: 'LangChain automation rocks!'")
