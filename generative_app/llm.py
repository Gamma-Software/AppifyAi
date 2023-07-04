from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import LLMResult

from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler

import asyncio
from uuid import UUID
from typing import Any, Dict, List, Optional, Union
import os
import re

from streamlit.delta_generator import DeltaGenerator
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
The code MUST be documented as much as possible and you MUST include the necessary imports.

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

class AsyncHandler(AsyncCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain."""

    def __init__(self, message_placeholder: DeltaGenerator) -> None:
        super().__init__()
        self.message_placeholder = message_placeholder
        self.code_block = False
        self.code_extracted = False
        self.full_response = ""

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        class_name = serialized["name"]
        message = ""
        for chunk in "⌛Processing".split():
            message += chunk + " "
            await asyncio.sleep(0.05)
            # Add a blinking cursor to simulate typing
            self.message_placeholder.info(message + "▌")

    async def on_llm_new_token(
        self,
        token: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        # Detect if the token is a code block, to print it all at once
        self.full_response += token

        if not self.code_extracted:
            if "`" in token and not self.code_block:
                self.code_block = True

            if self.code_block and self.full_response.count("`") == 6:
                # We have a full code block, print it now
                self.message_placeholder.markdown(self.full_response)
                self.code_block = False
                self.code_extracted = True

        if self.code_extracted:
            message = ""
            code, explain = parse(self.full_response)

            if code:
                message = f"```python\n{code}\n```\n"
            if explain:
                message += f"{explain}"

            if message is not "":
                # Add a blinking cursor to simulate typing
                self.message_placeholder.markdown(message + "▌")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        self.code_extracted = False
        self.full_response = ""


def llm_chain(message_placeholder: DeltaGenerator) -> LLMChain:
    model_name = "text-davinci-003"
    if st.secrets["openai_api_key"] is None:
        st.error("OpenAI API key is missing! Please add it to your secrets.")
        st.stop()
    llm = OpenAI(temperature=0, openai_api_key=st.secrets["openai_api_key"],
                 max_tokens=2000, model_name=model_name,
                 streaming=True, callbacks=[AsyncHandler(message_placeholder)])
    prompt_template = PromptTemplate(template=template, input_variables=["question", "python_code"])
    python_assistant_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=True)
    return python_assistant_chain

def parse(output):
    python_code = None
    explain_code = None
    pattern = r"```python\n(.*?)\n```.*\n(.*?)$"
    python_code_match = re.search(pattern, output, re.DOTALL | re.MULTILINE)
    if python_code_match:
        python_code = python_code_match.group(1)
        explain_code = python_code_match.group(2)
        if python_code == "None":
            python_code = None
    return python_code, explain_code