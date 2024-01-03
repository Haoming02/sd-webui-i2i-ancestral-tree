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
        T2I_OUTPUT_FOLDER.replace('/', '\\'),
        latest_i2i_folder.replace('/', '\\'),
        I2I_OUTPUT_FOLDER.replace('/', '\\'),
        latest_i2i_folder.replace('/', '\\')
    ]

def populate_textfields():
    t2i, t2if, i2i, i2if = parse_latest_folder()
    return [
        gr.update(value=t2i),
        gr.update(value=t2if),
        gr.update(value=i2i),
        gr.update(value=i2if)
    ]


def load_images(path_t2i:str, t2i_folders:str, path_i2i:str, i2i_folders:str) -> list:
    if len(path_t2i.strip()) == 0 or len(path_t2i.strip()) == 0:
        return []
    if len(t2i_folders.strip()) == 0 or len(i2i_folders.strip()) == 0:
        return []

    foldersA = [os.path.join(path_t2i, SUB.strip()) for SUB in t2i_folders.split(',')]
    foldersB = [os.path.join(path_i2i, SUB.strip()) for SUB in i2i_folders.split(',')]

    image_files = []
    for FOLDER in (foldersA + foldersB):
        if not os.path.exists(FOLDER): continue
        image_files += [os.path.join(FOLDER, F) for F in os.listdir(FOLDER)]

    return [
        (img, f'{img}_-{path2hash(img)}_-{img2input(img)}') for img in image_files
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
                out_t2i = gr.Textbox('', max_lines=1, label='txt2img', interactive=True, scale=2)
                out_t2if = gr.Textbox('', max_lines=1, label='Folders', interactive=True, scale=3)
                pop_btn = gr.Button('Populate', scale=1)
                out_i2i = gr.Textbox('', max_lines=1, label='img2img', interactive=True, scale=2)
                out_i2if = gr.Textbox('', max_lines=1, label='Folders', interactive=True, scale=3)

            load_btn = gr.Button('Load', variant='primary')

        res_gal = gr.Gallery(elem_id='i2i_tree_nodes', visible=False)

        with gr.Row():
            img_open = gr.Textbox('', visible=False, elem_id='i2i_tree_img_open')
            oimg_btn = gr.Button('', visible=False, elem_id='i2i_tree_oimg_btn')

        pop_btn.click(populate_textfields, outputs=[out_t2i, out_t2if, out_i2i, out_i2if])
        oimg_btn.click(open_image, inputs=[img_open])
        load_btn.click(load_images, inputs=[out_t2i, out_t2if, out_i2i, out_i2if], outputs=[res_gal]).success(
            None, None, None, _js="() => { i2i_construct_tree(); }")

    return [(TREE, 'i2i Tree', 'sd-webui-i2i-ancestral-tree')]

script_callbacks.on_ui_tabs(tree_ui)
