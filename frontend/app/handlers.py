import gradio as gr
import requests

from .config import BACKEND_URL, get_header


def add_requirement(text: str) -> str:
    if not text.strip():
        return "Empty text. Fill in the field."

    headers, session = get_header()
    url = f"{BACKEND_URL}/requirements/"
    response = session.post(url, json={"text": text}, headers=headers)

    if response.status_code == 201:
        return "Requirement saved successfully!", ""
    return f"Error saving: {response.text}", text


def ask_question(question):
    url = f"{BACKEND_URL}/requirement/ask/"
    try:
        response = requests.post(url, json={"question": question})
        if response.status_code == 200:
            return response.json().get("response", "No response.")
        return f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"


def delete_requirement(id_requirement: str) -> str:
    try:
        id_requirement = int(id_requirement)
    except ValueError:
        return "ID inválido."

    headers, session = get_header(content_type=None)
    url = f"{BACKEND_URL}/requirements/{id_requirement}/"
    response = session.delete(url, headers=headers)

    if response.status_code == 204:
        return "Requirement deleted successfully!"
    elif response.status_code == 404:
        return "Requirement not found."
    else:
        return f"Error deleting: {response.status_code} - {response.text}"


def delete_and_update(id_requirement: str):
    message = delete_requirement(id_requirement)
    new_options = update_requirement()
    return message, new_options


def update_requirement():
    url = f"{BACKEND_URL}/requirements/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        options = [(f"{r['id']}: {r['text'][:50]}", str(r["id"])) for r in data]
        return gr.update(choices=options)
    return gr.update(choices=[])


def upload_pdf(pdf_file):
    if pdf_file is None:
        return "No file uploaded."

    try:
        with open(pdf_file.name, "rb") as f:
            files = {"pdf": f}
            url = f"{BACKEND_URL}/business-visions/"
            response = requests.post(url, files=files)
        if response.status_code == 201:
            return "Upload successful."
        else:
            return f"Error: {response.text}"
    except Exception as e:
        return f"Upload failed: {str(e)}"
