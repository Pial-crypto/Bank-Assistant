import requests
import re

from app.config import OLLAMA_MODEL, OLLAMA_URL


PHRASE_MAP = {
    r"amar card hariye geche": "My card has been lost",
    r"amar card hariye gese": "My card has been lost",
    r"card hariye geche": "The card has been lost",
    r"card churi hoye geche": "The card has been stolen",
    r"amar card churi hoye geche": "My card has been stolen",
}

BANGLISH_MARKERS = {
    "amar", "ami", "apnar", "koto", "kivabe",
    "kibhabe", "korbo", "korini", "lagbe",
    "khulte", "geche", "gese", "hariye",
    "ekhon", "kothay", "janabo", "dorkar",
    "hobe", "hoy", "hoye", "nibo", "nite",
    "pabo", "ache", "nei", "chai", "diben",
    "kore", "keno", "jonno", "ki",
}


def is_banglish(text):
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    return len(words.intersection(BANGLISH_MARKERS)) >= 2


def apply_phrase_mapping(query):

    normalized = query.lower()

    for pattern, replacement in PHRASE_MAP.items():
        if re.search(pattern, normalized):
            normalized = re.sub(
                pattern,
                replacement,
                normalized,
                flags=re.IGNORECASE
            )

    return normalized


def normalize_query(query):

    if not is_banglish(query):
        return query

    mapped_query = apply_phrase_mapping(query)

    # If a known banking phrase was translated,
    # preserve it and normalize only the remaining text.
    if mapped_query != query.lower():
        return mapped_query

    prompt = f"""
Translate the complete Banglish question into English.

IMPORTANT:
- Preserve every meaningful detail.
- Never remove the subject or the main event.
- Do not answer the question.
- Do not summarize.
- Translate the entire sentence.
- If unsure about a word, preserve its meaning as closely as possible.

Examples:

Amar card hariye geche, ekhon ki korbo?
= My card has been lost. What should I do now?

Savings account khulte ki ki documents lagbe?
= What documents are required to open a savings account?

Personal loan er interest rate koto?
= What is the interest rate on a personal loan?

Customer question:
{query}

Return only the complete English translation.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Translate Banglish faithfully without omitting meaning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=30
        )

        response.raise_for_status()

        translated = response.json()["message"]["content"].strip()

        if translated:
            print(f"Normalized query: {translated}")
            return translated

    except Exception as error:
        print(f"Normalization failed: {error}")

    return query