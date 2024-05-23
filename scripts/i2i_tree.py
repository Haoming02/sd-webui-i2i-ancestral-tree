"""Script that handles the user interface"""

from scripts.folder_utils import get_latest_folder, open_image, load_images
from modules import script_callbacks
import gradio as gr


def tree_ui():

    with gr.Blocks() as TREE:
        with gr.Row(elem_id="i2i_tree_tools"):
            img_folders = gr.Textbox(
                value=get_latest_folder,
                lines=1,
                max_lines=2,
                label="Image Folders",
                interactive=True,
                scale=4,
            )

            load_btn = gr.Button("Generate", variant="primary", scale=1)

        graph_gallery = gr.Textbox(visible=False, elem_id="i2i_tree_nodes")

        load_btn.click(
            fn=load_images, inputs=[img_folders], outputs=[graph_gallery]
        ).success(None, None, None, _js="() => { i2i_construct_tree(); }")

        img_open = gr.Textbox(visible=False, elem_id="i2i_tree_img_open")
        img_open.change(open_image, inputs=[img_open], outputs=None)

        img_folders.do_not_save_to_config = True

    return [(TREE, "i2i Graph", "sd-webui-i2i-ancestral-tree")]


script_callbacks.on_ui_tabs(tree_ui)
