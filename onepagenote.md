Nirbhor Bank – Offline Bilingual AI Assistant

Project Submission Note | AI Engineer – Round 2, Task 2

1. Project Overview

The Nirbhor Bank AI Assistant is an offline, FAQ-based bilingual banking assistant designed to answer customer questions in English, Bangla, and Banglish. It uses only the provided bank-faq.csv dataset as its knowledge source. If a question cannot be confidently matched to the available FAQs, the assistant provides a human-support fallback instead of generating an unsupported answer.

2. Technical Approach

The project uses a Retrieval-Augmented Generation (RAG) architecture:

Language handling: Detects English, Bangla, and Banglish queries and applies normalization where needed.

Semantic retrieval: Uses paraphrase-multilingual-MiniLM-L12-v2 to generate multilingual embeddings and retrieve relevant FAQ entries.

Local language model: Uses Qwen2.5:3B through Ollama for Banglish normalization and response translation.

Confidence validation: Applies a similarity threshold of 0.70 and a top-result margin threshold of 0.02 to reduce unsupported answers.

Fallback handling: Uses a predefined human-support response when the system cannot confidently answer.

The application is implemented in Python using Sentence Transformers, PyTorch, Pandas, and Requests.

3. Testing and Evaluation

The assistant was evaluated using the provided 40-question mixed-language test set, containing 30 answerable and 10 unsupported questions.

Evaluation Metric

Result

Total questions

40

Correct answers

24/30

Correct fallback responses

9/10

Overall correct responses

33/40

Overall accuracy

82.50%

Average response time

6.684 seconds

Minimum response time

0.030 seconds

Maximum response time

40.852 seconds

Total evaluation time

267.350 seconds

Online model comparison: Gemini was also tested against the same questions. It identified the expected FAQ information for the 30 answerable questions and recognized the 10 unsupported questions. However, some unsupported responses included information beyond the supplied FAQ, and the required fallback and language-consistency rules were not consistently followed. Response-time comparison was unavailable.

4. Challenges and Limitations

The most challenging part was distinguishing genuinely answerable questions from semantically similar but unsupported questions, particularly across Bangla and Banglish. Some valid questions were rejected by the confidence gate, while one unsupported question was incorrectly accepted during evaluation.

Other limitations include:

Banglish normalization and translation may occasionally produce imperfect language.

Local model response times depend on available hardware.

The assistant does not currently connect users to a real human-support system.

Evaluation results reflect the provided 40-question test set and do not establish performance on unseen questions.

5. Future Improvements

Improve Bangla and Banglish normalization and translation quality.

Improve retrieval confidence calibration to balance correct answers and safe fallback behavior.

Optimize local inference speed.

Integrate a real human-support handoff mechanism.

Expand testing when additional approved evaluation data becomes available.

6. Conclusion

The project demonstrates a working offline bilingual banking assistant that retrieves answers from a controlled FAQ dataset and uses confidence-based fallback handling. The evaluation achieved 82.50% overall correctness on the supplied test set. Further improvements are needed in retrieval reliability, language consistency, and response speed.

Knowledge source: Provided bank-faq.csv dataset only.
Local model: Qwen2.5:3B via Ollama.
Embedding model: paraphrase-multilingual-MiniLM-L12-v2.