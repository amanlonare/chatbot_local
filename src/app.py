import sqlite3
import streamlit as st

from pathlib import Path
from src.database.db_operations import (
    get_all_chat_history_ids, delete_chat_history,
    save_text_message, load_last_k_text_messages_ollama, load_messages,
    init_db)
from src.llm.chat_api_handler import ChatAPIHandler
from src.templates.html_templates import css
from src.utils import config_loader
from src.utils.utils import (list_ollama_models, get_timestamp, command,
                             get_avatar)

PROJECT_ROOT = Path(__file__).parent.parent

config = config_loader.load_config(f"{PROJECT_ROOT}/src/config/config.yaml")


def get_session_key():
    if st.session_state.session_key == "new_session":
        st.session_state.new_session_key = get_timestamp()
        return st.session_state.new_session_key
    return st.session_state.session_key


def delete_chat_session_history():
    delete_chat_history(st.session_state.session_key)
    st.session_state.session_index_tracker = "new_session"


def update_model_options():
    st.session_state.model_options = list_model_options()


def clear_cache():
    st.cache_resource.clear()


def list_model_options():
    """
    List all available model options from the configuration file.

    Returns:
        list: A list of model options.
    """
    if st.session_state.endpoint_to_use == "ollama":
        ollama_options = list_ollama_models()
        if ollama_options == []:
            st.warning("""
                No ollama models available, please choose one from
                https://ollama.com/library and pull with /pull <model_name>
            """)
        return ollama_options


def main():
    st.title("Multimodal Local Chat App")
    st.write(css, unsafe_allow_html=True)

    # Initialize session state variables (without DB connection)
    if "session_key" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
        st.session_state.endpoint_to_use = "ollama"
        st.session_state.model_options = list_model_options()
        st.session_state.model_tracker = None

    # Handle new session creation
    if (st.session_state.session_key == "new_session" and
            st.session_state.new_session_key is not None):
        st.session_state.session_index_tracker = (
            st.session_state.new_session_key
        )
        st.session_state.new_session_key = None

    # if "db_conn" not in st.session_state:
    #     st.session_state.session_key = "new_session"
    #     st.session_state.new_session_key = None
    #     st.session_state.session_index_tracker = "new_session"
    #     st.session_state.db_conn = sqlite3.connect(
    #         config["database"]["chat_history_path"])
    #     st.session_state.endpoint_to_use = "ollama"
    #     st.session_state.model_options = list_model_options()
    #     st.session_state.model_tracker = None

    # if (st.session_state.session_key == "new_session" and
    #         st.session_state.new_session_key is not None):
    #     st.session_state.session_index_tracker = (
    #         st.session_state.new_session_key
    #         )
    #     st.session_state.new_session_key = None

    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + get_all_chat_history_ids()
    try:
        index = chat_sessions.index(st.session_state.session_index_tracker)
    except ValueError:
        st.session_state.session_index_tracker = "new_session"
        index = chat_sessions.index(st.session_state.session_index_tracker)
        clear_cache()

    st.sidebar.selectbox("Select a chat session", chat_sessions,
                         key="session_key", index=index)

    api_col, model_col = st.sidebar.columns(2)

    api_col.selectbox(label="Select an API",
                      options=["ollama"], key="endpoint_to_use",
                      on_change=update_model_options)
    model_col.selectbox(label="Select a Model",
                        options=st.session_state.model_options,
                        key="model_to_use")

    delete_chat_col, clear_cache_col = st.sidebar.columns(2)
    delete_chat_col.button("Delete Chat Session",
                           on_click=delete_chat_session_history)

    chat_container = st.container()
    user_input = st.chat_input("Type your message here", key="user_input")

    if user_input:
        if user_input.startswith("/"):
            response = command(user_input)
            save_text_message(get_session_key(), "user", user_input)
            save_text_message(get_session_key(), "assistant", response)
            user_input = None

        if user_input:
            llm_answer = ChatAPIHandler.chat(
                user_input=user_input,
                chat_history=load_last_k_text_messages_ollama(
                    get_session_key(),
                    config["chat_config"]["chat_memory_length"]))
            save_text_message(get_session_key(), "user", user_input)
            save_text_message(get_session_key(), "assistant", llm_answer)
            user_input = None

    if ((st.session_state.session_key != "new_session") !=
            (st.session_state.new_session_key is not None)):
        with chat_container:
            chat_history_messages = load_messages(get_session_key())

            for message in chat_history_messages:
                with st.chat_message(
                        name=message["sender_type"],
                        avatar=get_avatar(message["sender_type"])):
                    if message["message_type"] == "text":
                        st.write(message["content"])
                    if message["message_type"] == "image":
                        st.image(message["content"])
                    if message["message_type"] == "audio":
                        st.audio(message["content"], format="audio/wav")

        if ((st.session_state.session_key == "new_session") and
                (st.session_state.new_session_key is not None)):
            st.rerun()


if __name__ == "__main__":
    init_db()
    main()
