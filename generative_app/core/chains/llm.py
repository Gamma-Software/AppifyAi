import time
import langchain
from langchain.schema.messages import BaseMessage
import streamlit as st
langchain.debug = st.secrets["langchain"]["debug"]
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
from typing import Any, Dict, List, Optional, Union
import os
import re

from streamlit.delta_generator import DeltaGenerator
import streamlit as st

import chains.doc_retriever as doc_retriever
from chains.conversational_retrieval_over_code import ConversationalRetrievalCodeChain


python_script = os.path.join(os.getcwd() , "langchain" ,"generated_script.py")


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

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], *, run_id: UUID, parent_run_id: Union[UUID, None] = None, tags: Union[List[str], None] = None, **kwargs: Any) -> Any:
        """Run when chain starts running."""
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
        return super().on_llm_new_token(token, run_id=run_id, parent_run_id=parent_run_id, **kwargs)

    def on_chain_end(self, outputs: Dict[str, Any], *, run_id: UUID, parent_run_id: Union[UUID, None] = None, **kwargs: Any) -> Any:
        """Run when chain ends running."""
        self.code_extracted = False
        self.full_response = ""
        return super().on_chain_end(outputs, run_id=run_id, parent_run_id=parent_run_id, **kwargs)

def load_conversation_chain(message_placeholder: DeltaGenerator, openai_api_key: str) -> ConversationalRetrievalCodeChain:
    if openai_api_key is None:
        raise ValueError("OpenAI API key is required to load the chain.")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0, openai_api_key=openai_api_key,
                     streaming=True, callbacks=[Handler(message_placeholder)])
    condense_question_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)
    critique_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key,verbose=False)
    missing_imports_llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key,verbose=False)
    retriever = doc_retriever.load_streamlit_doc_retriever(st.secrets["openai_api_key"],
                                                           chroma_server_host=st.secrets["chroma"]["host"],
                                                           chroma_server_port=st.secrets["chroma"]["port"],
                                                           mode="docker")
    qa_over_streamlit_code = ConversationalRetrievalCodeChain.from_llm(llm=llm, retriever=retriever,
                                                                       condense_question_llm=condense_question_llm,
                                                                       return_source_documents=True,
                                                                       self_critique_llm=critique_llm,
                                                                       missing_imports_llm=missing_imports_llm,
                                                                       return_revision_request=True,
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