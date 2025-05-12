from setuptools import setup, find_packages

setup(
    name="chatbot_local",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "langchain",
        "chromadb",
        "langchain-community",
        "langchain-ollama",
        "torch",
        "torchvision",
        "torchaudio",
        "transformers",
        "streamlit-mic-recorder"
    ],
)