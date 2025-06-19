import base64
import os

import gradio as gr

from .business_visions import update_business_visions, upload_pdf
from .config import STATIC_DIR
from .projects import load_projects, save_project
from .questions import ask_question
from .requirements import add_requirement, delete_and_update, update_requirement

APP_TITLE = "ReqCheck - Requirements Checking"
PORT = 7860


def get_header_html(logo_base64: str) -> str:
    return f"""
    <div style="
        position: relative;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f8f9fa;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        padding: 0 30px;
        margin-bottom: 20px;
        border-radius: 8px;
    ">
        <div style="position: absolute; left: 30px;">
            <img src="data:image/png;base64,{logo_base64}"
                style="width: 60px; height: 60px; border-radius: 10px; border: 1px solid #ccc;" />
        </div>
        <div
            style="
            font-size: 32px;
            font-weight: 600;
            color: #333;
            font-family: 'Segoe UI', sans-serif;
            "
        >
            {APP_TITLE}
        </div>
    </div>
    """


def run_server() -> None:
    logo_path = os.path.join(STATIC_DIR, "logo.png")
    custom_css = os.path.join(STATIC_DIR, "custom.css")
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")

    with gr.Blocks(title=APP_TITLE, css=open(custom_css).read()) as demo:
        gr.HTML(get_header_html(logo_base64))

        with gr.Tab("📁 Project Details"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 🎯 Project")
                    project_dropdown = gr.Dropdown(label="Select Project", choices=[], type="value")
                    create_new_project_btn = gr.Button("➕ Create New Project")

                    with gr.Column(visible=False) as new_project_section:
                        project_name = gr.Textbox(label="Project Name")
                        project_description = gr.Textbox(label="Project Description", lines=2)
                        save_project_btn = gr.Button("💾 Save Project")

                with gr.Column(scale=1):
                    with gr.Group():
                        with gr.Row():
                            gr.Markdown("### 📝 Requirements")
                            btn_show_add_req = gr.Button("➕", scale=1)

                        with gr.Column(visible=False) as add_req_section:
                            input_text = gr.Textbox(label="New Requirement", lines=3)
                            btn_save_req = gr.Button("Save Requirement")

                        requirements_list = gr.Radio(
                            label="Existing Requirements", choices=[], type="value"
                        )
                        edit_field = gr.Textbox(label="Edit Selected Requirement", visible=False)

                        with gr.Row(visible=False) as edit_buttons_row:
                            btn_edit_req = gr.Button("✏️ Edit")
                            btn_save_edit = gr.Button("💾 Save Edit")
                            btn_delete_req = gr.Button("🗑️ Delete")

                    with gr.Group():
                        with gr.Row():
                            gr.Markdown("### 📄 Business Vision")
                            btn_show_add_bv = gr.Button("➕", scale=1)
                            business_vision_list = gr.Radio(
                                label="Existing Business Vision", choices=[], type="value"
                            )

                        with gr.Column(visible=False) as add_bv_section:
                            pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
                            btn_process_pdf = gr.Button("📥 Process PDF")

            gr.Markdown("---")
            status_output = gr.Textbox(
                label="📢 Status / Result",
                lines=3,
                interactive=False,
                max_lines=10,
                show_copy_button=True,
            )

        with gr.Tab("❓ Ask a Question"):
            input_ask = gr.Textbox(label="Enter your question")
            btn_ask = gr.Button("Ask")
            answer = gr.Textbox(label="Answer")

        def toggle_new_project_form():
            return gr.update(visible=True)

        def toggle_add_req():
            return gr.update(visible=True)

        def toggle_add_bv():
            return gr.update(visible=True)

        def show_edit_tools(req_text):
            if req_text:
                return [gr.update(value=req_text, visible=True), gr.update(visible=True)]
            else:
                return [gr.update(visible=False), gr.update(visible=False)]

        def handle_edit(project, old_text, new_text):
            return update_requirement(project_name=project, old_req=old_text, new_req=new_text)

        def handle_delete(text):
            return delete_and_update(text), update_requirement()

        demo.load(fn=load_projects, outputs=project_dropdown).then(
            fn=update_requirement, inputs=project_dropdown, outputs=requirements_list
        ).then(
            fn=update_business_visions, inputs=[project_dropdown], outputs=[business_vision_list]
        )

        create_new_project_btn.click(fn=toggle_new_project_form, outputs=new_project_section)

        save_project_btn.click(
            fn=save_project,
            inputs=[project_name, project_description],
            outputs=[status_output, project_dropdown, new_project_section],
        )

        btn_show_add_req.click(fn=toggle_add_req, outputs=add_req_section)
        btn_show_add_bv.click(fn=toggle_add_bv, outputs=add_bv_section)

        btn_save_req.click(
            fn=add_requirement,
            inputs=[project_dropdown, input_text],
            outputs=[status_output, input_text],
        ).then(fn=update_requirement, inputs=[project_dropdown], outputs=[requirements_list])

        project_dropdown.change(
            fn=update_requirement, inputs=[project_dropdown], outputs=[requirements_list]
        )

        btn_process_pdf.click(
            fn=upload_pdf, inputs=[project_dropdown, pdf_file], outputs=status_output
        )

        requirements_list.change(
            fn=show_edit_tools, inputs=requirements_list, outputs=[edit_field, edit_buttons_row]
        )
        btn_edit_req.click(
            fn=lambda x: gr.update(visible=True, value=x),
            inputs=requirements_list,
            outputs=edit_field,
        )

        btn_save_edit.click(
            fn=handle_edit,
            inputs=[project_dropdown, requirements_list, edit_field],
            outputs=[requirements_list],
        )

        btn_delete_req.click(
            fn=handle_delete, inputs=[requirements_list], outputs=[status_output, requirements_list]
        )

        btn_ask.click(fn=ask_question, inputs=input_ask, outputs=answer)

    demo.launch(server_name="0.0.0.0", server_port=PORT)


if __name__ == "__main__":
    run_server()
