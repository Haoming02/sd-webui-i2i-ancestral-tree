from modules.images import read_info_from_image
import modules.scripts as scripts
from pathlib import Path
from PIL import Image
import os


def img2hash(img:Image) -> str:
    from hashlib import md5
    return md5(img.convert('L').tobytes()).hexdigest()

def path2hash(path:str) -> str:
    return img2hash(Image.open(path))

def img2input(path:str) -> str:
    info, _ = read_info_from_image(Image.open(path))

    if info is not None:
        for chunks in [line.split(',') for line in info.split('\n')]:
            for p in chunks:
                if 'input_hash' in p:
                    return p.split(':')[1].strip()

    else:
        p = Path(path)
        info = p.with_suffix('.txt')
        if os.path.exists(info):

            with open(info, 'r', encoding='utf8') as INFOTEXT:
                DATA = INFOTEXT.readlines()

                for chunks in [line.split(',') for line in DATA]:
                    for p in chunks:
                        if 'input_hash' in p:
                            return p.split(':')[1].strip()

    return None


class i2iInfo(scripts.Script):

    def title(self):
        return "i2i Info"

    def show(self, is_img2img):
        return scripts.AlwaysVisible if is_img2img else None

    def ui(self, is_img2img):
        return None

    def process(self, p):
        i2i_type = 'I2I'

        if getattr(p, 'image_mask', None) is not None:
            i2i_type = 'INP'
        else:
            w, h = p.init_images[0].size

            if int(w) > int(p.width) or int(h) > int(p.height):
                i2i_type = 'DWS'
            elif int(w) < int(p.width) or int(h) < int(p.height):
                i2i_type = 'UPS'

        p.extra_generation_params['input_hash'] = f'{i2i_type}{img2hash(p.init_images[0])}'
        return p
