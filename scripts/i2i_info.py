"""Script that injects source information during img2img"""

from scripts.i2i_cache import image_to_hash
from modules import scripts


class i2iInfo(scripts.Script):

    def title(self):
        return "i2i Info"

    def show(self, is_img2img):
        return scripts.AlwaysVisible if is_img2img else None

    def ui(self, is_img2img):
        return None

    def process(self, p):
        i2i_type = "img2img"
        source_image = p.init_images[0]

        if getattr(p, "image_mask", None):
            i2i_type = "inpaint"
        else:
            old_w, old_h = source_image.size
            new_w = p.width
            new_h = p.height

            if (new_w > old_w) or (new_h > old_h):
                i2i_type = "upscale"
            elif (new_w < old_w) or (new_h < old_h):
                i2i_type = "downscale"

        p.extra_generation_params["source_hash"] = (
            f"{i2i_type}-[=]-{image_to_hash(source_image)}"
        )

        return p
