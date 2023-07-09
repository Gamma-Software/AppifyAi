import time
import langchain
from langchain.schema.messages import BaseMessage
langchain.debug = True
from langchain.prompts import PromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import LLMResult
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.llms import OpenAI

from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler

import asyncio
from uuid import UUID
from typing import Any, Dict, List, Optional
import os
import re

from streamlit.delta_generator import DeltaGenerator
import streamlit as st

import doc_retriever
from chains.conversational_retrieval_over_code import ConversationalRetrievalCodeChain


python_script = os.path.join(os.getcwd() , "langchain" ,"generated_script.py")


template = """You're an AI assistant specializing in python development. Based on the input provided, you must update the python code that is compatible with python 3.9. Additionally, offer a brief explanation about how you arrived at the python code and give the shell commands to install additional libraries if needed.
If the input is a question, you must explain the code only and additionnaly propose some code. Do not halucinate or make up information.

The current python code you must update is the following:
```python
{python_code}
```
Use the streamlit built in functions in priority. If the user ask to use a specific library, you can use it. If he need to install the python module give the shell command to install it.
The code MUST be documented as much as possible and you MUST include the necessary imports.
Do not use the statement 'if __name__ == "__main__":', place the code directly in the body of the script instead.

Write your anwser in the following format:
```python
the code you generated
```
the explanation of the code you generated

If you did not generated any code (for instance when the user ask a question, not an instruction), this is the format:
```python
None
```
the anwser to the question, or any other anwser you want to give (like greatings, etc.)

Remember to be polite.

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

            if message != "":
                # Add a blinking cursor to simulate typing
                self.message_placeholder.markdown(message + "▌")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        self.code_extracted = False
        self.full_response = ""


class Handler(BaseCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain."""

    def __init__(self, message_placeholder: DeltaGenerator) -> None:
        super().__init__()
        self.message_placeholder = message_placeholder
        self.code_block = False
        self.code_extracted = False
        self.full_response = ""

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, **kwargs: Any) -> Any:
        """Run when chain starts running."""
        message = ""
        for chunk in "⌛Processing".split():
            message += chunk + " "
            time.sleep(0.1)
            # Add a blinking cursor to simulate typing
            self.message_placeholder.info(message + "▌")
        return super().on_chain_start(serialized, inputs, run_id=run_id, parent_run_id=parent_run_id, tags=tags, **kwargs)

    def on_llm_new_token(
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

            if self.code_block and self.full_response.count("`") >= 6:
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

            if message != "":
                # Add a blinking cursor to simulate typing
                self.message_placeholder.markdown(message + "▌")

    def on_chain_end(self, outputs: Dict[str, Any], *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
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
    python_assistant_chain = LLMChain(llm=llm, prompt=prompt_template, verbose=False)
    return python_assistant_chain

def load_conversation_chain(message_placeholder: DeltaGenerator, openai_api_key: str = None) -> ConversationalRetrievalCodeChain:
    model_name = "text-davinci-003"
    model_name = "gpt-3.5-turbo-16k"
    if st.secrets["openai_api_key"] is None:
        st.error("OpenAI API key is missing! Please add it to your secrets.")
        st.stop()
    if openai_api_key is None:
        openai_api_key = st.secrets["openai_api_key"]
    llm = ChatOpenAI(model_name=model_name, temperature=0, openai_api_key=openai_api_key,
                 max_tokens=2000, streaming=True, callbacks=[Handler(message_placeholder)])  # 'ada' 'gpt-3.5-turbo' 'gpt-4',
    condense_question_llm = OpenAI(model_name=model_name, temperature=0,
                                   openai_api_key=openai_api_key,
                                   max_tokens=2000)  # 'ada' 'gpt-3.5-turbo' 'gpt-4',
    retriever = doc_retriever.load_streamlit_doc_retriever()
    qa_over_streamlit_code = ConversationalRetrievalCodeChain.from_llm(llm=llm, retriever=retriever,
                                                                       condense_question_llm=condense_question_llm,
                                                                       return_source_documents=True,
                                                                       max_tokens_limit=2000,
                                                                       verbose=False)
    return qa_over_streamlit_code

def load_agent():
    if st.secrets["openai_api_key"] is None:
        st.error("OpenAI API key is missing! Please add it to your secrets.")
        st.stop()
    doc_chain = doc_retriever.load_streamlit_doc_chain(
        OpenAI(temperature=0, max_tokens=2000, openai_api_key=st.secrets["openai_api_key"]))

    tools = [
        Tool(
            name="Streamlit up to date source code",
            func=doc_chain.run,
            description="useful for when you need to answer questions about the streamlit Python API. Input should be a fully formed question.",
        ),
    ]

    model_name = "text-davinci-003"
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm=OpenAI(openai_api_key=st.secrets["openai_api_key"], max_tokens=2000, temperature=0, model_name=model_name)
    agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=False, memory=memory)
    return agent_chain

def load_chat_agent():
    if st.secrets["openai_api_key"] is None:
        st.error("OpenAI API key is missing! Please add it to your secrets.")
        st.stop()
    doc_chain = doc_retriever.load_streamlit_doc_chain(
        OpenAI(temperature=0, max_tokens=2000, openai_api_key=st.secrets["openai_api_key"]))

    tools = [
        Tool(
            name="Streamlit up to date source code",
            func=doc_chain.run,
            description="useful for when you need to answer questions about the streamlit Python API. Input should be a fully formed question.",
        ),
    ]

    model_name = "text-davinci-003"
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOpenAI(openai_api_key=st.secrets["openai_api_key"], max_tokens=2000, temperature=0, model_name=model_name)
    agent_chain = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=False, memory=memory)
    return agent_chain

def parse(output):
    python_code = None
    explain_code = None
    pattern = r"```python(.*?)```(.*?)$"
    python_code_match = re.search(pattern, output, re.DOTALL)
    if python_code_match:
        python_code = python_code_match.group(1)
        explain_code = python_code_match.group(2)
        if python_code == "None":
            python_code = None
    return python_code, explain_code