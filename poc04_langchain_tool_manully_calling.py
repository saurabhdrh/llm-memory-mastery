from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# 1. DEFINE THE TOOLS
# =====================================================================
@tool
def calculate_word_count(text: str) -> int:
    """Counts the total number of words in a given text string."""
    return len(text.split())

# Set up the built-in Wikipedia tool
wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wikipedia_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)

# Put them in a list
tools = [calculate_word_count, wikipedia_tool]

# =====================================================================
# 2. SET UP LLM AND BIND TOOLS
# =====================================================================
# Make sure your GROQ_API_KEY environment variable is set!
llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

# bind_tools tells the LLM about the tools and their schemas
llm_with_tools = llm.bind_tools(tools)

# =====================================================================
# 3. CREATE A MANUALLY MAPPED TOOL REGISTRY
# =====================================================================
# We map the exact internal structural string names of the tools
# to their executable Python instances.
tool_map = {
    "calculate_word_count": calculate_word_count,
    "wikipedia": wikipedia_tool  # Structural name for WikipediaQueryRun
}

# =====================================================================
# 4. EXECUTION FUNCTION (USER MANUALLY CALLS THE TOOLS)
# =====================================================================
def ask_llm_manually(prompt: str):
    print(f"\nUser Prompt: \"{prompt}\"")

    response = llm_with_tools.invoke(prompt)

    if response.tool_calls:
        print("-> LLM wants to use a tool.")

        tool_messages = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"   [LLM Request] Tool Name: {tool_name}")
            print(f"   [LLM Request] Tool Arguments: {tool_args}")

            if tool_name in tool_map:
                result = tool_map[tool_name].invoke(tool_args)
                print(f"   [User Execution Result]: {result}")
                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )
            else:
                raise ValueError(
                    f"Tool '{tool_name}' is not in the tool_map registry."
                )

        final_response = llm_with_tools.invoke(
            [HumanMessage(content=prompt), response, *tool_messages]
        )
        print(f"   [LLM Final Answer]: {final_response.content}")
    else:
        print("-> LLM answered directly without tools.")
        print(f"   [LLM Response]: {response.content}")

# --- Test Case 1: Manual trigger for the Custom Tool ---
ask_llm_manually("Count the words in this sentence: Manual tool binding gives you full control.")

# --- Test Case 2: Manual trigger for the In-built Wikipedia Tool ---
ask_llm_manually("Search Wikipedia for information on Marie Curie.")