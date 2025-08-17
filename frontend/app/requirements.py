import gradio as gr
import requests

from .config import BACKEND_URL, get_header
from .constants import ERROR, SUCCESS, WARNING, dic_icons


def add_requirement(project_id: int, text: str) -> str:
    if not project_id:
        return (
            f"{dic_icons.get(ERROR)} Please select a project before adding a requirement.",
            gr.update(value=""),
        )

    if not text.strip():
        return f"{dic_icons.get(ERROR)} Requirement text is empty.", gr.update(value="")

    headers, session = get_header()
    url = f"{BACKEND_URL}/requirements/"
    response = session.post(url, json={"text": text, "project": project_id}, headers=headers)

    if response.status_code == 201:
        return f"{dic_icons.get(SUCCESS)} Requirement saved successfully!", ""
    return f"{dic_icons.get(ERROR)} Error saving: {response.text}", text


def edit_requirement(req_id: int, project_id: int, new_text):
    headers, session = get_header()

    edit_url = f"{BACKEND_URL}/requirements/{req_id}/"
    edit_response = session.patch(
        edit_url, json={"text": new_text, "project": project_id}, headers=headers
    )

    if edit_response.status_code == 200:
        return update_requirement(project_id)
    else:
        return gr.update(choices=[])


def delete_requirement(id_requirement: str) -> str:
    try:
        id_requirement = int(id_requirement)
    except ValueError:
        return "Invalid ID."

    headers, session = get_header(content_type=None)
    url = f"{BACKEND_URL}/requirements/{id_requirement}/"
    response = session.delete(url, headers=headers)

    if response.status_code == 204:
        return f"{dic_icons.get(SUCCESS)} Requirement deleted successfully!"
    elif response.status_code == 404:
        return f"{dic_icons.get(ERROR)} Requirement not found."
    else:
        return f"{dic_icons.get(ERROR)} Error deleting: {response.status_code} - {response.text}"


def delete_and_update(id_requirement: str, project_id: int):
    message = delete_requirement(id_requirement)
    updated_choices, mapping = update_requirement(project_id)
    return message, updated_choices


def update_requirement(project_id=None):
    url = f"{BACKEND_URL}/requirements/"
    if project_id:
        url += f"?project={project_id}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        mapping = {str(r["id"]): r["text"] for r in data}

        def truncate(text, max_len=60):
            return text if len(text) <= max_len else text[:max_len].rstrip() + "..."

        options = [(truncate(r["text"]), str(r["id"])) for r in data]

        return options, mapping

    return [], {}


def validate_requirement(requirement_id: str, requirement_text: str) -> str:
    try:
        response = requests.post(
            f"{BACKEND_URL}/requirements/validate/",
            json={"requirement_id": requirement_id},
            timeout=300,
        )
        if response.status_code == 200:
            return response.json().get("validation_result", "⚠️ No results returned.")
        else:
            return f"{dic_icons.get(ERROR)} Error: {response.text}"
    except Exception as e:
        return f"{dic_icons.get(ERROR)} Validation error: {str(e)}"


def validate_all_requirements(project_name: str) -> str:
    try:
        response = requests.get(f"{BACKEND_URL}/api/projects/?name={project_name}")
        projects = response.json()
        if not projects:
            return f"{dic_icons.get(WARNING)} Project not found."

        project_id = projects[0]["id"]

        response = requests.post(
            f"{BACKEND_URL}/requirements/validate_all/",
            json={"project_id": project_id},
            timeout=60,
        )

        if response.status_code != 200:
            return f"Erro: {response.text}"

        result_list = response.json()
        output = "Validation of all requirements:\n\n"
        for item in result_list:
            output += f"Requirement: {item['text']}\n{item['validation']}\n\n"

        return output

    except Exception as e:
        return f"{dic_icons.get(ERROR)} Error validating requirements: {str(e)}"
