import asyncio
import base64
import os

import gradio as gr

from .artifacts import get_artifacts, update_requirement_wrapped
from .business_visions import upload_pdf
from .config import STATIC_DIR
from .projects import load_projects, save_project
from .questions import ask_question, ask_question_chat
from .requirements import (
    add_requirement,
    delete_and_update,
    edit_requirement,
    validate_all_requirements,
    validate_requirement,
)

APP_TITLE = "ReqCheck - Requirements Checking"
PORT = 7860


def get_header_html(logo_b64: str) -> str:
    return f"""
    <div class="header">
      <img src="data:image/png;base64,{logo_b64}" alt="Logo"/>
      <div class="header-title">{APP_TITLE}</div>
    </div>
    """


async def hide_status_message():
    await asyncio.sleep(10)
    return gr.update(visible=False)


def toggle_visible_and_reset(current_visible):
    clear = "" if not current_visible else gr.update()
    return (gr.update(visible=not current_visible), not current_visible, clear, clear)


def toggle_visible(current_visible):
    return gr.update(visible=not current_visible), not current_visible


def toggle_edit_tools(selected_id, req_map, previous_selected):
    if not selected_id:
        return (gr.update(visible=False), gr.update(visible=False), None)

    if selected_id == previous_selected:
        return (gr.update(visible=False), gr.update(visible=False), None)
    else:
        req_text = req_map.get(selected_id, "")
        return (
            gr.update(value=req_text, visible=True, interactive=False),
            gr.update(visible=True),
            selected_id,
        )


def show_full_preview(selected_id, req_map):
    if not selected_id:
        return gr.update(visible=False)
    return gr.update(value=req_map.get(selected_id, ""), visible=True)


def handle_edit(project_id, req_id, new_text):
    updated_choices, updated_map = edit_requirement(
        req_id=int(req_id), project_id=project_id, new_text=new_text
    )

    return (
        gr.update(choices=[("", None)] + updated_choices, value=None),
        gr.update(value=new_text, visible=False, interactive=False),
        gr.update(visible=False),
        updated_map,
        gr.update(value="✅ Requirement updated successfully", visible=True),
    )


def handle_delete(req_id, project_id):
    message, updated_choices = delete_and_update(req_id, project_id)

    return (
        message,
        gr.update(choices=[("", None)] + updated_choices, value=None),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value=None, visible=False),
    )


