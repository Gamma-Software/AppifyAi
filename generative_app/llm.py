from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import RegexParser
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import RegexParser

import os
import re
import streamlit as st

import langchain
langchain.debug = True

python_script = os.path.join(os.getcwd() , "langchain" ,"generated_script.py")


template = """You're an AI assistant specializing in python development. Based on the input provided, you must update the python code that is compatible with python 3.9. Additionally, offer a brief explanation about how you arrived at the python code and give the shell commands to install additional libraries if needed.
If the input is a question, you must explain the code only and additionnaly propose some code. Do not halucinate or make up information. If you do not know the answer, just say "I don't know".

The current python code you must update is the following:
```python
{python_code}
```
Use the streamlit built in functions in priority. If the user ask to use a specific library, you can use it. If he need to install the python module give the shell command to install it.
The code must be documented as much as possible and you MUST include the necessary imports.

Write your anwser in the following format:code:
```python
the code you generated
```
explain:
the explanation of the code you generated

If you did not generated any code (for instance when the user ask a question, not an instruction), this is the format:code:
```python
None
```
explain:
the anwser to the question

Question: {question}

Answer:"""

def setup(openai_api_key: str):
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key, max_tokens=2000, model_name="text-davinci-003")
    prompt_template = PromptTemplate(template=template, input_variables=["question", "python_code"])
    python_assistant_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)
    return python_assistant_chain

def parse(output):
    python_code = None
    explain_code = None
    pattern = r"code:\n```python\n(.*?)\n```\nexplain:\n(.*?)$"
    python_code_match = re.search(pattern, output, re.DOTALL | re.MULTILINE)
    if python_code_match:
        python_code = python_code_match.group(1)
        explain_code = python_code_match.group(2)
        if python_code == "None":
            python_code = None
    return python_code, explain_code