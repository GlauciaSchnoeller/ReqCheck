import os
from urllib.parse import urlparse

import gradio as gr
import requests

from .config import BACKEND_URL
from .constants import ERROR, SUCCESS, dic_icons


def get_filename(file):
    filename = os.path.basename(urlparse(file).path)
    return filename


def upload_pdf(project_id: int, pdf_file: dict):
    if not project_id:
        return (
            f"{dic_icons.get(ERROR)} Please select a project before uploading a PDF.",
            gr.update(),
        )

    if pdf_file is None:
        return f"{dic_icons.get(ERROR)} No PDF file uploaded.", gr.update()

    try:
        with open(pdf_file.name, "rb") as f:
            url = f"{BACKEND_URL}/business-visions/upload/"
            response = requests.post(url, files={"pdf": f}, data={"project": project_id})
        if response.status_code == 201:
            status = f"{dic_icons.get(SUCCESS)} Upload successful."
        else:
            status = f"{dic_icons.get(ERROR)} Error: {response.text}"
    except Exception as e:
        status = f"{dic_icons.get(ERROR)} Upload failed: {str(e)}"

    return status, update_business_visions(project_id)


def update_business_visions(project_id=None):

    url = f"{BACKEND_URL}/business-visions/"
    if project_id:
        url += f"?project={project_id}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        options = [(get_filename(r["pdf"]), str(r["id"])) for r in data]
        return gr.update(choices=options)
    return gr.update(choices=[])
