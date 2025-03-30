""" This file contains logic related to LLM communication """

# Standard libraries
from os import getenv

# External libraries
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# Local imports
from src.models import sessions_db_string
from src.utils import get_or_create_retriever

# Instantiate OpenAI chat model integration
llm = ChatOpenAI(model=getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)


def get_session_history(
    session_id: str, as_dict: bool = False
) -> SQLChatMessageHistory | list:
    """Get the session history from SQL database.

    Args:
        session_id (str): The session id for the session history.
        as_dict (bool, optional): Whether to return session history as a list of dictionaries. Defaults to False.

    Returns:
        SQLChatMessageHistory | list: The mensage history.
    """
    history = SQLChatMessageHistory(
        session_id=session_id, connection=sessions_db_string
    )
    if as_dict:
        history = [
            {"message": message.content, "kind": message.type}
            for message in history.get_messages()
        ]
    return history


def get_conversational_rag_chain(
    url: str, url_hash: str
) -> RunnableWithMessageHistory | None:
    """Get conversational RAG chain with historical context.

    Args:
        url (str): Website to be scraped for context.
        url_hash (str): Hash that identifies the ChromaDB collection.

    Returns:
        RunnableWithMessageHistory | None: The conversational RAG chain instance.
    """

    # Get retriever
    retriever = get_or_create_retriever(url, url_hash)

    # Handle bad retriever
    if retriever is None:
        return None

    # Create historical conversation context
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # Create conversation context
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Create retrieval chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Instatiate chat history RAG chain
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain
