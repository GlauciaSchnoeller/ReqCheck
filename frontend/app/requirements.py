import gradio as gr
import requests

from .config import BACKEND_URL, get_header


def add_requirement(project_id: int, text: str) -> str:
    if not project_id:
        return "❌ Please select a project before adding a requirement.", gr.update(value="")

    if not text.strip():
        return "❌ Requirement text is empty.", gr.update(value="")

    headers, session = get_header()
    url = f"{BACKEND_URL}/requirements/"
    response = session.post(url, json={"text": text, "project": project_id}, headers=headers)

    if response.status_code == 201:
        return "✅ Requirement saved successfully!", ""
    return f"❌ Error saving: {response.text}", text


def edit_requirement(project_id: int, old_text: str, new_text: str):

    headers, session = get_header()
    url = f"{BACKEND_URL}/requirements/?project={project_id}"
    response = session.get(url, headers=headers)

    if response.status_code != 200:
        return gr.update(choices=[])

    requirements = response.json()
    req_to_edit = next((r for r in requirements if r["text"] == old_text), None)

    if not req_to_edit:
        return gr.update(choices=[])

    req_id = req_to_edit["id"]
    edit_url = f"{BACKEND_URL}/requirements/{req_id}/"
    edit_response = session.patch(edit_url, json={"text": new_text}, headers=headers)

    if edit_response.status_code == 200:
        return update_requirement(project_id)
    else:
        return gr.update(choices=[])


def delete_requirement(id_requirement: str) -> str:
    try:
        id_requirement = int(id_requirement)
    except ValueError:
        return "ID inválido."

    headers, session = get_header(content_type=None)
    url = f"{BACKEND_URL}/requirements/{id_requirement}/"
    response = session.delete(url, headers=headers)

    if response.status_code == 204:
        return "✅ Requirement deleted successfully!"
    elif response.status_code == 404:
        return "❌ Requirement not found."
    else:
        return f"❌ Error deleting: {response.status_code} - {response.text}"


def delete_and_update(id_requirement: str):
    message = delete_requirement(id_requirement)
    new_options = update_requirement()
    return message, new_options


def update_requirement(project_id=None):

    url = f"{BACKEND_URL}/requirements/"
    if project_id:
        url += f"?project={project_id}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        options = [(r["text"], str(r["id"])) for r in data]
        return gr.update(choices=options)
    return gr.update(choices=[])
