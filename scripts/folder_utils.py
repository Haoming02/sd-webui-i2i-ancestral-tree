"""Script that parses the folder structures"""

from modules.shared import opts

from scripts.i2i_cache import (
    IMAGE_HASH_CACHE,
    SOURCE_HASH_CACHE,
)

from scripts.graph_utils import iTreeNode, construct_hierarchy

from PIL import Image
import subprocess
import threading
import base64
import json
import glob
import io
import os

SAFE_GUARD = 64


def image_to_base64(img_path: str, upper_limit: int = 1024) -> str:
    """Scale a large image into a small image, then convert into base64 format"""

    img = Image.open(img_path)
    og_w, og_h = w, h = img.size

    while (w > upper_limit) or (h > upper_limit):
        w //= 2
        h //= 2

    if w != og_w:
        img = img.resize((w, h), Image.Resampling.BILINEAR)

    img_byte = io.BytesIO()
    img.save(img_byte, format="JPEG", optimize=True)
    return base64.b64encode(img_byte.getvalue()).decode("utf-8")


def get_image_url(node: dict):
    node["url"] = f"data:image/jpeg;base64,{image_to_base64(node['path'])}"


def get_latest_folder() -> str:
    """Parse options to find the folder that contains the latest generated images"""

    try:
        if getattr(opts, "outdir_samples", "").strip():
            dir = os.path.abspath(opts.outdir_samples)
        else:
            dir = os.path.abspath(opts.outdir_img2img_samples)

        if getattr(opts, "save_to_dirs", True):
            if os.listdir(dir):
                return os.path.join(dir, os.listdir(dir)[-1])
            else:
                return dir

    except:
        return ""


def open_image(path: str):
    """Handles the image-click event from the Graph"""
    path = os.path.normpath(path)

    # Confirmed to work on Win 11
    if os.name == "nt":
        subprocess.run(f'explorer /select, "{path}"')
    # Untested...
    else:
        subprocess.run(f'xdg-open --select, "{path}"')


def empty_check() -> InterruptedError:
    """When loading too many empty files, ask for continue"""

    print(
        f"\n\n[i2i] None of the past {SAFE_GUARD} images contain the information of source hash...\n"
        "(This may also mean that it is loading txt2img results, if the folder also includes them)\n"
    )

    check = input("Do you wish to continue?\n\t[Y/n]: ")

    if check.strip() != "Y":
        raise InterruptedError(
            "\n\nEnsure that:\n"
            "1. Infotext metadata is Enabled\n"
            "2. Specfify a folder that contains img2img results generated AFTER this Extension is installed\n"
            "3. Sketch & Inpaint Sketch images do NOT work\n"
        )


def load_images(folder_paths: str) -> str:
    """Parse and load all images in the specified folders"""
    if not folder_paths.strip():
        raise ValueError("\n[i2i] Folder path is empty...\n")

    folders = [folder.strip('"').strip() for folder in folder_paths.split("\n")]
    image_files = set()

    for folder in folders:
        if os.path.exists(folder):
            objs = glob.glob(os.path.join(folder, "**", "*"), recursive=True)

            for obj in objs:
                if os.path.isdir(obj) or obj.endswith(".txt"):
                    continue
                else:
                    image_files.add(obj)

    if len(image_files) == 0:
        raise FileNotFoundError("\n\n[i2i] Hmm... No images detected...\n")

    SOURCE_LIST = []
    RESULT_LIST = []

    empty_count = 0

    for img_path in image_files:

        source_hash, i2i_mode = SOURCE_HASH_CACHE.get(img_path, tag=True)

        if not source_hash:
            empty_count += 1

            if empty_count > SAFE_GUARD:
                empty_check()
                empty_count = 0

            continue

        sauce_path = IMAGE_HASH_CACHE.get(source_hash)

        if not sauce_path:
            # print(f'\n[i2i] Image "{img_path}" was not img2img from generated results...')
            continue
        if not os.path.exists(sauce_path):
            print(
                f'\n[i2i] The source image\n\t"{sauce_path}"\nfor the result image\n\t"{img_path}"\nwas not found...\n'
            )
            continue

        result_node = iTreeNode(
            None,
            img_path,
            sauce_path,
            i2i_mode,
        )

        source_node = iTreeNode(
            None,
            sauce_path,
            None,
            None,
        )

        RESULT_LIST.append(result_node)
        SOURCE_LIST.append(source_node)

    if len(SOURCE_LIST) == 0:
        raise FileNotFoundError("\n\n[i2i] Hmm... No valid images detected...\n")

    tree, path_mapping = construct_hierarchy(RESULT_LIST, SOURCE_LIST)

    threads = []
    for node in path_mapping.values():
        thread = threading.Thread(target=get_image_url, args=(node,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return f"{json.dumps(tree)}-[=]-{json.dumps(path_mapping)}"
