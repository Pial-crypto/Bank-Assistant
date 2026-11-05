**# Nirbhor Bank --- Offline Bilingual Bank Assistant**



An offline, FAQ-grounded bilingual banking assistant for the fictional

Nirbhor Bank PLC and its NB Go mobile banking service. The assistant

accepts questions in English, Bangla, and Banglish and responds in the

language used by the customer.



**## Project Overview**



This project was developed for the \*\*BIAI AI Engineer Round 2 --- Task

2\*\*.



The assistant uses a local language model and a multilingual semantic

retrieval system to answer banking questions using only the provided

\`bank-faq.csv\` dataset.



If a question is outside the supported FAQ information or the system

cannot confidently identify a relevant FAQ, it returns a fallback

response:



\> I don't know, let me connect you to a person



The fallback is localized for Bangla and Banglish queries.



**## Key Features**



\-   **\*\*Multilingual input:\*\*** English, Bangla, and Banglish.

\-   **\*\*Language-matched responses:\*\*** Generates responses in the

    customer's language.

\-   **\*\*FAQ-only knowledge:\*\*** Uses the supplied bank FAQ dataset as its

    source of banking information.

\-   **\*\*Semantic retrieval:\*\*** Uses multilingual sentence embeddings to

    identify relevant FAQ entries.

\-   **\*\*Confidence-based rejection:\*\*** Uses similarity and ranking-margin

    thresholds to reduce unsupported answers.

\-   **\*\*Local LLM:\*\*** Uses Qwen 2.5 3B through Ollama.

\-   **\*\*Human-support fallback:\*\*** Offers to connect the customer to a

    person when the system cannot answer confidently.

\-   **\*\*Offline operation:\*\*** Runs locally after the required models and

    dependencies have been downloaded.



**## Technology Stack**



  Component               Technology

**&#xA0; ----------------------- -----------------------------------------**

  Programming language    Python

  Local language model    Qwen 2.5 3B

  Local model runtime     Ollama

  Embedding model         \`paraphrase-multilingual-MiniLM-L12-v2\`

  Retrieval               Semantic similarity search

  Data source             CSV

  Data processing         Pandas

  Embedding computation   Sentence Transformers, PyTorch

  HTTP requests           Requests



**## Project Structure**



\`\`\` text

AI-Bank-Assistant/

├── app/

│   ├── \_\_init\_\_.py

│   ├── assistant.py

│   ├── retriever.py

│   ├── language.py

│   └── config.py

├── data/

│   ├── bank-faq.csv

│   └── test-questions.csv

├── evaluation/

│   ├── ground-truth.csv

│   ├── retrieval-results.csv

│   └── final-results.csv

├── tests/

├── app.py

├── evaluate.py

├── requirements.txt

└── README.md

\`\`\`



**## How It Works**



1\.  The customer submits a question in English, Bangla, or Banglish.

2\.  The language-handling module identifies the language and normalizes

    Banglish queries where necessary.

3\.  The retriever compares the question against the FAQ questions and

    their search aliases using multilingual embeddings.

4\.  The assistant ranks the relevant FAQ entries.

5\.  A confidence gate checks the top result's similarity score and its

    margin over the second-ranked result.

6\.  If the result passes the confidence checks, the assistant responds

    using the retrieved FAQ information.

7\.  If the result fails the checks, the assistant returns the

    human-support fallback response.



**## Confidence Thresholds**



The current implementation uses:



\-   **\*\*Similarity threshold:\*\*** \`0.70\`

\-   **\*\*Ranking-margin threshold:\*\*** \`0.02\`



These thresholds were selected based on experiments with the supplied

evaluation questions. They are empirical settings, not guarantees of

correctness for every possible customer query.



**## Installation and Setup**



**### 1. Clone the repository**



\`\`\` bash

git clone https\://github.com/Pial-crypto/Bank-Assistant.git

cd Bank-Assistant

\`\`\`



If the repository contains the project files inside a nested

\`AI-Bank-Assistant\` directory, enter that directory before continuing.



**### 2. Create and activate a virtual environment**



Windows PowerShell:



\`\`\` powershell

python -m venv .venv

.venv\Scripts\Activate.ps1

\`\`\`



**### 3. Install dependencies**



\`\`\` bash

pip install -r requirements.txt

\`\`\`



**### 4. Install Ollama**



Download and install Ollama from \<https\://ollama.com/>.



Pull the required model:



\`\`\` bash

ollama pull qwen2.5:3b

\`\`\`



Make sure Ollama is running locally.



**### 5. Run the application**



\`\`\` bash

python app.py

\`\`\`



**### 6. Run the evaluation**



\`\`\` bash

python evaluate.py

\`\`\`



The evaluation results are saved in:



\`\`\` text

evaluation/final-results.csv

\`\`\`



**\*\*Note:\*\*** Confirm the repository's actual folder layout and the

evaluation output path before publishing. The commands above assume

\`app.py\` and \`evaluate.py\` are in the current project directory.



**## Evaluation Results**



The assistant was evaluated using the 40 questions supplied for the

assignment.



  Metric                                  Result

**&#xA0; ---------------------------- -----------------**

  Total questions                             40

  Answerable questions                        30

  Correct FAQ answers                    24 / 30

  Unsupported questions                       10

  Correct fallback responses              9 / 10

  Overall correct                        33 / 40

  Overall accuracy                    **\*\*82.50%\*\***

  Average response time            6.684 seconds

  Maximum response time           40.852 seconds

  Minimum response time            0.030 seconds

  Total evaluation time          267.350 seconds



**### Evaluation Interpretation**



\-   The assistant correctly answered 24 of the 30 answerable questions.

\-   It correctly rejected 9 of the 10 unsupported questions.

\-   One unsupported question was incorrectly accepted as an FAQ answer.

\-   Six answerable questions were not answered correctly.



The results show that the system works, but retrieval accuracy and

unsupported-question detection still need improvement.



**## Online Model Comparison**



The same supplied questions were also compared against an online Gemini

model.



The comparison indicated that Gemini identified the expected FAQ

information for the 30 answerable questions and recognized the 10

unsupported questions. However, its unsupported responses did not

consistently follow the required fallback wording, and some responses

introduced information beyond the supplied FAQ.



A reliable latency comparison was not available.



Therefore, the online model's results should not be interpreted as a

fully compliant 40/40 result.



**## Optional Experiment: Banglish Fine-Tuning**



**\*\*Kaggle Notebook:\*\*** [View Banglish Fine-Tuning

Experiment]\(https\://www\.kaggle.com/code/mahamudulhassanpial/notebook35aceba83e)



As an additional experiment, the base Qwen2.5-3B model was fine-tuned to

normalize Banglish banking queries into clear English banking questions.



**### Training Setup**



\-   **\*\*Base model:\*\*** \`Qwen/Qwen2.5-3B-Instruct\`

\-   **\*\*Training environment:\*\*** Kaggle with NVIDIA Tesla T4 GPU

\-   **\*\*Fine-tuning method:\*\*** QLoRA with 4-bit quantization and LoRA

    adapters

\-   **\*\*Training data:\*\*** Banglish query aliases extracted from the

    supplied banking FAQ dataset

\-   **\*\*Training objective:\*\*** Convert Banglish banking queries into clear

    English banking questions

\-   **\*\*Training epochs:\*\*** 3

\-   **\*\*Best adapter:\*\*** Epoch 1, selected using validation loss



**### Training Results**



  Epoch     Training Loss   Validation Loss

**&#xA0; ------- --------------- -----------------**

  1                1.9321        **\*\*0.8893\*\***

  2                0.5747            1.0710

  3                0.2298            1.2635



Training loss decreased across the epochs, but validation loss increased

after the first epoch. This indicates signs of overfitting. Therefore,

the Epoch 1 adapter with the lowest validation loss was selected for

testing.



**### Base Model vs Fine-Tuned Model**



The two models were evaluated directly on the Banglish normalization

task, without running the FAQ retrieval system.



The evaluation used the 10 Banglish questions detected in the supplied

40-question test dataset. Semantic similarity was calculated against the

corresponding English FAQ questions.



  Metric                          Base Qwen2.5-3B   Fine-Tuned Qwen2.5-3B

**&#xA0; ----------------------------- ----------------- -----------------------**

  Average semantic similarity          **\*\*0.7670\*\***                  0.6805

  Average generation time           **\*\*1.240 sec\*\***               1.509 sec



Additional comparison:



\-   Fine-tuned model improved on 2 questions.

\-   Performance declined on 7 questions.

\-   Performance remained unchanged on 1 question.



**### Fine-Tuning Conclusion**



The fine-tuning process completed successfully, and the adapter was

saved. However, the experiment did not demonstrate an improvement over

the original base model.



The base model achieved higher average semantic similarity and lower

average generation time on the evaluated Banglish queries.



The increasing validation loss also suggests overfitting. Further

improvements would require better training examples, more representative

data, and improved training configuration.



This experiment is reported separately from the main RAG evaluation

because it measures Banglish normalization quality rather than

end-to-end banking question-answering accuracy.



**\*\*Important:\*\*** The semantic similarity score is not a direct measure of

answer correctness. The comparison is limited to the evaluated Banglish

queries and should not be treated as proof of performance on unseen

queries.



**## Limitations**



\-   The assistant's accuracy depends on the coverage and quality of the

    supplied FAQ dataset.

\-   Similarity-based retrieval can occasionally match an unsupported

    question to an unrelated FAQ.

\-   Banglish normalization and response translation depend on the local

    language model.

\-   Translation may fail or return English text instead of the

    customer's original language.

\-   The fallback only offers human support; it does not initiate a real

    call, create a support ticket, or connect to a live agent.

\-   Local inference speed depends on the computer's hardware and

    model-loading state.

\-   The confidence thresholds were tuned using the assignment's supplied

    evaluation questions, so the reported performance should not be

    treated as proof of general performance on unseen questions.

\-   The optional fine-tuning experiment did not improve the measured

    Banglish normalization performance.



**## Future Improvements**



\-   Improve retrieval accuracy for semantically similar banking

    questions.

\-   Improve Banglish normalization and language detection.

\-   Improve fallback and translation reliability.

\-   Experiment with more representative Banglish training examples and

    improved fine-tuning configurations.

\-   Add a real customer-support integration if the bank provides an

    appropriate support API.

\-   Optimize local inference latency.



**## Data and Privacy**



This project uses the fictional Nirbhor Bank FAQ dataset supplied for

the assignment. It does not use real customer records or real banking

credentials.



**## Author**



Developed as part of the \*\*BIAI AI Engineer Round 2 technical

assignment\*\*.



**## How This Project Addresses the Evaluation Criteria**



The assignment uses the following scoring rubric. This section explains

where each criterion is demonstrated in the project and distinguishes

completed technical work from separate presentation deliverables.



**&#xA0; ----------------------------------------------------------------------------**

  Evaluation criterion                        Weight Evidence in this project

**&#xA0; --------------------- ---------------------------- -------------------------**

  Loom presentation:                             20% The Loom presentation is

  clear, confident,                                  a separate submission

  explains the why, and                              deliverable. It should

  understandable to a                                demonstrate the running

  non-technical person                               assistant, explain why

                                                     answers are restricted to

                                                     the supplied FAQ, show

                                                     English/Bangla/Banglish

                                                     examples, and communicate

                                                     the evaluation results

                                                     and limitations.



  Works correctly on                             25% The assistant uses the

  the supplied sample                                supplied \`bank-faq.csv\`

  files                                              and was evaluated against

                                                     the 40 supplied test

                                                     questions. The measured

                                                     result was 33/40 overall

                                                     (82.50%), including 24/30

                                                     correct answerable FAQ

                                                     responses and 9/10

                                                     correct

                                                     unsupported-question

                                                     fallbacks.



  Clear, sensible                                20% The implementation

  implementation that                                separates language

  handles mistakes                                   handling, FAQ retrieval,

                                                     assistant logic, and

                                                     configuration into

                                                     modules. It uses input

                                                     validation, retrieval

                                                     confidence checks, and a

                                                     human-support fallback

                                                     when it cannot

                                                     confidently answer.



  Solving the hardest                            15% A key challenge was

  part of the task                                   handling Banglish queries

                                                     while keeping answers

                                                     grounded in the limited

                                                     FAQ dataset. The system

                                                     combines Banglish

                                                     normalization,

                                                     multilingual semantic

                                                     retrieval, and confidence

                                                     checks to reduce

                                                     unrelated FAQ matches.

                                                     Unsupported questions can

                                                     still be incorrectly

                                                     accepted, as shown by the

                                                     evaluation.



  Clean code that can                            10% The README provides

  be run using the                                   environment setup,

  README                                             dependency installation,

                                                     Ollama model setup,

                                                     application launch, and

                                                     evaluation commands.

                                                     These instructions assume

                                                     the repository contains

                                                     the documented project

                                                     structure; verify the

                                                     actual repository layout

                                                     before submission.



  Honesty about what                             10% The results and

  does not work                                      limitations are reported

                                                     explicitly. The assistant

                                                     missed six answerable

                                                     questions and incorrectly

                                                     accepted one unsupported

                                                     question. The optional

                                                     fine-tuning experiment

                                                     also did not improve the

                                                     measured Banglish

                                                     normalization similarity.

  ----------------------------------------------------------------------------



**### Hardest Technical Challenge**



The most difficult part was not simply generating a banking response. It

was deciding whether a customer's question genuinely matched one of the

30 supplied FAQ entries.



This was challenging because: - Customers may express the same banking

intent using English, Bangla, or Banglish. - Different questions can

contain similar words but require different answers. - An unsupported

question can still receive a high semantic similarity score against an

unrelated FAQ. - The assistant must prefer a safe fallback over

inventing banking information when the match is uncertain.



The implementation addresses this with language normalization,

multilingual embeddings, FAQ ranking, and similarity/margin-based

rejection. The evaluation shows that this approach is useful but not

perfect.



**### What Does Not Work Reliably Yet**



\-   Six of the 30 answerable test questions were not answered correctly.

\-   One of the 10 unsupported questions was incorrectly accepted as an

    FAQ answer.

\-   Banglish normalization and response translation may fail or produce

    output in the wrong language.

\-   The optional QLoRA fine-tuning experiment did not improve the

    measured semantic similarity: the base model scored 0.7670, while

    the fine-tuned model scored 0.6805 on the evaluated Banglish

    queries.

\-   The fallback message does not create a real support ticket or

    connect the customer to a live representative.

\-   The reported evaluation uses the assignment's supplied 40 questions;

    it does not establish performance on all possible banking questions.



**### Submission Checklist**



\-   [ ] Confirm the GitHub repository contains the application code,

    supplied sample data permitted for submission, evaluation files,

    \`requirements.txt\`, and this README.

\-   [ ] Verify the README commands against the actual repository folder

    structure.

\-   [ ] Record the Loom presentation and include its link in the

    submission form or submission note.

\-   [ ] Include the one-page submission note with the measured results,

    challenges, limitations, and next steps.

\-   [ ] Keep the optional fine-tuning notebook available as supporting

    evidence: [Kaggle Fine-Tuning

    Notebook]\(https\://www\.kaggle.com/code/mahamudulhassanpial/notebook35aceba83e).
