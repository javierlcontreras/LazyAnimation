from human_drawer import *
import random
import tqdm
import glob

from PIL import ImageFont, ImageDraw, Image

from configuration_constants import VIDEO_SETTINGS, ART_PATHS


class AnimationEngine:
    def __init__(self):
        self.human_drawer = HumanDrawer()

    def getFrame(self, frame_info):
        eyes = frame_info["eyes"]
        mouth = frame_info["mouth"]
        hands = frame_info["hands"]
        eyebrows = frame_info["eyebrows"]
	
        image = self.human_drawer.draw(hands, mouth, eyes, eyebrows)

        frame_resized = self._imageResize(image, VIDEO_SETTINGS["WIDTH"], VIDEO_SETTINGS["HEIGHT"])
        return frame_resized

    def _writeTextOnImage(self, img, word):
        (W, H) = img.size
        fontsize = 200

        draw = ImageDraw.Draw(img)
        color = (0, 0, 0)

        while True:
            font = ImageFont.truetype(f"{ART_PATHS['FONTS']}/SODORBld.ttf", fontsize)

            x1, y1, x2, y2 = draw.textbbox((0, 0), word, font=font)
            w = x2 - x1
            h = y2 - y1
            if w > 0.7 * W or h > 0.7 * H:
                fontsize -= 1
            else:
                break

        draw.text(((W - w) / 2, (H - h) / 2), word.replace("-", " "), font=font, fill="white",
                  stroke_width=fontsize // 10, stroke_fill="black")

        return img

    def _imageResize(self, img, W, H):
        h, w = img.size

        back = np.zeros((H, W, 3), dtype="uint8")

        if w / W > h / H:
            swidth = W
            sheight = h * W / w
        else:
            sheight = H
            swidth = w * H / h

        sheight = int(sheight)
        swidth = int(swidth)
        img = img.resize((swidth, sheight), resample=Image.Resampling.NEAREST)

        pil_back = Image.new("RGBA", (W, H))
        dx = W // 2 - swidth // 2
        dy = H // 2 - sheight // 2
        pil_back.paste(img, (dx, dy), mask=img)

        return pil_back
