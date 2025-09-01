import requests

from .config import BACKEND_URL


def ask_question(question):
    url = f"{BACKEND_URL}/requirement/ask/"
    try:
        response = requests.post(url, json={"question": question})
        if response.status_code == 200:
            return response.json().get("response", "No response.")
        return f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"


def ask_question_chat(history, user_input):
    if user_input.strip() == "":
        return history, ""

    resposta = ask_question(user_input)

    history.append((user_input, resposta))
    return history, ""
