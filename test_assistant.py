
from app.assistant import BankAssistant

assistant = BankAssistant()

test_questions = [
    "What is the annual debit card fee?",
    "আমার কার্ড হারিয়ে গেছে, এখন কী করব?",
    "Amar card hariye geche, ekhon ki korbo?",
    "What is today's gold price?",
]

for question in test_questions:

    result = assistant.ask(question)

    print("\nQuestion:", question)
    print("Answer:", result["answer"])
    print("FAQ ID:", result["faq_id"])
    print("Status:", result["status"])

    print("-" * 60)
