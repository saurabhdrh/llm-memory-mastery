from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()


def print_turn(turn_label: str, role: str, content: str) -> None:
    print("\n" + "-" * 60)
    print(f"{turn_label}: {role}")
    print(content)


llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Use the chat history when answering."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm
session_store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]


with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

session_id = "mukul-thread-1"

print("=" * 60)
print("POC 02: LangChain In-Memory Chat History")
print(f"Session ID: {session_id}")
print("=" * 60)

first_question = "My name is Mukul. I work on OLMS."
first_answer = with_history.invoke(
    {"question": first_question},
    config={"configurable": {"session_id": session_id}},
)
print_turn("Turn 1", "User", first_question)
print_turn("Turn 1", "AI", first_answer.content)

follow_up = "What is my name and which project do I work on?"
second_answer = with_history.invoke(
    {"question": follow_up},
    config={"configurable": {"session_id": session_id}},
)
print_turn("Turn 2", "User", follow_up)
print_turn("Turn 2", "AI", second_answer.content)

print("\n" + "=" * 60)
print("Lesson: the same session remembers previous messages in memory.")
print("Limitation: this memory is lost when the app restarts.")
print("=" * 60)

turn_number = 3
while True:
    user_choice = input("\nDo you want to ask another question in the same session? (y/n): ").strip().lower()
    if user_choice not in {"y", "yes"}:
        print("Ending POC 02 interactive chat.")
        break

    follow_up = input("Type your question (or 'exit' to quit): ").strip()
    if follow_up.lower() in {"exit", "quit", "q"}:
        print("Ending POC 02 interactive chat.")
        break

    answer = with_history.invoke(
        {"question": follow_up},
        config={"configurable": {"session_id": session_id}},
    )
    print_turn(f"Turn {turn_number}", "User", follow_up)
    print_turn(f"Turn {turn_number}", "AI", answer.content)
    turn_number += 1
