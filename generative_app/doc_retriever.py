from typing import List
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers.language import LanguageParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
from langchain.vectorstores.base import VectorStoreRetriever

import shutil
import os
import git
import sys

import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def num_tokens_from_string(docs: List[Document], encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = 0
    max_tokens = 0
    for doc in docs:
        if len(encoding.encode(doc.page_content)) > max_tokens:
            max_tokens = len(encoding.encode(doc.page_content))
        num_tokens += len(encoding.encode(doc.page_content))
    return num_tokens, max_tokens

def load_streamlit_docs() -> VectorStoreRetriever:
    # Check if the Chroma database exists
    if not os.path.exists("document_database/streamlit_chroma_db"):
        raise Exception("The Chroma database for Streamlit does not exist. Please run the script `doc_retriever.py` to create it.")

    # load from disk
    retriever = Chroma(persist_directory="document_database/streamlit_chroma_db").as_retriever()
    retriever.search_kwargs["distance_metric"] = "cos"
    retriever.search_kwargs["fetch_k"] = 20
    retriever.search_kwargs["maximal_marginal_relevance"] = True
    retriever.search_kwargs["k"] = 20
    return retriever

if __name__ == "__main__":
    openai_api_key = sys.argv[1]
    if openai_api_key is None:
        print("OpenAI API key is missing! Please add it in argument.")
        exit(1)

    # Check if the Chroma database exists
    if os.path.exists("document_database/streamlit_chroma_db"):
        try:
            choice = input("The Chroma database for Streamlit already exists. "
                        "Press Enter to delete it and create a new one. Press Ctrl+C or enter anything else to cancel.")
            if ["y", "Y", "yes", "Yes", "YES", ""] in choice:
                shutil.rmtree("document_database/streamlit_chroma_db")
            else:
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            print("Cancelled.")
            exit(0)


    print("=== Clone the latest version of the Streamlit repo...")
    if os.path.exists("streamlit"):
        shutil.rmtree("streamlit")
    os.system("git clone https://github.com/streamlit/streamlit.git --branch master --single-branch")

    version_of_streamlit = git.Repo("streamlit").head.object.hexsha

    print("=== Create documents containing the Streamlit code base and split them into chunks...")
    loader = GenericLoader.from_filesystem(
        "streamlit/",
        glob="**/*.py",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON),
        show_progress=True
    )
    streamlit_source_code_doc = loader.load()
    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=500, chunk_overlap=50
    )
    streamlit_source_code_doc = python_splitter.split_documents(streamlit_source_code_doc)

    token, max_token = num_tokens_from_string(streamlit_source_code_doc, "cl100k_base")
    print(f"Number of tokens in source code: {token}, max tokens in source code: {max_token}, price: {token * 0.0001/1000}")

    print("=== Create embeddings and save them into Chroma Database for later use...")
    embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = Chroma.from_documents(documents=streamlit_source_code_doc,embedding=embeddings_model, persist_directory=f"document_database/streamlit_chroma_db")
    vectorstore.persist()