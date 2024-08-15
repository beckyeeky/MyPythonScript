import os
import sys
from PIL import Image, ImageSequence

def get_background_color(image, tolerance=0):
    """
    Determine the background color of an image.
    
    :param image: PIL Image object
    :param tolerance: Color tolerance value
    :return: "black" or "white"
    """
    image = image.convert("RGB")
    datas = image.getdata()
    black_count = sum(1 for item in datas if all(v < tolerance for v in item))
    white_count = sum(1 for item in datas if all(v > 255 - tolerance for v in item))
    return "black" if black_count > white_count else "white"

def remove_background(image, background_color, tolerance=0):
    """
    Remove the background from an image.
    
    :param image: PIL Image object
    :param background_color: "black" or "white"
    :param tolerance: Color tolerance value
    :return: Processed PIL Image object
    """
    image = image.convert("RGBA")
    datas = image.getdata()
    new_data = []
    for item in datas:
        if background_color == "black":
            new_data.append((255, 255, 255, 0) if all(v < tolerance for v in item[:3]) else item)
        else:  # white background
            new_data.append((255, 255, 255, 0) if all(v > 255 - tolerance for v in item[:3]) else item)
    image.putdata(new_data)
    return image

def crop_image(image):
    """
    Crop the image to remove excess transparent space.
    
    :param image: PIL Image object
    :return: Cropped PIL Image object
    """
    bbox = image.getbbox()
    if bbox:
        return image.crop(bbox)
    return image

def process_image(input_path, output_path, tolerance=0, crop=False):
    """
    Process a single image file.
    
    :param input_path: Path to input image
    :param output_path: Path to save processed image
    :param tolerance: Color tolerance value
    :param crop: Whether to crop the image after processing
    """
    with Image.open(input_path) as im:
        if input_path.lower().endswith('.gif'):
            frames = []
            durations = []
            background_color = get_background_color(im.convert("RGB"), tolerance)
            for frame in ImageSequence.Iterator(im):
                processed_frame = remove_background(frame, background_color, tolerance)
                if crop:
                    processed_frame = crop_image(processed_frame)
                frames.append(processed_frame)
                durations.append(frame.info.get('duration', 100))
            frames[0].save(output_path, save_all=True, append_images=frames[1:], 
                           loop=0, duration=durations, disposal=2, format="GIF")
        else:
            background_color = get_background_color(im, tolerance)
            processed_image = remove_background(im, background_color, tolerance)
            if crop:
                processed_image = crop_image(processed_image)
            # Ensure static images are saved as PNG
            output_path = os.path.splitext(output_path)[0] + '.png'
            processed_image.save(output_path, "PNG")

def process_directory(directory_path, output_directory, tolerance=0, crop=False):
    """
    Process all supported image files in a directory.
    
    :param directory_path: Path to input directory
    :param output_directory: Path to output directory
    :param tolerance: Color tolerance value
    :param crop: Whether to crop the images after processing
    """
    os.makedirs(output_directory, exist_ok=True)
    supported_formats = ('.png', '.jpg', '.jpeg', '.gif')
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(directory_path, filename)
            output_path = os.path.join(output_directory, f"processed_{filename}")
            print(f"Processing {input_path}")
            process_image(input_path, output_path, tolerance, crop)

def print_usage():
    """Print usage instructions."""
    print("Usage: python script.py <input_path> <output_path> [tolerance] [crop]")
    print("  <input_path>: Path to input image or directory")
    print("  <output_path>: Path to output image or directory")
    print("  [tolerance]: Optional color tolerance value (default: 0)")
    print("  [crop]: Optional flag to crop excess transparent space (use 'crop' to enable)")
    print("\nSupported image formats: PNG, JPG, JPEG, GIF")
    print("Note: Static images will be output as PNG, GIFs will remain as GIF")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print_usage()
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        tolerance = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        crop = 'crop' in sys.argv

        if os.path.isfile(input_path):
            process_image(input_path, output_path, tolerance, crop)
        elif os.path.isdir(input_path):
            process_directory(input_path, output_path, tolerance, crop)
        else:
            print(f"Error: {input_path} is not a valid file or directory.")
            print_usage()