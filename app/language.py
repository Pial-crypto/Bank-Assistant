
import re
import requests
import unicodedata

from app.config import OLLAMA_MODEL, OLLAMA_URL


BANGLISH_MARKERS = {
    # Pronouns
    "ami", "amar", "amra", "amader",
    "apni", "apnar", "apnara", "apnader",
    "tumi", "tomar", "tomra", "tomader",

    # Question words
    "ki", "kono", "kothay", "kokhon",
    "kobe", "koto", "kotodin", "koydin",
    "koyta", "koita", "koybar",
    "kivabe", "kibhabe", "keno",
    "kon", "konta",

    # Actions and verbs
    "korbo", "korben", "kori", "korini",
    "korechi", "kore", "kora", "korte",
    "korle", "hobe", "hoy", "hoye",
    "hoyeche", "hoyni", "hoyna",
    "hote", "hole", "parbo",
    "pabo", "pawa", "diben", "dibo",
    "deya", "dewa", "nibo", "nite",
    "nile", "niye", "lagbe", "lage",
    "chai", "dorkar", "khulte",
    "khulbo", "khule", "bondho",
    "pathabo", "pathale", "pathate",
    "ashbe", "asche", "jabe", "jabo",
    "jay", "janabo", "bolbo", "bolben",
    "geche", "gese", "hariye",
    "kinle", "gele", "thake", "thakbe",

    # Time and frequency
    "ekhon", "aj", "kal", "por",
    "pore", "proti", "prottek",
    "din", "dine", "mashe",
    "bochor", "bochore", "ghonta",
    "tarikh", "shomoy", "somoy",

    # Money and quantities
    "taka", "hajar", "lakh",
    "khoroch", "dam", "mullo",
    "beton", "beshi", "kom",

    # Location and direction
    "theke", "porjonto", "moddhe",
    "upore", "niche", "baire",
    "vitor", "basha", "basay", "bashay",

    # Connectors
    "naki", "jonno", "sathe",
    "diye", "charai", "shudhu",
    "matro", "er",

    # Common states
    "ache", "nei", "nai",
}


PHRASE_MAP = {
    "amar card hariye geche": "My card has been lost",
    "amar card hariye gese": "My card has been lost",
    "card hariye geche": "The card has been lost",
    "card churi hoye geche": "The card has been stolen",
    "amar card churi hoye geche": "My card has been stolen",
    "cheque er payment": "cheque payment",
}



WORD_MAP = {
    # Debit card
    "dabit": "debit",
    "ডেবিট": "debit",

    # ATM
    "এটিএম": "ATM",

    # SMS
    "এস এম এস": "SMS",
    "এসএম এস": "SMS",
    "এসএমএস": "SMS",

    # NID
    "national identity card": "NID",
    "national id": "NID",
    "জাতীয় পরিচয়পত্র": "NID",
    "জাতীয় পরিচয়পত্র": "NID",
    "এনআইডি": "NID",

    # FDR
    "fixed term deposit": "FDR",
    "fixed deposit": "FDR",
    "ফিক্সড ডিপোজিট": "FDR",

    # Percentage
    "per cent": "percent",
    "শতকরা": "percent",
    "শতাংশ": "percent",
    "শতে": "percent",

    # Annual / yearly
    "every year": "annual",
    "per year": "annual",
    "yearly": "annual",
    "বার্ষিক": "annual",
    "প্রতি বছর": "annual",
    "বছরে": "annual",

    # Remittance
    "রেমিটেন্স": "remittance",
    "রেমিট্যান্স": "remittance",
    "বিদেশ থেকে টাকা পাঠানো": "remittance",
    "বাইরে থেকে টাকা পাঠানো": "remittance",
    "abroad theke taka pathano": "remittance",

    # Penalty
    "জরিমানা": "penalty",
    # "fine": "penalty",
}


def is_banglish(text):
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    matches = words.intersection(BANGLISH_MARKERS)

    return len(matches) >= 2


def apply_phrase_mapping(query):
    mapped = query

    for phrase, replacement in PHRASE_MAP.items():
        mapped = re.sub(
            re.escape(phrase),
            replacement,
            mapped,
            flags=re.IGNORECASE
        )

    return mapped


def apply_word_mapping(query):
    mapped = query

   
    mappings = sorted(
        WORD_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for source, replacement in mappings:

        if re.search(r"[a-zA-Z]", source):
           
            pattern = r"(?<![a-zA-Z])" + re.escape(source) + r"(?![a-zA-Z])"
        else:
            
            pattern = re.escape(source)

        mapped = re.sub(
            pattern,
            replacement,
            mapped,
            flags=re.IGNORECASE
        )

    return mapped


def normalize_query(query):

    if not isinstance(query, str) or not query.strip():
        return query

    query = unicodedata.normalize("NFKC", query).strip()

    
    mapped_query = apply_phrase_mapping(query)
    mapped_query = apply_word_mapping(mapped_query)

   
    if re.search(r"[\u0980-\u09FF]", mapped_query):
        return mapped_query

    
    if not is_banglish(mapped_query):
        return mapped_query

    prompt = f"""
Translate the following complete Banglish banking question into English.

Preserve:
- The exact subject.
- The main action or problem.
- Numbers, amounts and ages.
- Negations and important conditions.
- Banking terms and their intended meaning.

Rules:
- Never answer the question.
- Never summarize.
- Never omit meaningful details.
- Do not invent information.
- Return only the English translation.

Examples:

Amar card hariye geche, ekhon ki korbo?
My card has been lost. What should I do now?

Ek din e koto taka transfer kora jay?
How much money can be transferred in one day?

Debit card er annual fee koto?
What is the annual fee for a debit card?

Input:
{mapped_query}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a faithful Banglish-to-English "
                            "translator for banking questions."
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

        translated = (
            response.json()["message"]["content"].strip()
        )

        if translated and len(translated) >= 5:
            print(f"Normalized query: {translated}")
            return translated

    except Exception as error:
        print(f"Normalization failed: {error}")

    
    return mapped_query
