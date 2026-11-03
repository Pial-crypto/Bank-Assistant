from app.retriever import FAQRetriever


def main():

    retriever = FAQRetriever()

    test_queries = [
        "What documents are needed to open a savings account?",
        "Savings account khulte ki ki documents lagbe?",
        "আমার কার্ড হারিয়ে গেছে, কী করব?",
        "Amar card hariye geche, ekhon ki korbo?",
        "Personal loan er interest rate koto?",
    ]

    for query in test_queries:

        print("\n" + "=" * 65)
        print("CUSTOMER:", query)

        results = retriever.search(query)

        for result in results:

            print("\nFAQ ID:", result["id"])
            print("Topic:", result["topic"])
            print("FAQ Question:", result["question"])
            print("Similarity:", result["similarity"])
            print("Relevant:", result["is_relevant"])
            print("Answer:", result["answer"])


if __name__ == "__main__":
    main()