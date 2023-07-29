import shutil
import os
import yaml
from typing import List
from pathlib import Path


import streamlit as st
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers.language import LanguageParser
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.retrievers.ensemble import EnsembleRetriever
import chromadb
import uuid
from chromadb.config import Settings
import tiktoken


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_string_list(docs: List[Document], encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = 0
    max_tokens = 0
    for doc in docs:
        if len(encoding.encode(doc.page_content)) > max_tokens:
            max_tokens = len(encoding.encode(doc.page_content))
        num_tokens += len(encoding.encode(doc.page_content))
    return num_tokens, max_tokens


def load_streamlit_doc_retriever(
    openai_api_key: str,
    chroma_server_host="localhost",
    chroma_server_port="8000",
    mode="docker",
) -> VectorStoreRetriever:
    if openai_api_key is None:
        raise Exception("Please provide an OpenAI API key.")

    # Check if the Chroma database exists
    if mode == "local":
        if not os.path.exists(".doc_db/streamlit_chroma_db"):
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )

    # load from disk
    if mode == "local":
        retriever = Chroma(
            persist_directory=".doc_db/streamlit_chroma_db",
            embedding_function=OpenAIEmbeddings(openai_api_key=openai_api_key),
        ).as_retriever()
        retriever.search_kwargs["distance_metric"] = "cos"
        retriever.search_kwargs["fetch_k"] = 4
        retriever.search_kwargs["maximal_marginal_relevance"] = True
        retriever.search_kwargs["k"] = 4
    if mode == "docker":
        client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_host,
                chroma_server_http_port=chroma_server_port,
            )
        )

        # Get the streamlit doc collection
        streamlit_doc_retriever = Chroma(
            client=client,
            collection_name="streamlit_doc",
            embedding_function=OpenAIEmbeddings(openai_api_key=openai_api_key),
        ).as_retriever()
        streamlit_doc_retriever.search_kwargs["distance_metric"] = "cos"
        streamlit_doc_retriever.search_kwargs["fetch_k"] = 4
        streamlit_doc_retriever.search_kwargs["maximal_marginal_relevance"] = True
        streamlit_doc_retriever.search_kwargs["k"] = 4

        # Get the streamlit custom snippets collection
        streamlit_snippets_retriever = Chroma(
            client=client,
            collection_name="streamlit_snippets",
            embedding_function=OpenAIEmbeddings(openai_api_key=openai_api_key),
        ).as_retriever()
        streamlit_snippets_retriever.search_kwargs["distance_metric"] = "cos"
        streamlit_snippets_retriever.search_kwargs["fetch_k"] = 4
        streamlit_snippets_retriever.search_kwargs["maximal_marginal_relevance"] = True
        streamlit_snippets_retriever.search_kwargs["k"] = 4

        # initialize the ensemble retriever (give more weights on the snippets)
        retriever = EnsembleRetriever(
            retrievers=[streamlit_doc_retriever, streamlit_snippets_retriever],
            weights=[0.4, 0.6],
        )

    return retriever


def is_docker_container_running(container_name: str) -> bool:
    """Returns True if the Docker container is running, False otherwise."""
    if os.system(f"docker ps | grep {container_name} > /dev/null") == 0:
        return True
    print(
        f"The Docker container {container_name} is not running."
        "Please run `docker-compose up -d` to start it."
    )
    return False


