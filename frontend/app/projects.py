import gradio as gr

from .config import BACKEND_URL, get_header


def load_projects(selected_id=None):
    headers, session = get_header()
    response = session.get(f"{BACKEND_URL}/projects/", headers=headers)

    if response.status_code == 200:
        projects = response.json()
        choices = [(proj["name"], proj["id"]) for proj in projects]

        if not selected_id and projects:
            selected_id = projects[0]["id"]

        return gr.update(choices=choices, value=selected_id)
    else:
        return gr.update(choices=[], value=None)


def save_project(name, description):
    headers, session = get_header()
    response = session.post(
        f"{BACKEND_URL}/projects/", json={"name": name, "description": description}, headers=headers
    )

    if response.status_code == 201:
        new_project_id = response.json()["id"]
        updated_dropdown = load_projects(selected_id=new_project_id)
        return ("✅ Project saved!", updated_dropdown, gr.update(visible=False))
    else:
        return f"❌ Failed to save: {response.text}", gr.update(), gr.update()
