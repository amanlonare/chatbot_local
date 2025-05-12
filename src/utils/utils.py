import aiohttp
import asyncio
import base64
import requests
import streamlit as st
import time

from datetime import datetime
from pathlib import Path
from src.utils import config_loader

PROJECT_ROOT = Path(__file__).parent.parent.parent

config = config_loader.load_config(f"{PROJECT_ROOT}/src/config/config.yaml")


def convert_ns_to_seconds(ns_value):
    return ns_value / 1_000_000_000 


def convert_bytes_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in \
              {execution_time:.4f} seconds")
        return result
    return wrapper


def list_ollama_models():
    """
    List all available models from the Ollama API.
    Returns:
        list: A list of model names.
    """
    json_response = requests.get(
        url=config["ollama"]["base_url"] + "/api/tags", timeout=10).json()
    if json_response.get("error", False):
        return []
    models = [model["name"] for model in json_response["models"]
              if "embed" not in model["name"]]
    return models


def command(user_input):
    splitted_input = user_input.split(" ")
    if splitted_input[0] == "/pull":
        return pull_model_in_background(splitted_input[1])
    elif splitted_input[0] == "/help":
        return "Possible commands:\n- /pull <model_name>"
    else:
        return """Invalid command, please use one of the following:\n
                    - /help\n
                    - /pull <model_name>"""


# Function to trigger the async pull (can be run in the event loop)
def pull_model_in_background(model_name, stream=False):
    try:
        # Check if there's already an event loop running
        loop = asyncio.get_running_loop()
    except RuntimeError:  # If no loop is running, start a new one
        loop = None

    if loop and loop.is_running():
        # If an event loop is already running, create a task 
        # for the async function
        return asyncio.create_task(
            pull_ollama_model_async(model_name, stream=stream))
    else:
        # Otherwise, use asyncio.run() to run it synchronously
        return asyncio.run(
            pull_ollama_model_async(model_name, stream=stream))


async def pull_ollama_model_async(model_name, stream=True, retries=1):
    url = config["ollama"]["base_url"] + "/api/pull"
    json_data = {"model": model_name, "stream": stream}

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=1800)) as session:
                async with session.post(url, json=json_data) as response:
                    if stream:
                        # Handle streaming response
                        async for chunk in response.content.iter_chunked(1024):
                            if chunk:
                                st.info(
                                    f"Received chunk: {chunk.decode('utf-8')}")
                    else:
                        json_response = await response.json()
                        print(json_response)

                        if json_response.get("error", False):
                            return json_response["error"]
                        else:
                            st.session_state.model_options = (
                                list_ollama_models())
                            return f"Pull of {model_name} finished."
                    return "Pulled"
        except asyncio.TimeoutError:
            st.warning(f"Timeout on attempt {attempt + 1}. Retrying...")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            break  # Break on non-timeout errors
    return f"Failed to pull {model_name} after {retries} attempts."


def get_avatar(sender_type):
    if sender_type == "user":
        return "src/utils/chat_icons/user_image.png"
    else:
        return "src/utils/chat_icons/bot_image.png"
