from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import RegexParser
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.llms import OpenAI
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

The python code you must update is the following:
```python
{python_code}
```

Use the streamlit built in functions in priority. If the user ask to use a specific library, you can use it. If he need to install the python module give the shell command to install it.
Very important: the code must be documented as much as possible and don't forget about the imports.

Write your anwser in the following format: the code and explanation in markdown format

Question: {question}

Answer:"""

def setup(openai_api_key: str):
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    prompt_template = PromptTemplate(template=template, input_variables=["question", "python_code"])
    python_assistant_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)
    return python_assistant_chain

def parse(output):
    python_code = None
    explain_code = None
    python_code_match = re.search(r"```python\n(.*?)\n```\n(.*)", output, re.DOTALL)
    python_code = python_code_match.group(1)
    explain_code = python_code_match.group(2)
    return python_code, explain_code