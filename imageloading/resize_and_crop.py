from PIL import Image, ImageDraw, ImageFont
import numpy as np

def resize_and_crop(image, target_width, target_height):
    # Get original dimensions
    w, h = image.size

    # Compute scaling factors
    scale_w = target_width / w
    scale_h = target_height / h
    scale = max(scale_w, scale_h)  # Scale to fill the whole target area

    # Resize while maintaining aspect ratio
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Compute center crop
    x_offset = (new_w - target_width) // 2
    y_offset = (new_h - target_height) // 2
    cropped = resized.crop((x_offset, y_offset, x_offset + target_width, y_offset + target_height))

    return cropped

