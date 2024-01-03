import modules.scripts as scripts
from PIL import Image


def img2hash(img:Image) -> str:
    from hashlib import md5
    return md5(img.convert('L').tobytes()).hexdigest()

def path2hash(path:str) -> str:
    return img2hash(Image.open(path))

def img2input(path:str) -> str:
    params = Image.open(path).info['parameters'].split(',')

    for p in params:
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
