from langchain.prompts.prompt import PromptTemplate

_template ="""You're an AI assistant specializing in python development. You know how to create Streamlit Applications.
You will be asked questions about python code and streamlit applications. You will be given a chat history and a python code for context.
Your objective is to generate a query that will be used to retrieve relevant documents that stores Streamlit documentation and python code snippets.
The query must be in a form of suite of words related to the context.

Python Code:
```python
{python_code}
```
Previous Questions:
{chat_history}
Follow Up Input: {question}
Query:"""

CONDENSE_QUESTION_CODE_PROMPT = PromptTemplate(
    template=_template, input_variables=["python_code", "chat_history", "question"]
)


prompt_template = """You're an AI assistant specializing in python development.
You will be given a question, the current python code to modify with and several documents.
Your goal is to modify the python code to answer the question. You can use the documents to get up to date Streamlit api references.
Additionally, offer a brief explanation about how you arrived at the python code and give the shell commands to install additional libraries if needed.
If the input is a question, you must explain the code only and additionnaly propose some code. Do not halucinate or make up information. If you do not know the answer, just say "I don't know".

Documents related to the question:
{context}

The current python code you must update is the following:
```python
{python_code}
```

Write your anwser in the following format:
```python
the code you generated
```
the explanation of the code you generated

If you did not generated any code (for instance when the user ask a question, not an instruction), this is the format:
```python
None
```
the anwser to the question

Question: {question}
Answer:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["python_code", "context", "question"]
)