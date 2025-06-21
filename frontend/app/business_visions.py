import os
from urllib.parse import urlparse

import gradio as gr
import requests

from .config import BACKEND_URL


def get_filename(file):
    filename = os.path.basename(urlparse(file).path)
    return filename


def upload_pdf(project_id: int, pdf_file: dict):
    if not project_id:
        return "❌ Please select a project before uploading a PDF."

    if pdf_file is None:
        return "❌ No PDF file uploaded."

    try:
        with open(pdf_file.name, "rb") as f:
            url = f"{BACKEND_URL}/business-visions/upload/"
            response = requests.post(url, files={"pdf": f}, data={"project": project_id})
        if response.status_code == 201:
            return "✅ Upload successful."
        else:
            return f"❌ Error: {response.text}"
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"


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
