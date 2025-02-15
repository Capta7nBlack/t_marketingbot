from PIL import Image, ImageDraw, ImageFont
import numpy as np
from imageloading.resize_and_crop import resize_and_crop
import os

def overlay_images(background_path, foreground_path, output_path, text, font_scale=1.75, thickness=2):
    # Load images
    background = Image.open(background_path).convert("RGBA")
    foreground = Image.open(foreground_path).convert("RGBA")  # Keep alpha

    if background is None:
        print("input image hasn't loaded")
    if foreground is None:
        print("frame image didn't load")

    w, h = foreground.size
    print("inthe start")
    print(h)
    # Resize and crop background to match foreground dimensions
    background = resize_and_crop(background, w, h)

    # If foreground has alpha channel, blend it with the background
    if foreground.mode == "RGBA":
        # Create a new image to hold the blended result
        blended = Image.new("RGBA", background.size)
        blended.paste(background, (0, 0))
        blended.paste(foreground, (0, 0), foreground)
        background = blended.convert("RGB")  # Convert back to RGB for text rendering

    # Prepare text
    text_lines = text.split("_")  # Split text by "_" for new lines

    # Load font
    font_path = os.path.join(os.path.dirname(__file__), "NotoSans-Regular.ttf")
    font_size = int(50 * font_scale)  # Adjust font size based on scale
    font = ImageFont.truetype(font_path, font_size)

    # Define text properties
    font_color = (255, 255, 255)  # White text
    margin = 100  # Margin from top
    line_height = font_size + 10  # Add spacing between lines

    # Calculate text height to position correctly
    draw = ImageDraw.Draw(background)

    wrapped_lines = []

    # Position text from the top downwards
    for line in text_lines:  # Draw from top to bottom
        # Measure text width and height
        text_width = draw.textlength(line, font=font)
        
        # Ensure text fits within image width (wrap text if too long)

        if text_width > w - 2 * margin:
            words = line.split(" ")
            temp_line = ""

            for word in words:
                temp_width = draw.textlength(temp_line + " " + word, font=font)
                if temp_width < w - 2 * margin:
                    temp_line += " " + word
                else:
                    wrapped_lines.append(temp_line.strip())
                    temp_line = word

            if temp_line:
                wrapped_lines.append(temp_line.strip())

        else:
            wrapped_lines.append(line)

    total_text_height = len(wrapped_lines) * line_height
    desired_center_y = 900
    y_position = desired_center_y - (total_text_height // 2)  

    for wrapped_line in wrapped_lines:
        temp_width = draw.textlength(wrapped_line, font=font)
        x_position = (w - temp_width) // 2  # Center align text
        y_position += line_height
        draw.text((x_position, y_position), wrapped_line, font=font, fill=font_color)
              # Move to the next line
        
        
    # Save the output image
    background.save(output_path)
