from scripts.i2i_info import img2input, path2hash
from modules import script_callbacks
import gradio as gr
import os

def parse_latest_folder():
    from modules.shared import opts
    T2I_OUTPUT_FOLDER = os.path.join(opts.outdir_samples, opts.outdir_txt2img_samples)
    I2I_OUTPUT_FOLDER = os.path.join(opts.outdir_samples, opts.outdir_img2img_samples)

    latest_t2i_folder = max(
        os.listdir(T2I_OUTPUT_FOLDER),
        key=lambda folder: os.path.getmtime(os.path.join(T2I_OUTPUT_FOLDER, folder)),
        default=None
    )

    latest_i2i_folder = max(
        os.listdir(I2I_OUTPUT_FOLDER),
        key=lambda folder: os.path.getmtime(os.path.join(I2I_OUTPUT_FOLDER, folder)),
        default=None
    )

    return [
        os.path.abspath(os.path.join(T2I_OUTPUT_FOLDER, latest_t2i_folder)),
        os.path.abspath(os.path.join(I2I_OUTPUT_FOLDER, latest_i2i_folder))
    ]

def load_images(path_t2i:str, path_i2i:str) -> list:
    if len(path_t2i.strip()) == 0 or len(path_t2i.strip()) == 0:
        return []

    filesA = [os.path.join(path_t2i, F) for F in os.listdir(path_t2i)]
    filesB = [os.path.join(path_i2i, F) for F in os.listdir(path_i2i)]

    return [
        (img, f'{path2hash(img)}-{img2input(img)}') for img in (filesA + filesB)
    ]

def populate_textfields():
    t2i, i2i = parse_latest_folder()
    return [gr.update(value=t2i), gr.update(value=i2i)]

def tree_ui():

    with gr.Blocks() as TREE:
        with gr.Column(elem_id='i2i_tree_tools'):
            with gr.Row():
                out_t2i = gr.Textbox('', max_lines=1, label='txt2img Output', interactive=True, scale=5)
                pop_btn = gr.Button('Populate', scale=1)
                out_i2i = gr.Textbox('', max_lines=1, label='img2img Output', interactive=True, scale=5)

            load_btn = gr.Button('Load', variant='primary')

        res_gal = gr.Gallery(elem_id='i2i_tree_nodes', visible=False)

        pop_btn.click(populate_textfields, outputs=[out_t2i, out_i2i])
        load_btn.click(load_images, inputs=[out_t2i, out_i2i], outputs=[res_gal]).success(
            None, None, None, _js="() => { i2i_construct_tree(); }")

    return [(TREE, 'i2i Tree', 'sd-webui-i2i-ancestral-tree')]

script_callbacks.on_ui_tabs(tree_ui)
