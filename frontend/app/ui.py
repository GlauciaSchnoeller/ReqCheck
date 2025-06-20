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


def get_header_html(logo_b64: str) -> str:
    return f"""
    <div class="header">
      <img src="data:image/png;base64,{logo_b64}" alt="Logo"/>
      <div class="header-title">{APP_TITLE}</div>
    </div>
    """


def run_server():

    logo_path = os.path.join(STATIC_DIR, "logo.png")
    custom_css = os.path.join(STATIC_DIR, "custom.css")

    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(custom_css) as f:
        css = f.read()

    with gr.Blocks(title=APP_TITLE, css=css) as demo:

        gr.HTML(get_header_html(logo_b64))

        new_project_visible = gr.State(False)
        add_req_visible = gr.State(False)
        add_bv_visible = gr.State(False)

        with gr.Row(elem_id="main-row"):
            with gr.Column(scale=3, min_width=320, elem_id="sidebar"):
                gr.Markdown("## 📁 Projects", elem_classes="sidebar-title")
                project_dropdown = gr.Dropdown(label="", choices=[], type="value")
                btn_add_project = gr.Button("➕ Add Project")

                with gr.Column(visible=False, elem_id="new-project-section") as new_project_section:
                    project_name = gr.Textbox(label="Project Name")
                    project_description = gr.Textbox(label="Project Description", lines=2)
                    save_project_btn = gr.Button("💾 Save Project")

            with gr.Column(scale=7, min_width=600, elem_id="main-content"):
                with gr.Tab("Project Details"):

                    with gr.Group(elem_classes="box"):
                        gr.Markdown("### 📝 Requirements")

                        with gr.Column(visible=False) as add_req_section:
                            input_text = gr.Textbox(label="New Requirement", lines=3)
                            btn_save_req = gr.Button("Save Requirement", elem_classes="btn-save")

                        requirements_list = gr.Radio(
                            label="Existing Requirements", choices=[], type="value"
                        )

                        btn_add_req = gr.Button("➕ Add Requirement")

                        edit_field = gr.Textbox(label="Edit Selected Requirement", visible=False)
                        with gr.Row(visible=False) as edit_buttons_row:
                            btn_edit_req = gr.Button("✏️ Edit")
                            btn_save_edit = gr.Button("💾 Save Edit")
                            btn_delete_req = gr.Button("🗑️ Delete")

                    with gr.Group(elem_classes="box"):
                        gr.Markdown("### 📄 Business Vision")

                        with gr.Column(visible=False) as add_bv_section:
                            pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
                            btn_process_pdf = gr.Button("📥 Process PDF", elem_classes="btn-save")

                        business_vision_list = gr.Radio(
                            label="Existing Business Vision", choices=[], type="value"
                        )

                        btn_add_bv = gr.Button("➕ Add Business Vision")

                    status_output = gr.Textbox(
                        label="📢 Status / Result",
                        lines=3,
                        interactive=False,
                        max_lines=10,
                        show_copy_button=True,
                    )

                with gr.Tab("❓ Ask a Question"):
                    input_ask = gr.Textbox(label="Enter your question")
                    btn_ask = gr.Button("Ask", elem_classes="btn-save")
                    answer = gr.Textbox(label="Answer")

        def toggle_visible(current_visible):
            return gr.update(visible=not current_visible), not current_visible

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

        btn_add_project.click(
            fn=toggle_visible,
            inputs=new_project_visible,
            outputs=[new_project_section, new_project_visible],
        )
        btn_add_req.click(
            fn=toggle_visible, inputs=add_req_visible, outputs=[add_req_section, add_req_visible]
        )
        btn_add_bv.click(
            fn=toggle_visible, inputs=add_bv_visible, outputs=[add_bv_section, add_bv_visible]
        )

        save_project_btn.click(
            fn=save_project,
            inputs=[project_name, project_description],
            outputs=[status_output, project_dropdown, new_project_section],
        )

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