def create_vector_store(
    openai_api_key: str,
    chroma_server_host="localhost",
    chroma_server_port="8000",
    mode="docker",
):
    if mode == "local":
        # Check if the Chroma database exists
        if os.path.exists(".doc_db/streamlit_chroma_db"):
            try:
                choice = input(
                    "The Chroma database for Streamlit already exists. "
                    "Press Yes to delete it and create a new one. "
                    "Press Ctrl+C or enter anything else to cancel."
                )
                if choice in ["y", "Y", "yes", "Yes", "YES"]:
                    shutil.rmtree(".doc_db/streamlit_chroma_db")
                else:
                    raise KeyboardInterrupt
            except KeyboardInterrupt:
                print("Cancelled.")
                exit(0)

    print("=== Clone the latest version of the Streamlit Doc repo...")
    if os.path.exists("docs"):
        shutil.rmtree("docs")
    os.system(
        "git clone https://github.com/streamlit/docs.git --branch main --depth 1 docs"
    )

    print(
        "=== Create documents containing the Streamlit code base and split them into chunks..."
    )

    steamlit_doc_loader = DirectoryLoader(
        "docs",
        glob="content/**/*.md",
        loader_cls=UnstructuredMarkdownLoader,
        show_progress=True,
        use_multithreading=True,
    )
    steamlit_doc = steamlit_doc_loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=2000,
        chunk_overlap=50,
    )
    steamlit_doc_splitted = text_splitter.split_documents(steamlit_doc)
    steamlit_doc_splitted

    # Load python exemple source code
    loader = GenericLoader.from_filesystem(
        "docs/",
        glob="python/api-examples-source/**/*.py",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON),
        show_progress=True,
    )
    streamlit_code_example_doc = loader.load()

    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=500, chunk_overlap=50
    )
    streamlit_code_example_doc_splitted = python_splitter.split_documents(
        streamlit_code_example_doc
    )

    token, max_token = num_tokens_from_string(steamlit_doc_splitted, "cl100k_base")
    print(
        f"Number of tokens in source code: {token}, max "
        f"tokens in source code: {max_token}, price: {token * 0.0001/1000}"
    )
    token, max_token = num_tokens_from_string(
        streamlit_code_example_doc_splitted, "cl100k_base"
    )
    print(
        f"Number of tokens in source code: {token}, max "
        f"tokens in source code: {max_token}, price: {token * 0.0001/1000}"
    )

    print("=== Create embeddings and save them into Chroma Database for later use...")
    embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

    docs = steamlit_doc_splitted + streamlit_code_example_doc_splitted
    if mode == "local":
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings_model,
            persist_directory=".doc_db/streamlit_chroma_db",
        )
        vectorstore.persist()
    if mode == "docker":
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,  # Replace with your own OpenAI API key
            model_name="text-embedding-ada-002",
        )
        client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_host,
                chroma_server_http_port=chroma_server_port,
            )
        )
        print(client.heartbeat())
        client.delete_collection("streamlit_doc")
        collection = client.create_collection(
            "streamlit_doc", embedding_function=openai_ef
        )
        for doc in docs:
            collection.add(
                ids=[str(uuid.uuid1())],
                metadatas=doc.metadata,
                documents=doc.page_content,
            )

    print("=== Remove Streamlit codesource.")
    if os.path.exists("streamlit"):
        shutil.rmtree("streamlit")


def snippets_to_vector_store(
    openai_api_key: str,
    chroma_server_host="localhost",
    chroma_server_port="8000",
    mode="docker",
):
    # First check if the vector store exists
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,  # Replace with your own OpenAI API key
        model_name="text-embedding-ada-002",
    )
    if mode == "local":
        if not os.path.exists(".doc_db/streamlit_chroma_db"):
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )
        # TODO create local client
    if mode == "docker":
        client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_host,
                chroma_server_http_port=chroma_server_port,
            )
        )
        collection = client.get_or_create_collection(
            "streamlit_snippets", embedding_function=openai_ef
        )
        if not collection:
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )

    # Then get the list of snippets
    snippets_indexes = read_snippets_index()

    my_bar = st.progress(0, text="Adding snippets to the vector store...")
    len_indexes_to_process = len(snippets_indexes["indexes"])
    for file_idx, data in enumerate(snippets_indexes["indexes"]):
        # check if the snippet file exists
        snippet_filepath = Path("streamlit_snippets/" + data["source"])
        if not snippet_filepath.exists():
            raise FileNotFoundError(
                f"The snippet file {str(snippet_filepath)} does not exist."
            )

        # Check if the snippet is not already in the vector store
        try:
            if not collection.get(where={"ids": file_idx}):
                raise Exception
        except BaseException:
            print("Snippet not found in the vector store, adding it...")

        # Load the snippet document
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=1000, chunk_overlap=50
        )
        with open(snippet_filepath, "r") as f:
            PYTHON_CODE = f.read()
        doc = python_splitter.create_documents([PYTHON_CODE])
        for doc_id, doc in enumerate(doc):
            doc.metadata = {
                "source": data["source"],
                "description": data["description"],
                "keywords": data["keywords"],
                "language": data["language"],
                "content_type": "simplyfied code",
            }

            # Add the snippet to the vector store
            # upsert items. new items will be added, existing items will be updated.
            collection.upsert(
                ids=[f"streamlit_snippet_{str(file_idx)}_{str(doc_id)}"],
                metadatas=[doc.metadata],
                documents=[doc.page_content],
            )
        my_bar.progress(
            (file_idx + 1) / len_indexes_to_process, text=str(data["source"]) + " added"
        )


def delete_vector_store(
    openai_api_key: str,
    chroma_server_host="localhost",
    chroma_server_port="8000",
    mode="docker",
):
    # First check if the vector store exists
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,  # Replace with your own OpenAI API key
        model_name="text-embedding-ada-002",
    )
    if mode == "local":
        if not os.path.exists(".doc_db/streamlit_chroma_db"):
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )
        # TODO create local client
    if mode == "docker":
        client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_host,
                chroma_server_http_port=chroma_server_port,
            )
        )
        if "collection" not in st.session_state:
            return
        collection = client.get_or_create_collection(
            st.session_state.collection, embedding_function=openai_ef
        )
        if not collection:
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )

    if "ids" in st.session_state and st.session_state["ids"]:
        collection.delete(ids=[st.session_state["ids"]])


def consult_vector_store(
    openai_api_key: str,
    chroma_server_host="localhost",
    chroma_server_port="8000",
    mode="docker",
):
    # First check if the vector store exists
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_api_key,  # Replace with your own OpenAI API key
        model_name="text-embedding-ada-002",
    )
    if mode == "local":
        if not os.path.exists(".doc_db/streamlit_chroma_db"):
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )
        # TODO create local client
    if mode == "docker":
        client = chromadb.Client(
            Settings(
                chroma_api_impl="rest",
                chroma_server_host=chroma_server_host,
                chroma_server_http_port=chroma_server_port,
            )
        )
        if "collection" not in st.session_state:
            return
        collection = client.get_or_create_collection(
            st.session_state.collection, embedding_function=openai_ef
        )
        if not collection:
            raise Exception(
                "The Chroma database for Streamlit does not exist. "
                "Please run the script `doc_retriever.py` to create it."
            )

    st.write(str(collection.count()) + " documents")
    if "query" in st.session_state and st.session_state["query"]:
        st.write(st.session_state["query"])
        results = collection.query(query_texts=[st.session_state.query], n_results=4)
    elif "ids" in st.session_state and st.session_state["ids"]:
        st.write(st.session_state["ids"])
        results = collection.get(ids=[st.session_state["ids"]])
    else:
        results = collection.get()
    st.write(results)

    collection


def read_snippets_index() -> dict:
    """Reads the snippets index yaml file and returns it as a dict."""
    with open("streamlit_snippets/index.yaml", "r") as f:
        snippets_index = yaml.load(f, Loader=yaml.FullLoader)
    return snippets_index


if __name__ == "__main__":
    st.title("AppifyAI Doc Retriever")
    openai_api_key = st.text_input("OpenAI API key")
    mode = st.selectbox("Mode", ["docker", "local"])
    choice = st.selectbox(
        "Action", ["create", "add snippets", "consult vector store", "delete data"]
    )

    if choice == "create":
        pass
    elif choice == "add snippets":
        pass
    elif choice == "consult vector store":
        collection = st.selectbox(
            "Select collection",
            ["streamlit_doc", "streamlit_snippets"],
            key="collection",
        )
        ids = st.text_input("Ids", key="ids")
        query = st.text_input("Query", key="query")
    elif choice == "delete data":
        collection = st.selectbox(
            "Select collection",
            ["streamlit_doc", "streamlit_snippets"],
            key="collection",
        )
        ids = st.text_input("Ids", key="ids")

    button = st.button("Run")

    if button:
        if choice == "create":
            create_vector_store(
                openai_api_key=openai_api_key,
                mode=mode,
                chroma_server_host=st.secrets["chroma"]["host"],
                chroma_server_port=st.secrets["chroma"]["port"],
            )
        elif choice == "add snippets":
            snippets_to_vector_store(
                openai_api_key=openai_api_key,
                mode=mode,
                chroma_server_host=st.secrets["chroma"]["host"],
                chroma_server_port=st.secrets["chroma"]["port"],
            )
        elif choice == "consult vector store":
            consult_vector_store(
                openai_api_key=openai_api_key,
                mode=mode,
                chroma_server_host=st.secrets["chroma"]["host"],
                chroma_server_port=st.secrets["chroma"]["port"],
            )
        elif choice == "delete data":
            delete_vector_store(
                openai_api_key=openai_api_key,
                mode=mode,
                chroma_server_host=st.secrets["chroma"]["host"],
                chroma_server_port=st.secrets["chroma"]["port"],
            )
