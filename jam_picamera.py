from PIL import Image
from picamera import PiCamera
import os

overlay_path = os.path.join(os.path.dirname(__file__), 'bbw.png')
overlay = Image.open(overlay_path)

def _pad(resolution, width=32, height=16):
    # A little utility routine which pads the specified resolution
    # up to the nearest multiple of *width* and *height*; this is
    # needed because overlays require padding to the camera's
    # block size (32x16)
    return (
        ((resolution[0] + (width - 1)) // width) * width,
        ((resolution[1] + (height - 1)) // height) * height,
    )

class JamPiCamera(PiCamera):
    def start_preview(self):
        pad = Image.new('RGB', _pad(self.resolution))
        pad.paste(overlay, (0, 0))
        self.add_overlay(pad.tobytes(), alpha=50, layer=3)
        super(JamPiCamera, self).start_preview()

    def capture(self, picture_path):
        super(JamPiCamera, self).capture(picture_path)
        output_img = Image.open(picture_path).convert('RGBA')
        new_output = Image.alpha_composite(output_img, overlay)
        new_output.save(picture_path)
