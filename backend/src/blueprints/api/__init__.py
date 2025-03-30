""" API blueprint """

# Standard libraries
from urllib.parse import urldefrag

# External libraries
from flask import Blueprint, request
import sqlalchemy as sql

# Local imports
from src.models import WebSession
from src.models.llm import get_conversational_rag_chain, get_session_history
from src.models.web import Users, Sessions
from src.utils import get_or_create_retriever, get_url_hash

# Create blueprint
api_bp = Blueprint(name="api_bp", import_name=__name__, url_prefix="/api")

# Cached conversational chains
chain_store = {}

# Invalid request error template
INVALID_REQUEST_BODY = ({"detail": "Invalid request body."}, 400)


# Index URL route
@api_bp.route("/index-url", methods=["POST"])
def index_url():
    """
    Indexes an URL, creating a new retriever.
    """
    # Get request body
    body = request.get_json(silent=True)

    # Check for valid request body
    if body is None:
        return

    # Check for valid URL
    url = body.get("url")
    if url is None:
        return INVALID_REQUEST_BODY
    url = urldefrag(url).url

    # Create URL hash
    url_hash = get_url_hash(url)

    # Check if URL is in local chain store
    if chain_store.get(url_hash) is not None:
        return {"detail": "URL was successfully indexed."}, 200

    # Get or create retriever
    retriever = get_or_create_retriever(url, url_hash)

    # Handle retriever creation error
    if retriever is None:
        return {"detail": "URL could not be indexed."}, 500

    return {"detail": "URL was successfully indexed."}, 200


# Ask URL route
@api_bp.route("/ask", methods=["POST"])
def ask():
    """
    Ask a question for an URL, creating a new chat session.
    """
    # Get request body
    body = request.get_json(silent=True)

    # Check for valid request body
    if body is None:
        return INVALID_REQUEST_BODY

    # Check for valid URL
    url = body.get("url")
    if url is None:
        return INVALID_REQUEST_BODY
    url = urldefrag(url).url

    # Check for valid chat message
    message = body.get("message")
    if message is None:
        return INVALID_REQUEST_BODY

    # Create URL hash
    url_hash = get_url_hash(url)

    # Check for valid session ID
    session_id = body.get("session_id")
    if session_id is None:
        session_id = url_hash
    else:
        session_id = str(session_id)

    # Get conversational RAG chain
    conversational_rag_chain = chain_store.get(url_hash)
    if conversational_rag_chain is None:
        conversational_rag_chain = get_conversational_rag_chain(url, url_hash)
        if conversational_rag_chain is None:
            return {"detail": "URL could not be indexed."}, 500
        chain_store[url_hash] = conversational_rag_chain

    # Ask question to LLM
    answer = conversational_rag_chain.invoke(
        {"input": message}, config={"configurable": {"session_id": session_id}}
    ).get("answer")

    return {"answer": answer}, 200


# Login route
@api_bp.route("/login", methods=["POST"])
def login():
    """
    Handles the user login.
    """
    # Get request body
    body = request.get_json(silent=True)

    # Check for valid request body
    if body is None:
        return INVALID_REQUEST_BODY

    # Check for valid URL
    username = body.get("username")
    if username is None:
        return INVALID_REQUEST_BODY

    # Add user if it doesn't exist
    with WebSession() as session:
        try:
            # Search for the user
            user = session.execute(
                sql.select(Users.id).where(Users.username == username)
            ).first()

            # Add if doesn't exist
            if user is None:
                user = Users(username=username)
                session.add(user)
                session.commit()
                session.flush()

            uid = user.id
        except Exception:
            session.rollback()
            return {"detail": "Login error."}, 500

    return {"detail": "User logged in successfully.", "user_id": str(uid)}, 200


# Create session route
@api_bp.route("/session", methods=["POST"])
def create_session():
    """
    Create a new chat session.
    """
    # Get request body
    body = request.get_json(silent=True)

    # Check for valid request body
    if body is None:
        return INVALID_REQUEST_BODY

    # Check for valid URL
    url = body.get("url")
    if url is None:
        return INVALID_REQUEST_BODY
    url = urldefrag(url).url

    # Check for valid label
    label = body.get("label")
    if label is None:
        return INVALID_REQUEST_BODY

    # Check for valid user data
    user_id = body.get("user_id")
    if user_id is None:
        return INVALID_REQUEST_BODY
    user_id = str(user_id)

    # Create URL hash
    url_hash = get_url_hash(url)

    # Add session if it doesn't exist
    with WebSession() as session:
        try:
            # Create chat session
            chat_session = Sessions(
                label=label, url=url, url_hash=url_hash, fk_users_id=user_id
            )
            session.add(chat_session)
            session.flush()

            # Get session primary key
            chat_session_pk = chat_session.id

            # Build session id
            session_id = f"{url_hash}--{user_id}--{chat_session_pk}"

            # Update session_id
            session.execute(
                sql.update(Sessions)
                .where(Sessions.id == chat_session_pk)
                .values(session_id=session_id)
            )

            session.commit()
        except Exception:
            session.rollback()
            return {"detail": "Session creation error."}, 500

    return {"detail": "Session created successfully.", "session_id": session_id}, 200


@api_bp.route("/session", methods=["GET"])
def get_sessions():
    """
    Get user sessions.
    """
    # Get request query parameters
    params = request.args

    # Check for user_id parameter
    user_id = params.get("user_id")
    if user_id is None:
        return INVALID_REQUEST_BODY

    # Get user sessions
    with WebSession() as session:
        try:
            query = sql.select(
                Sessions.label, Sessions.url, Sessions.url_hash, Sessions.session_id
            ).where(Sessions.fk_users_id == user_id)
            cols = ["label", "url", "url_hash", "session_id"]
            data = [dict(zip(cols, row)) for row in session.execute(query).all()]
        except Exception:
            return {"detail": "Session query error."}, 500

    return {"detail": "Sessions queried successfully.", "sessions": data}, 200


@api_bp.route("/messages", methods=["GET"])
def get_messages():
    """
    Get messages from a chat session.
    """
    # Get request query parameters
    params = request.args

    # Check for session_id parameter
    session_id = params.get("session_id")
    if session_id is None:
        return INVALID_REQUEST_BODY

    # Get session history messages
    messages = get_session_history(session_id, as_dict=True)

    return {"detail": "Messages queried successfully.", "messages": messages}, 200
