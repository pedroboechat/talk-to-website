""" This file contains utility funcions """

# Standard libraries
from hashlib import sha256
from urllib.parse import urldefrag

# External libraries
from chromadb.api.configuration import InvalidConfigurationError
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests

# Local imports
from src.models import chroma_client


def get_url_hash(url: str) -> str:
    """Get website hash from its URL.

    Args:
        url (str): The website URL.

    Returns:
        str: Hashed URL.
    """
    clean_url = urldefrag(url).url
    return sha256(clean_url.encode()).hexdigest()[:-1]


def get_or_create_retriever(url: str, url_hash: str) -> VectorStoreRetriever | None:
    """Tries to get a retriever and fallbacks to create it.

    Args:
        url (str): Website to be scraped for context.
        url_hash (str): Hash that identifies the ChromaDB collection.

    Returns:
        VectorStoreRetriever | None: ChromaDB retriever for the website.
    """

    try:
        # Tries to get URL in ChromaDB
        retriever = Chroma(
            collection_name=url_hash,
            embedding_function=OpenAIEmbeddings(),
            create_collection_if_not_exists=False,
        ).as_retriever()
    except ValueError:
        try:
            # Scrape website source code
            loader = WebBaseLoader(web_paths=(url,), raise_for_status=True)

            # Create document splits
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)

            # Create ChromaDB collection
            vectorstore = Chroma.from_documents(
                client=chroma_client,
                collection_name=url_hash,
                documents=splits,
                embedding=OpenAIEmbeddings(),
            )

            # Create retriever
            retriever = vectorstore.as_retriever()
        except (requests.exceptions.HTTPError, InvalidConfigurationError):
            return None

    return retriever
