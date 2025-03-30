""" This file contains database helpers """

# Standard libraries
from os import makedirs

# External libraries
import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from src.models.base import Base
import src.models.web  # noqa: F401

# Create databases directory
makedirs("./databases", exist_ok=True)

# Instantiate ChromaDB client
chroma_client = chromadb.HttpClient(host="chromadb", port=8000)

# Create general website database engine
web_db_string = "sqlite:///databases/web.db"
web_db = create_engine(web_db_string)

# Create chat sessions database engine
sessions_db_string = "sqlite:///databases/sessions.db"

# Web database 'sessionmaker'
WebSession = sessionmaker(autocommit=False, autoflush=False, bind=web_db)

# Create tables
Base.metadata.create_all(bind=web_db)
