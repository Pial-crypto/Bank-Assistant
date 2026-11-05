import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "models/qwen-banglish-lora"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float32,
    device_map="cpu"
)

print("Loading fine-tuned adapter...")
model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
model.eval()

def normalize_banglish(query):
    messages = [
        {
            "role": "user",
            "content": (
                "Normalize this Banglish banking query into a clear "
                "English banking question. Return only the normalized question:\n"
                + query
            )
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            repetition_penalty=1.1
        )

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


test_queries = [
    "amar account er balance kivabe dekhbo?",
    "debit card hariye gele ki korbo?",
    "loan er interest rate koto?",
    "credit card er bill kokhon dite hobe?"
]

for query in test_queries:
    print("\nBanglish:", query)
    print("Normalized:", normalize_banglish(query))