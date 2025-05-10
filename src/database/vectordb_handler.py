import chromadb

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from pathlib import Path
from src.utils import config_loader

PROJECT_ROOT = Path(__file__).parent.parent

config = config_loader.load_config(f"{PROJECT_ROOT}/config/config.yaml")


def get_ollama_embeddings():
    return OllamaEmbeddings(model=config["ollama"]["embedding_model"],
                            base_url=config["ollama"]["base_url"])


def load_vectordb(embeddings=get_ollama_embeddings()):
    persistent_client = (
        chromadb.PersistentClient(config["chromadb"]["chromadb_path"])
    )

    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name=config["chromadb"]["collection_name"],
        embedding_function=embeddings,
    )

    return langchain_chroma
