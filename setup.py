from setuptools import setup, find_packages

setup(
    name="chatbot_local",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "langchain",
        "chromadb",
        "langchain-community",
        "langchain-ollama",
    ],
)