import base64
import os

import gradio as gr

from .config import STATIC_DIR
from .handlers import (
    add_requirement,
    ask_question,
    delete_and_update,
    update_requirement,
    upload_pdf,
)

APP_TITLE = "ReqCheck - Requirements Checking"
PORT = 7860


def get_header_html(logo_base64: str) -> str:
    return f"""
    <div style="
        position: relative;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-bottom: 1px solid #ddd;
        padding: 0 20px;
        margin-bottom: 30px;
    ">
        <div style="position: absolute; left: 20px;">
            <img src="data:image/png;base64,{logo_base64}"
                style="width: 60px; height: 60px; border-radius: 50%;" />
        </div>
        <div style="font-size: 28px; font-weight: bold; margin: 0 auto;">
            {APP_TITLE}
        </div>
    </div>
    """


def run_server() -> None:
    logo_path = os.path.join(STATIC_DIR, "logo.png")

    with gr.Blocks(title=APP_TITLE) as demo:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")

        gr.HTML(get_header_html(logo_base64))

        with gr.Tab("➕ Add Requirement"):
            input_text = gr.Textbox(label="New Requirement", lines=4)
            btn_save = gr.Button("Save")
            status = gr.Textbox(label="Status")
            btn_save.click(fn=add_requirement, inputs=input_text, outputs=[status, input_text])

        with gr.Tab("📋 View Requirements"):
            btn_update = gr.Button("🔄 Update List")
            dropdown = gr.Radio(label="Requirements", choices=[], type="value")
            btn_delete = gr.Button("🗑️ Delete Selected")
            status = gr.Textbox(label="Status", interactive=False)

            btn_update.click(fn=update_requirement, outputs=dropdown)
            btn_delete.click(fn=delete_and_update, inputs=dropdown, outputs=[status, dropdown])

        with gr.Tab("❓ Ask a Question"):
            input_ask = gr.Textbox(label="Enter your question")
            btn_ask = gr.Button("Ask")
            answer = gr.Textbox(label="Answer")
            btn_ask.click(fn=ask_question, inputs=input_ask, outputs=answer)

        with gr.Tab("📄 Add business vision"):
            pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
            btn_process_pdf = gr.Button("Process PDF")
            output_pdf = gr.Textbox(label="Result", lines=10)

            btn_process_pdf.click(fn=upload_pdf, inputs=pdf_file, outputs=output_pdf)

    demo.launch(server_name="0.0.0.0", server_port=PORT)


if __name__ == "__main__":
    run_server()
