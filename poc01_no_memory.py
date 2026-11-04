from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def print_turn(turn_label: str, role: str, content: str) -> None:
    print("\n" + "-" * 60)
    print(f"{turn_label}: {role}")
    print(content)


llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

print("=" * 60)
print("POC 01: No Memory")
print("The model is stateless. Each call is treated as a fresh conversation.")
print("=" * 60)

first_user_message = "Hi! My name is Mukul and I work on OLMS."
first_response = llm.invoke(first_user_message)
print_turn("Turn 1", "User", first_user_message)
print_turn("Turn 1", "AI", first_response.content)

second_user_message = "What is my name and which project do I work on?"
second_response = llm.invoke(second_user_message)
print_turn("Turn 2", "User", second_user_message)
print_turn("Turn 2", "AI", second_response.content)

print("\n" + "=" * 60)
print("Lesson: the model does not remember previous turns unless we add memory.")
print("=" * 60)

turn_number = 3
while True:
    user_choice = input("\nDo you want to ask a follow-up question? (y/n): ").strip().lower()
    if user_choice not in {"y", "yes"}:
        print("Ending POC 01 interactive chat.")
        break

    follow_up = input("Type your question (or 'exit' to quit): ").strip()
    if follow_up.lower() in {"exit", "quit", "q"}:
        print("Ending POC 01 interactive chat.")
        break

    response = llm.invoke(follow_up)
    print_turn(f"Turn {turn_number}", "User", follow_up)
    print_turn(f"Turn {turn_number}", "AI", response.content)
    turn_number += 1