def run_server():
    logo_path = os.path.join(STATIC_DIR, "logo.png")
    custom_css = os.path.join(STATIC_DIR, "custom.css")

    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(custom_css) as f:
        css = f.read()

    with gr.Blocks(title=APP_TITLE, css=css) as demo:
        gr.HTML(get_header_html(logo_b64))

        # states
        new_project_visible = gr.State(False)
        add_req_visible = gr.State(False)
        add_bv_visible = gr.State(False)
        chatbot_state = gr.State([])
        requirement_map_state = gr.State({})
        selected_req_state = gr.State(value=None)

        with gr.Row(elem_id="main-row"):
            with gr.Column(scale=3, min_width=320, elem_id="sidebar"):
                gr.Markdown("## 📁 Projects", elem_classes="sidebar-title")
                project_dropdown = gr.Dropdown(label="", choices=[], type="value")
                btn_add_project = gr.Button("➕ Add Project")

                with gr.Column(visible=False, elem_id="new-project-section") as new_project_section:
                    project_name = gr.Textbox(label="Project Name")
                    project_description = gr.Textbox(label="Project Description", lines=2)
                    save_project_btn = gr.Button("📎 Save Project")

                status_output_project = gr.Markdown(visible=False)

            with gr.Column(scale=7, min_width=600, elem_id="main-content"):
                with gr.Tabs():
                    with gr.Tab("📋 Requirements"):
                        with gr.Group(elem_classes="box"):
                            gr.Markdown("### RequirementS")

                            with gr.Column(visible=False) as add_req_section:
                                input_text = gr.Textbox(label="New Requirement", lines=3)
                                btn_save_req = gr.Button(
                                    "Save Requirement", elem_classes="btn-save"
                                )

                            requirements_list = gr.Dropdown(
                                label="🔽 Select a requirement",
                                choices=[],
                                type="value",
                                value=None,
                                interactive=True,
                                show_label=True,
                            )

                            with gr.Row(elem_id="req-buttons-row"):
                                btn_add_req = gr.Button("➕ Add Requirement")
                                btn_validate_req = gr.Button("✅ Validate Requirement")
                                btn_validate_all = gr.Button("✅ Validate All Requirements")

                            full_text_preview = gr.Textbox(
                                label="Full Requirement", visible=False, interactive=False
                            )

                            edit_field = gr.Textbox(
                                label="Selected Requirement (Editable)",
                                visible=False,
                                interactive=False,
                            )

                            with gr.Row(visible=False) as edit_buttons_row:
                                btn_edit_req = gr.Button("✏️ Edit")
                                btn_save_edit = gr.Button("📎 Save Edit")
                                btn_delete_req = gr.Button("🗑️ Delete")

                            status_output_req = gr.Textbox(
                                label="📢 Status / Result", lines=2, interactive=False, max_lines=20
                            )

                    with gr.Tab("📄 Business Vision"):
                        with gr.Group(elem_classes="box"):
                            gr.Markdown("### Business Vision")

                            with gr.Column(visible=False) as add_bv_section:
                                pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
                                btn_process_pdf = gr.Button(
                                    "📅 Process PDF", elem_classes="btn-save"
                                )

                            business_vision_list = gr.Radio(
                                label="Existing Business Vision", choices=[], type="value"
                            )

                            btn_add_bv = gr.Button("➕ Add Business Vision")

                            status_output_bv = gr.Textbox(
                                label="📢 Status / Result", lines=2, interactive=False, max_lines=20
                            )

                    with gr.Tab("❓ Ask a Question"):
                        chatbot = gr.Chatbot(label="💬 Chat", elem_id="chat-box")
                        input_ask = gr.Textbox(
                            placeholder="Enter your question...", show_label=False
                        )
                        btn_ask = gr.Button("Enviar", elem_classes="btn-save")

        # events
        demo.load(fn=load_projects, outputs=project_dropdown)

        btn_add_project.click(
            fn=toggle_visible_and_reset,
            inputs=[new_project_visible],
            outputs=[new_project_section, new_project_visible, project_name, project_description],
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
            outputs=[project_dropdown, new_project_section, status_output_project],
            show_progress=False,
        ).then(fn=hide_status_message, outputs=status_output_project).then(
            fn=update_requirement_wrapped,
            inputs=[project_dropdown],
            outputs=[requirements_list, requirement_map_state],
        )

        btn_save_req.click(
            fn=add_requirement,
            inputs=[project_dropdown, input_text],
            outputs=[status_output_req, input_text],
        ).then(
            fn=lambda: (gr.update(visible=False), False),
            outputs=[add_req_section, add_req_visible],
        ).then(
            fn=update_requirement_wrapped,
            inputs=[project_dropdown],
            outputs=[requirements_list, requirement_map_state],
        )

        project_dropdown.change(
            fn=get_artifacts,
            inputs=[project_dropdown],
            outputs=[requirements_list, requirement_map_state, business_vision_list],
        )

        btn_process_pdf.click(
            fn=upload_pdf,
            inputs=[project_dropdown, pdf_file],
            outputs=[status_output_bv, business_vision_list],
        )

        requirements_list.change(
            fn=toggle_edit_tools,
            inputs=[requirements_list, requirement_map_state, selected_req_state],
            outputs=[edit_field, edit_buttons_row, selected_req_state],
        ).then(
            fn=show_full_preview,
            inputs=[requirements_list, requirement_map_state],
            outputs=[full_text_preview],
        )

        btn_edit_req.click(
            fn=lambda x: gr.update(interactive=True),
            inputs=edit_field,
            outputs=edit_field,
        )
        btn_save_edit.click(
            fn=handle_edit,
            inputs=[project_dropdown, requirements_list, edit_field],
            outputs=[
                requirements_list,
                edit_field,
                edit_buttons_row,
                requirement_map_state,
                status_output_req,
            ],
        )

        btn_delete_req.click(
            fn=handle_delete,
            inputs=[requirements_list, project_dropdown],
            outputs=[
                status_output_req,
                requirements_list,
                edit_field,
                edit_buttons_row,
                full_text_preview,
            ],
        ).then(fn=lambda: gr.update(value=None), inputs=[], outputs=[edit_field])

        btn_validate_req.click(
            fn=validate_requirement,
            inputs=[project_dropdown, requirements_list],
            outputs=[status_output_req],
        )

        btn_validate_all.click(
            fn=validate_all_requirements, inputs=[project_dropdown], outputs=[status_output_req]
        )

        btn_ask.click(fn=ask_question, inputs=input_ask, outputs=None)

        btn_ask.click(
            fn=ask_question_chat,
            inputs=[chatbot_state, input_ask],
            outputs=[chatbot, input_ask, chatbot_state],
        ).then(fn=lambda h: h, inputs=[chatbot], outputs=[chatbot_state])

    demo.launch(server_name="0.0.0.0", server_port=PORT)


if __name__ == "__main__":
    run_server()
