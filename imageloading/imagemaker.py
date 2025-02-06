import cv2
import numpy as np
from imageloading.resize_and_crop import resize_and_crop


def overlay_images(background_path, foreground_path, output_path, text, font_scale=2.5, thickness=2):
    # Load images
    background = cv2.imread(background_path)
    foreground = cv2.imread(foreground_path, cv2.IMREAD_UNCHANGED)  # Keep alpha
    if background is None:
        print("input image hasn't loaded")
    if foreground is None:
        print("frame image didn't load")

    h, w = foreground.shape[:2]

    background = resize_and_crop(background, w, h)
    # If foreground has alpha channel, blend it with the background
    if foreground.shape[2] == 4:
        alpha_channel = foreground[:, :, 3] / 255.0
        foreground = foreground[:, :, :3]  # Remove alpha

        for c in range(3):  # Blend each channel (R, G, B)
            background[:, :, c] = (1 - alpha_channel) * background[:, :, c] + alpha_channel * foreground[:, :, c]

    # Prepare text
    text_lines = text.split("_")  # Split text by "_" for new lines

    # Define text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_thickness = thickness
    font_color = (255, 255, 255)  # White text
    margin = 100  # Margin from bottom

    # Calculate text height to position correctly
    text_size = cv2.getTextSize("A", font, font_scale, font_thickness)[0]  # Get height of a single character
    line_height = text_size[1] + 10  # Add spacing between lines

    # Position text from the bottom upwards
    y_position = 840  # Start from the bottom
    for line in text_lines:  # Draw from bottom to top
        text_width, text_height = cv2.getTextSize(line, font, font_scale, font_thickness)[0]

        # Ensure text fits within image width (wrap text if too long)
        if text_width > w - 2 * margin:
            words = line.split(" ")
            wrapped_lines = []
            temp_line = ""

            for word in words:
                temp_size = cv2.getTextSize(temp_line + " " + word, font, font_scale, font_thickness)[0][0]
                if temp_size < w - 2 * margin:
                    temp_line += " " + word
                else:
                    wrapped_lines.append(temp_line.strip())
                    temp_line = word

            if temp_line:
                wrapped_lines.append(temp_line.strip())

            for wrapped_line in (wrapped_lines):
                text_width, _ = cv2.getTextSize(wrapped_line, font, font_scale, font_thickness)[0]
                x_position = (w - text_width) // 2  # Center align text
                y_position += line_height
                cv2.putText(background, wrapped_line, (x_position, y_position), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        
        else:
            x_position = (w - text_width) // 2  # Center align text
            y_position += line_height
            cv2.putText(background, line, (x_position, y_position), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

    # Save and display the output image
    cv2.imwrite(output_path, background)

# Example Usage
# background = typeless_loader("background")
# overlay_images(background, "foreground.png", "output.png", "is it??? ")

