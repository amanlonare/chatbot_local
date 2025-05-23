import requests
import streamlit as st

from pathlib import Path
from src.database.vectordb_handler import load_vectordb
from src.utils import config_loader
from src.utils.utils import convert_ns_to_seconds, convert_bytes_to_base64

PROJECT_ROOT = Path(__file__).parent.parent

config = config_loader.load_config(f"{PROJECT_ROOT}/config/config.yaml")


class OllamaChatAPIHandler:

    def __init__(self):
        pass

    @classmethod
    def api_call(cls, chat_history):
        data = {
            "model": st.session_state["model_to_use"],
            "messages": chat_history,
            "stream": False
        }
        response = requests.post(
            url=config["ollama"]["base_url"] + "/api/chat",
            json=data)
        print(response.json())
        json_response = response.json()
        if "error" in json_response.keys():
            return "OLLAMA ERROR: " + json_response["error"]
        cls.print_times(json_response)
        return json_response["message"]["content"]

    @classmethod
    def image_chat(cls, user_input, chat_history, image):
        chat_history.append(
            {"role": "user", "content": user_input,
             "images": [convert_bytes_to_base64(image)]})
        return cls.api_call(chat_history)

    @classmethod
    def print_times(cls, json_response):        
        total_duration_ns = json_response.get("total_duration", 0)
        load_duration_ns = json_response.get("load_duration", 0)
        prompt_eval_duration_ns = json_response.get("prompt_eval_duration", 0)
        eval_duration_ns = json_response.get("eval_duration", 0)

        total_duration_seconds = convert_ns_to_seconds(total_duration_ns)
        load_duration_seconds = convert_ns_to_seconds(load_duration_ns)
        prompt_eval_duration_seconds = convert_ns_to_seconds(
            prompt_eval_duration_ns)
        eval_duration_seconds = convert_ns_to_seconds(eval_duration_ns)

        print(f"Total duration: {total_duration_seconds:.4f} seconds")
        print(f"Load duration: {load_duration_seconds:.4f} seconds")
        print(f"Prompt eval duration: {prompt_eval_duration_seconds:.4f} \
              seconds")
        print(f"Eval duration: {eval_duration_seconds:.4f} seconds")


class ChatAPIHandler:

    def __init__(self):
        pass

    @classmethod
    def chat(cls, user_input, chat_history, image=None):
        endpoint = st.session_state["endpoint_to_use"]
        print(f"Endpoint to use: {endpoint}")
        print(f"Model to use: {st.session_state['model_to_use']}")
        if endpoint == "ollama":
            handler = OllamaChatAPIHandler
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        if st.session_state.get("pdf_chat", False):
            vector_db = load_vectordb()
            retrieved_documents = vector_db.similarity_search(
                user_input,
                k=config["chat_config"]["number_of_retrieved_documents"]
                )
            context = "\n".join(
                [item.page_content for item in retrieved_documents]
                )
            template = f"Answer the user question based on this context: \
                {context}\nUser Question: {user_input}"
            chat_history.append({"role": "user", "content": template})
            return handler.api_call(chat_history)

        if image:
            return handler.image_chat(user_input, chat_history, image)

        chat_history.append({"role": "user", "content": user_input})
        return handler.api_call(chat_history)
