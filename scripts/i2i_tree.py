from scripts.i2i_info import img2input, path2hash
from PIL import UnidentifiedImageError
from modules import script_callbacks
from modules.shared import opts
import gradio as gr
import os


empty_count = 0
Sisyphus = 100
"""Safe Guard to avoid unnecessary parsing..."""


def parse_latest_folder() -> str:
    """
    Attempt to parse Options to find the folder(s) that contain the latest generated images
    """

    dir2check = []

    # [Default]: Empty; Uses outputs folder with sub-folder
    if len(opts.outdir_samples.strip()) == 0:
        dir2check.append(os.path.abspath(opts.outdir_img2img_samples))
        dir2check.append(os.path.abspath(opts.outdir_txt2img_samples))
    else:
        dir2check.append(os.path.abspath(opts.outdir_samples))

    if opts.save_to_dirs: # [Default]: True; Save to Folders named with Date
        latest_folders = [os.path.join(folder,
            max(
                os.listdir(folder),
                key=lambda subfolder: os.path.getmtime(os.path.join(folder, subfolder)),
                default='.'
            )
        ) for folder in dir2check]

        return "\n".join(latest_folders)

    else:
        return "\n".join(dir2check)

def populate_textfields():
    """
    Parse the paths and update the Textbox
    """
    try:
        return gr.update(value=str(parse_latest_folder()))

    except FileNotFoundError:
        print('Something went wrong while trying to parse output path options. Create a new Issue on GitHub with your save directory options.')
        print('(You can still manually enter the paths)')
        return gr.update(value='')


def load_images(image_paths:str, recursive:bool) -> list:
    """
    Parse and load all images in the specified folder
    """

    if len(image_paths.strip()) == 0:
        print('Path is Empty...')
        return []

    folders = [F.strip('"').strip() for F in image_paths.split('\n')]

    image_files = []
    for FOLDER in folders:
        if os.path.exists(FOLDER):
            image_files += [os.path.join(FOLDER, F) for F in os.listdir(FOLDER)]

    global empty_count
    empty_count = 0
    return_list = []

    image_files = sorted(image_files, key=lambda x: os.path.getmtime(x), reverse=True)

    for img in image_files:
        if empty_count > Sisyphus:
            break

        try:
            self_hash = path2hash(img)
            parent_hash = img2input(img)

            # Pray no sane person names folder with `_-`
            return_list.append((img, f'{img}_-{self_hash}_-{parent_hash}'))

            if parent_hash is None:
                empty_count += 1
            else:
                empty_count -= 1

            if empty_count > Sisyphus:
                print(f'\nNone of the past {Sisyphus} images contains the input hash information...')
                print('(This could also simply mean it is loading txt2img results)')
                CHECK = input('Do you wish to continue?\n\t[Y/n]: ')

                if CHECK.strip() == 'Y':
                    empty_count = 0
                else:
                    print('\nEnsure that:')
                    print('1. Infotext metadata is Enabled')
                    print('2. Specfify a folder that contains images generated AFTER this Extension is installed')
                    print('3. Sketch & Inpaint Sketch images do NOT work\n')

        except PermissionError:
            # Folder
            if recursive is True or recursive is None:
                return_list += load_images(img, None)
            else:
                continue

        except UnidentifiedImageError:
            # Not Image
            continue

    if recursive is not None and len(return_list) == 0:
        print('Hmm... No images detected...')

    return return_list


def open_image(path:str):
    """
    Handles the image-click event from the Graph
    """
    import subprocess
    path = os.path.normpath(path)

    if os.name == 'nt':
        # Confirmed to work on Win11
        subprocess.run(['explorer', '/select,', path])
    else:
        # Untested...
        subprocess.run(['xdg-open', '--select', path])


def tree_ui():

    with gr.Blocks() as TREE:
        with gr.Column(elem_id='i2i_tree_tools'):
            with gr.Row():
                img_folders = gr.Textbox('', lines=4, label='Image Folders', interactive=True, scale=8)

                with gr.Column(scale=1):
                    rec_cbx = gr.Checkbox(label='Recursive Search')
                    pop_btn = gr.Button('Populate')
                    load_btn = gr.Button('Generate', variant='primary')

        res_gal = gr.Gallery(elem_id='i2i_tree_nodes', visible=False)

        with gr.Row():
            img_open = gr.Textbox('', visible=False, elem_id='i2i_tree_img_open')
            oimg_btn = gr.Button('', visible=False, elem_id='i2i_tree_oimg_btn')

        pop_btn.click(populate_textfields, outputs=img_folders)
        oimg_btn.click(open_image, inputs=img_open)
        load_btn.click(load_images, inputs=[img_folders, rec_cbx], outputs=res_gal).success(
            None, None, None, _js="() => { i2i_construct_tree(); }")

    return [(TREE, 'i2i Tree', 'sd-webui-i2i-ancestral-tree')]

script_callbacks.on_ui_tabs(tree_ui)
