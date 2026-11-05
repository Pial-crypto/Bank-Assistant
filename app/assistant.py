
import re
import requests

from app.retriever import FAQRetriever
from app.config import OLLAMA_MODEL, OLLAMA_URL
from app.language import BANGLISH_MARKERS


SIMILARITY_THRESHOLD = 0.70
MARGIN_THRESHOLD = 0.02

FALLBACK = "I don't know, let me connect you to a person"


class BankAssistant:

    def __init__(self):
        print("Initializing Nirbhor Bank Assistant...")

        self.retriever = FAQRetriever()

        print("Bank Assistant is ready.")

    def fallback_response(self, language):
            
        fallback_messages = {
        "english": "I don't know, let me connect you to a person",
        "bangla": "আমি জানি না। আপনাকে একজন প্রতিনিধির সাথে সংযুক্ত করে দিচ্ছি।",
        "banglish": "Ami jani na. Apnake ekjon representative-er sathe connect kore dicchi."
            }
       

        # answer = self.translate_response(FALLBACK, language)

        return {
        "answer": fallback_messages.get(
            language,
            fallback_messages["english"]
        ),
        "faq_id": None,
        "status": "fallback"
    }

    def detect_language(self, text):

        # Bangla script detection
        if re.search(r"[\u0980-\u09FF]", text):
            return "bangla"

        # Banglish detection using Romanized Bangla markers
        words = set(re.findall(r"[a-zA-Z]+", text.lower()))

        if words.intersection(BANGLISH_MARKERS):
            return "banglish"

        return "english"

    def translate_response(self, text, language):

        if language == "english":
            return text

        if language == "bangla":
            instruction = """
Translate the following English bank answer into natural,
clear Bangla using Bengali script.

Rules:
- Use proper, natural Bangla.
- Preserve all numbers, amounts, dates and conditions.
- Do not add or remove any information.
- Output only the translated answer.
"""

        else:
            instruction = """
Convert the following English bank answer into natural Banglish.

IMPORTANT:
- Banglish means Bengali language written ONLY with English/Roman letters.
- Do NOT use Bengali script at all.
- Do NOT translate into English.
- Use natural Bangladeshi conversational Banglish.
- Preserve all numbers, amounts, dates and conditions.
- Do not add or remove any information.
- Output ONLY the Banglish answer.

Example:
English: Please call our hotline to block your lost card.
Banglish: Apnar hariye jawa card block korar jonno amader hotline-e call korun.

English: You can collect your new card from the branch within 7 working days.
Banglish: Apni 7 working days-er moddhe branch theke notun card collect korte parben.
"""

        prompt = f"""
{instruction}

Text:
{text}
"""

        for attempt in range(2):

            try:
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a professional Bengali and Banglish "
                                    "translator for a Bangladesh bank."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0
                        }
                    },
                    timeout=30
                )

                response.raise_for_status()

                translated = response.json()["message"]["content"].strip()

                if not translated:
                    continue

                # Validate that Banglish contains no Bengali script
                if language == "banglish":

                    if re.search(r"[\u0980-\u09FF]", translated):

                        prompt += """
Your previous response incorrectly used Bengali script.
Rewrite it using ONLY English/Roman letters.
Do not use a single Bengali-script character.
"""

                        continue

                return translated

            except Exception as error:
                print(f"Response translation failed: {error}")

        print(
            "Translation validation failed. "
            "Returning original FAQ answer."
        )

        return text

    def ask(self, question):

        if not isinstance(question, str) or not question.strip():
            return self.fallback_response("english")

        question = question.strip()

        language = self.detect_language(question)

        print(f"\nUser question: {question}")
        print(f"Detected language: {language}")

        # Retrieve FAQ candidates
        results = self.retriever.search(
            question,
            top_k=len(self.retriever.faq)
        )

        if len(results) < 2:
            print("Not enough FAQ results.")
            return self.fallback_response(language)

        top1 = results[0]
        top2 = results[1]

        top1_score = float(top1["similarity"])
        top2_score = float(top2["similarity"])

        margin = top1_score - top2_score

        print(
            f"Top FAQ: {top1['id']} | "
            f"Score: {top1_score:.4f}"
        )

        print(
            f"Second FAQ: {top2['id']} | "
            f"Score: {top2_score:.4f}"
        )

        print(f"Score margin: {margin:.4f}")

        # Confidence gate
        if (
            top1_score < SIMILARITY_THRESHOLD
            or margin < MARGIN_THRESHOLD
        ):

            print("Confidence gate rejected the question.")

            return self.fallback_response(language)

        
        faq_answer = str(top1["answer"]).strip()

        if not faq_answer:
            print("FAQ answer is empty.")
            return self.fallback_response(language)

        
        final_answer = self.translate_response(
            faq_answer,
            language
        )

        print(f"Selected FAQ: {top1['id']}")
        print(f"Assistant response: {final_answer}")

        return {
            "answer": final_answer,
            "faq_id": str(top1["id"]),
            "status": "answered"
        }
