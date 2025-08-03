import gradio as gr

from .business_visions import update_business_visions
from .requirements import update_requirement


def update_requirement_wrapped(project_id=None):
    options, mapping = update_requirement(project_id)
    options.insert(0, ("", None))

    return gr.update(choices=options, value=None), mapping


def get_artifacts(projects_id):
    requirements_list, requirement_map_state = update_requirement_wrapped(projects_id)
    business_vision_list = update_business_visions(projects_id)  # noqa: F821
    return (requirements_list, requirement_map_state, business_vision_list)
