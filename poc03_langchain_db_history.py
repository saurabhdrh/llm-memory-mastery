from pathlib import Path

from dotenv import load_dotenv
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

load_dotenv()


def print_turn(turn_label: str, role: str, content: str) -> None:
    print("\n" + "-" * 60)
    print(f"{turn_label}: {role}")
    print(content)


llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Use the thread-specific chat history."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm

db_path = Path("chat_history.db")
db_url = f"sqlite:///{db_path.resolve()}"


def get_session_history(session_id: str) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(session_id=session_id, connection=db_url)


with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

for session_id in ["thread_1", "thread_2"]:
    history = get_session_history(session_id)
    history.clear()

print("=" * 60)
print("POC 03: Persistent Multi-Thread Chat History")
print("Each session_id is a separate conversation thread.")
print("=" * 60)

call_1 = ("thread_1", "My name is Mukul. I work on OLMS.")
call_2 = ("thread_2", "What is my name?")
call_3 = ("thread_1", "What is my name and which project do I work on?")

for session_id, question in [call_1, call_2, call_3]:
    response = with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )
    print_turn(f"Thread {session_id}", "User", question)
    print_turn(f"Thread {session_id}", "AI", response.content)

print("\n" + "=" * 60)
print("Thread 1 stored messages:")
for item in get_session_history("thread_1").messages:
    print(type(item).__name__, "-", item.content)

print("\nThread 2 stored messages:")
for item in get_session_history("thread_2").messages:
    print(type(item).__name__, "-", item.content)

print("\nLesson: this supports multiple persistent chat threads, but it stores raw chat history. It does not automatically save durable facts across different chats.")
print("=" * 60)

turn_number = 4
while True:
    user_choice = input("\nDo you want to continue in a persistent thread? (y/n): ").strip().lower()
    if user_choice not in {"y", "yes"}:
        print("Ending POC 03 interactive chat.")
        break

    thread_choice = input("Choose thread_id (thread_1 or thread_2): ").strip()
    if thread_choice not in {"thread_1", "thread_2"}:
        print("Invalid thread selection. Use 'thread_1' or 'thread_2'.")
        continue

    question = input("Type your question (or 'exit' to quit): ").strip()
    if question.lower() in {"exit", "quit", "q"}:
        print("Ending POC 03 interactive chat.")
        break

    response = with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": thread_choice}},
    )
    print_turn(f"Turn {turn_number} (Thread {thread_choice})", "User", question)
    print_turn(f"Turn {turn_number} (Thread {thread_choice})", "AI", response.content)
    turn_number += 1
