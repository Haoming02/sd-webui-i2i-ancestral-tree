"""Script that manages the local disk cache of the relationships"""

from modules.script_callbacks import on_image_saved, ImageSaveParams
from modules.scripts import basedir

from PIL import Image
from diskcache import Cache

try:
    from imagehash import phash
    iHash = True
except ModuleNotFoundError:
    from hashlib import md5
    iHash = False

import os

STORAGE_SIZE = 4 * 1024 * 1024
"""4 MB"""

IMAGE_HASH_CACHE = Cache(
    directory=os.path.join(basedir(), "cache", "image_hash"),
    size_limit=STORAGE_SIZE,
    cull_limit=32,
    eviction_policy="least-recently-stored",
)
"""
The cache that stores the hash to image mapping
  - Key: The hash of the generated image
  - Value: The path to the generated image in outputs folder
"""


SOURCE_HASH_CACHE = Cache(
    directory=os.path.join(basedir(), "cache", "source_hash"),
    size_limit=STORAGE_SIZE,
    cull_limit=32,
    eviction_policy="least-recently-stored",
)
"""
The cache that stores the hash of the source image in an img2img result
  - Key: The path to the generated image in outputs folder
  - Value: The hash of the source image
"""


def image_to_hash(image: Image) -> str:
    """Generate the hash from an image"""
    if iHash:
        return str(phash(image))
    else:
        return md5(image.convert("L").tobytes()).hexdigest()


def get_hash_from_parameters(param: str) -> str:
    """Read the source hash from the image parameters"""
    if not param:
        return None, None

    parameters: list[str] = param.split(",")
    for parameter in parameters:
        if "source_hash" in parameter:
            mode_hash_pair = parameter.split(":")[1].strip()
            return mode_hash_pair.split("-[=]-")

    return None, None


def to_path(filepath: str) -> str:
    """Return the image path in a consistent way"""
    path = os.path.abspath(filepath)
    return os.path.normpath(path)


def on_save(params: ImageSaveParams):
    """Store the hash of the image whenever one is generated and saved"""
    image_hash = image_to_hash(params.image)
    file_path = to_path(params.filename)
    IMAGE_HASH_CACHE.add(image_hash, file_path)

    i2i_mode, source_hash = get_hash_from_parameters(params.pnginfo["parameters"])
    if source_hash:
        SOURCE_HASH_CACHE.set(file_path, source_hash, tag=i2i_mode)


def reset_cache():
    """Clear out the existing caches"""
    IMAGE_HASH_CACHE.clear()
    SOURCE_HASH_CACHE.clear()


on_image_saved(on_save)
