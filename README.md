# Talk to your website

## Overview

The project in this repository consists of a fullstack LLM chat system with retrieval-augmented generation (RAG) features. After giving a arbitrary username in the login page, you will be redirected to a simple chat interface, where you can create a new conversation with a LLM model for the context of a website of your choice. The LLM model will answer you questions based on the content provided by the website.

After the indexing of the website, you will be able to ask questions and to keep a conversation that evolves based on your interaction and follow-up questions. You can create multiple conversations about the same website, without mixing the conversation context. You can also make the login with different usernames to be presented to single-user session chats.

## Implementation

### Tech stack

- LLM provider: OpenAI

  - Default model: gpt-4o-mini

  - Vector database: ChromaDB 0.5.23

- Backend: Python 3.12.5

  - Web server: Flask 3.0.3

  - RAG: Langchain 0.2.13

- Frontend: Node 20.16.0

  - Framework: Nuxt.js 3.12.4

  - UI components: Vuetify 3.6.14

### Langchain

The communication with the LLM model, as well as the history, chat and RAG features, were implemented using the Langchain library for Python. In summary, we index the website contents in ChromaDB and then use a retrieval interface to get the documents context. Chat sessions and history are stored in an SQLite file.

To have unique ChromaDB collections for each website, I used SHA256 hashes of their URLs (referred as `url_hash`s) as indexes. Also, for identifying unique chat sessions, I used a combination of the `url_hash`, `user_id` and the session's database primary key to create `session_id`s for indexes.

### Backend / API

This implementation provides two major endpoints, `index_url` and `ask`.

- The `POST /api/index_url` endpoint expects an URL in the request body key `url`. This URL will be indexed by the model and stored in ChromaDB.

- The `POST /api/ask` endpoint expects an URL in the request body key `url`. It also expects a `message` and a `session_id`.

- Other then these, the `GET /api/sessions`, `POST /api/sessions`, `GET /api/login` and `GET /api/messages` endpoints were implemented because of the project needs.

### Docker

The project was divided into three containers: `backend`, `frontend` and `chromadb`. By setting the `.env` file with your environment variables, as present in the `example.env` file, and running the `docker compose up` command, you are able to run it.

## References

- Langchain Docs
  [[1]](https://api.python.langchain.com/en/latest/)
  [[2]](https://python.langchain.com/v0.2/docs/tutorials/qa_chat_history/)
  [[3]](https://python.langchain.com/v0.2/docs/how_to/message_history/)
  [[4]](https://python.langchain.com/v0.2/docs/integrations/memory/sql_chat_message_history/)
  [[5]](https://python.langchain.com/v0.2/docs/how_to/vectorstores/)
  [[6]](https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores/)
  [[7]](https://python.langchain.com/v0.2/docs/tutorials/retrievers/)
  [[8]](https://python.langchain.com/v0.1/docs/use_cases/question_answering/)
  [[9]](https://github.com/langchain-ai/langchain/discussions/16582/)
