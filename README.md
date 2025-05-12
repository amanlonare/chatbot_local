# Multi-Modal Local Chatbot

## Features

A local chatbot application built with Streamlit and Ollama that supports text conversations, PDF context understanding, and image analysis capabilities. This chatbot runs completely locally, ensuring data privacy and security.

## Features

- 🔒 **Local Operation**: Runs completely offline for data security
- 💬 **Q&A Support**: Interactive chat interface with memory
- 📄 **PDF Context**: Can understand and answer questions from PDF documents
- 🖼️ **Image Analysis**: Capability to understand and discuss images
- 🎯 **Model Selection**: Support for various Ollama models
- 🔄 **Session Management**: Save and manage multiple chat sessions
- 🎨 **Modern UI**: Clean interface built with Streamlit

## Prerequisites

- Python 3.11 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- Make (for using Makefile commands)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chatbot_local.git
cd chatbot_local
```

2. Install dependencies using Make:
```bash
make install
```

This will:
- Create a virtual environment
- Install required packages
- Set up the project in development mode

## Running the Application

1. First, ensure Ollama is running:
```bash
ollama serve
```

2. Pull a model (e.g., Gemma):
```bash
ollama pull gemma:2b
```

for images, pull the model (or any vision model)
```bash
ollama run llava
```

for embedding, pull the model (or any other as per your preference)
config.yaml has defined nomic-embed-text as embedding model
```bash
ollama pull nomic-embed-text
```

3. Start the Streamlit application:
```bash
streamlit run src/app.py
```

## Project Structure

```
chatbot_local/
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── database/           # Database operations
│   ├── llm/               # LLM integration
│   ├── utils/             # Utility functions
│   └── config/            # Configuration files
├── chat_sessions/         # SQLite database storage
└── chroma_db/            # Vector database storage
```

## Usage

1. Select or create a new chat session
2. Choose an LLM model from available Ollama models
3. Start chatting!

### Available Commands
- `/help` - Show available commands
- `/pull <model_name>` - Pull a new model from Ollama

## Configuration

Edit `src/config/config.yaml` to customize:
- Database paths
- Ollama settings
- Chat memory length
- Vector database settings

## Development

Clean build files:
```bash
make clean
```

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [Ollama](https://ollama.ai/) for LLM support
- Uses [LangChain](https://python.langchain.com/) for LLM interactions
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage