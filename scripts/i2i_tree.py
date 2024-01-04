from scripts.i2i_info import img2input, path2hash
from PIL import UnidentifiedImageError
from modules import script_callbacks
from modules.shared import opts
import gradio as gr
import os

def parse_latest_folder() -> str:
    """
    Attempt to parse Options to find the folder(s) that contain all the generated images
    """

    dir2check = []

    # [Default]: Empty; Uses outputs folder with sub-folder
    if len(opts.outdir_samples.strip()) == 0:
        dir2check.append(os.path.abspath(opts.outdir_txt2img_samples))
        dir2check.append(os.path.abspath(opts.outdir_img2img_samples))
    else:
        dir2check.append(os.path.abspath(opts.outdir_samples))

    if opts.save_to_dirs: # [Default]: True; Save to Folders sorted by Date
        latest_folders = [os.path.join(folder,
            max(
                os.listdir(folder),
                key=lambda subfolder: os.path.getmtime(os.path.join(folder, subfolder)),
                default=None
            )
        ) for folder in dir2check]

        return "\n".join(latest_folders)

    else:
        return "\n".join(dir2check)

def populate_textfields():
    try:
        return gr.update(value=str(parse_latest_folder()))
    except FileNotFoundError:
        print('Something went wrong while trying to parse output paths. Create a new Issue on GitHub with your save directory options.')
        return gr.update(value='')


def load_images(image_paths:str) -> list:
    if len(image_paths.strip()) == 0:
        print('Path is Empty...')
        return []

    folders = [F.strip() for F in image_paths.split('\n')]

    image_files = []
    for FOLDER in folders:
        if not os.path.exists(FOLDER): continue
        image_files += [os.path.join(FOLDER, F) for F in os.listdir(FOLDER)]

    img_list = []
    for img in image_files:
        try:
            img_list.append((img, f'{img}_-{path2hash(img)}_-{img2input(img)}'))
        except PermissionError:
            # Folder
            continue
        except UnidentifiedImageError:
            # Not Image
            continue

    if len(img_list) == 0:
        print('Hmm... No images detected...')

    return img_list


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
                img_folders = gr.Textbox('', lines=4, label='Image Folders', interactive=True, scale=8)
                with gr.Column(scale=1):
                    pop_btn = gr.Button('(Try) Populate')
                    load_btn = gr.Button('Generate', variant='primary')

        res_gal = gr.Gallery(elem_id='i2i_tree_nodes', visible=False)

        with gr.Row():
            img_open = gr.Textbox('', visible=False, elem_id='i2i_tree_img_open')
            oimg_btn = gr.Button('', visible=False, elem_id='i2i_tree_oimg_btn')

        pop_btn.click(populate_textfields, outputs=img_folders)
        oimg_btn.click(open_image, inputs=img_open)
        load_btn.click(load_images, inputs=img_folders, outputs=res_gal).success(
            None, None, None, _js="() => { i2i_construct_tree(); }")

    return [(TREE, 'i2i Tree', 'sd-webui-i2i-ancestral-tree')]

script_callbacks.on_ui_tabs(tree_ui)
