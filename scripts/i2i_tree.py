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
        default='.'
    )

    latest_i2i_folder = max(
        os.listdir(I2I_OUTPUT_FOLDER),
        key=lambda folder: os.path.getmtime(os.path.join(I2I_OUTPUT_FOLDER, folder)),
        default='.'
    )

    return [
        os.path.join(T2I_OUTPUT_FOLDER, latest_t2i_folder).replace('/', '\\'),
        os.path.join(I2I_OUTPUT_FOLDER, latest_i2i_folder).replace('/', '\\')
    ]

def populate_textfields():
    t2i, i2i = parse_latest_folder()
    return [gr.update(value=t2i), gr.update(value=i2i)]


def load_images(path_t2i:str, path_i2i:str) -> list:
    if len(path_t2i.strip()) == 0 or len(path_t2i.strip()) == 0:
        return []

    filesA = [os.path.join(path_t2i, F) for F in os.listdir(path_t2i)]
    filesB = [os.path.join(path_i2i, F) for F in os.listdir(path_i2i)]

    return [
        (img, f'{img}_-{path2hash(img)}_-{img2input(img)}') for img in (filesA + filesB)
    ]


def open_image(path:str):
    path = os.path.normpath(path)

    import subprocess
    if os.name == 'nt':
        subprocess.run(['explorer', '/select,', path])
    else:
        subprocess.run(['xdg-open', '--select', path])


def tree_ui():

    with gr.Blocks() as TREE:
        with gr.Column(elem_id='i2i_tree_tools'):
            with gr.Row():
                out_t2i = gr.Textbox('', max_lines=1, label='txt2img Output', interactive=True, scale=5)
                pop_btn = gr.Button('Populate', scale=1)
                out_i2i = gr.Textbox('', max_lines=1, label='img2img Output', interactive=True, scale=5)

            load_btn = gr.Button('Load', variant='primary')

        res_gal = gr.Gallery(elem_id='i2i_tree_nodes', visible=False)

        with gr.Row():
            img_open = gr.Textbox('', visible=False, elem_id='i2i_tree_img_open')
            oimg_btn = gr.Button('', visible=False, elem_id='i2i_tree_oimg_btn')

        pop_btn.click(populate_textfields, outputs=[out_t2i, out_i2i])
        oimg_btn.click(open_image, inputs=[img_open])
        load_btn.click(load_images, inputs=[out_t2i, out_i2i], outputs=[res_gal]).success(
            None, None, None, _js="() => { i2i_construct_tree(); }")

    return [(TREE, 'i2i Tree', 'sd-webui-i2i-ancestral-tree')]

script_callbacks.on_ui_tabs(tree_ui)
