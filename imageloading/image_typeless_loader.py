import glob

# Find the first image in the directory
def typeless_loader(image_name):
    image_name +=".*"
    image_files = glob.glob(image_name)  # Matches "background.png", "background.jpg", etc.
    if image_files:
        image_path = image_files[0]
        return image_path
    else:
        raise FileNotFoundError("No background image found with any known extension.")
def main():
    image_path = typeless_loader("background")
    print(image_path)

if __name__ == "__main__":
    main()
