import requests

from .config import BACKEND_URL, get_header
from .constants import ERROR, SUCCESS, dic_icons


def add_requirement(project_id: int, text: str):
    if not project_id:
        return f"{dic_icons.get(ERROR)} Please select a project.", ""
    if not text.strip():
        return f"{dic_icons.get(ERROR)} Requirement text is empty.", ""

    headers, session = get_header()
    url = f"{BACKEND_URL}/requirements/"
    resp = session.post(url, json={"text": text, "project": project_id}, headers=headers)

    if resp.status_code == 201:
        return f"{dic_icons.get(SUCCESS)} Requirement saved!", ""
    return f"{dic_icons.get(ERROR)} Error: {resp.text}", text


def edit_requirement(req_id: int, project_id: int, new_text: str):
    headers, session = get_header()
    url = f"{BACKEND_URL}/requirements/{req_id}/"
    resp = session.patch(url, json={"text": new_text, "project": project_id}, headers=headers)
    if resp.status_code == 200:
        return update_requirement(project_id)
    return [], {}


def delete_requirement(req_id: str):
    try:
        req_id = int(req_id)
    except ValueError:
        return f"{dic_icons.get(ERROR)} Invalid ID."
    headers, session = get_header(content_type=None)
    url = f"{BACKEND_URL}/requirements/{req_id}/"
    resp = session.delete(url, headers=headers)
    if resp.status_code == 204:
        return f"{dic_icons.get(SUCCESS)} Requirement deleted!"
    elif resp.status_code == 404:
        return f"{dic_icons.get(ERROR)} Not found."
    return f"{dic_icons.get(ERROR)} Error: {resp.text}"


def delete_and_update(req_id: str, project_id: int):
    message = delete_requirement(req_id)
    updated_choices, mapping = update_requirement(project_id)
    return message, updated_choices


def update_requirement(project_id=None):
    url = f"{BACKEND_URL}/requirements/"
    if project_id:
        url += f"?project={project_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return [], {}
    data = resp.json()
    mapping = {str(r["id"]): r["text"] for r in data}

    def truncate(text, max_len=60):
        return text if len(text) <= max_len else text[:max_len].rstrip() + "..."

    options = [(truncate(r["text"]), str(r["id"])) for r in data]
    return options, mapping


def validate_requirement(requirement_id: str, project_id: int = None):
    try:
        _, session = get_header()
        url = f"{BACKEND_URL}/requirements/validate/"
        payload = {"requirement_id": requirement_id, "project_id": project_id}
        resp = session.post(url, json=payload, timeout=300)

        if resp.status_code != 200:
            return {"status": "Error validating requirement", "error": resp.text}

        data = resp.json()
        validation = data.get("validation_result", {})

        output = "📝 Validation of the individual requirement:\n\n"
        output += (
            f"Requirement: {data.get('text', '')}\n\n"
            f"Consistency: {validation.get('consistency')}\n"
            f"Completeness: {validation.get('completeness')}\n"
            f"Ambiguity: {validation.get('ambiguity')}\n"
            f"Notes: {validation.get('notes')}\n\n"
        )
        return output

    except Exception as ex:
        return {"status": "Error validating requirement", "error": str(ex)}


def validate_all_requirements(project_id: int):
    try:
        _, session = get_header()
        url = f"{BACKEND_URL}/requirements/validate_all/"
        payload = {"project_id": project_id}
        resp = session.post(url, json=payload, timeout=300)
        if resp.status_code != 200:
            return f"{dic_icons.get(ERROR)} Error: {resp.text}"
        result_list = resp.json()

        output = "📝 Validation of all requirements:\n\n"
        for item in result_list:
            validation = item.get("validation_result", {})
            output += (
                f"Requirement: {item['text']}\n\n"
                f"Consistency: {validation.get('consistency')}\n"
                f"Completeness: {validation.get('completeness')}\n"
                f"Ambiguity: {validation.get('ambiguity')}\n"
                f"Notes: {validation.get('notes')}\n\n"
            )
        return output
    except Exception as e:
        return f"{dic_icons.get(ERROR)} Batch validation error: {str(e)}"
