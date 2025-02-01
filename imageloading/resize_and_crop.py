import cv2
def resize_and_crop(image, target_width, target_height):
    h, w = image.shape[:2]

    # Compute scaling factors
    scale_w = target_width / w
    scale_h = target_height / h
    scale = max(scale_w, scale_h)  # Scale to fill the whole target area

    # Resize while maintaining aspect ratio
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(image, (new_w, new_h))

    # Compute center crop
    x_offset = (new_w - target_width) // 2
    y_offset = (new_h - target_height) // 2
    cropped = resized[y_offset:y_offset + target_height, x_offset:x_offset + target_width]

    return cropped
