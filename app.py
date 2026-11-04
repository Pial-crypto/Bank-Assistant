
from app.assistant import BankAssistant


def main():
    print("=" * 55)
    print("       NIRBHOR BANK - BILINGUAL AI ASSISTANT")
    print("=" * 55)
    print("Languages: English | বাংলা | Banglish")
    print("Type 'exit' or 'quit' to close the assistant.")
    print("-" * 55)

    try:
        assistant = BankAssistant()
    except Exception as error:
        print(f"\nFailed to initialize assistant: {error}")
        return

    while True:
        try:
            question = input("\nYou: ").strip()

            if question.lower() in {"exit", "quit"}:
                print("\nAssistant: Thank you for using Nirbhor Bank Assistant.")
                break

            if not question:
                print("Please enter a question.")
                continue

            result = assistant.ask(question)

            print(f"\nAssistant: {result['answer']}")

            if result.get("status") == "fallback":
                print("[Human support fallback]")

        except KeyboardInterrupt:
            print("\n\nAssistant closed.")
            break
        except Exception as error:
            print(f"\nAn error occurred: {error}")


if __name__ == "__main__":
    main()
