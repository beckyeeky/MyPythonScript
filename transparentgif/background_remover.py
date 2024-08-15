import os
import sys
from PIL import Image, ImageSequence, ImageFilter

def get_background_color(image, tolerance=0):
    """Determine the background color of an image."""
    image = image.convert("RGB")
    colors = image.getcolors(image.width * image.height)
    return max(colors, key=lambda x: x[0])[1]

def remove_background(image, background_color, tolerance=10):
    """Remove the background from an image."""
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []
    for item in data:
        if all(abs(item[i] - background_color[i]) <= tolerance for i in range(3)):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image

def smooth_edges(image, iterations=1):
    """Smooth the edges of the image to reduce jaggedness."""
    for _ in range(iterations):
        alpha = image.split()[3]
        alpha = alpha.filter(ImageFilter.SMOOTH)
        image.putalpha(alpha)
    return image

def crop_image(image):
    """Crop the image to remove excess transparent space."""
    bbox = image.getbbox()
    return image.crop(bbox) if bbox else image

def process_image(input_path, output_path=None, tolerance=10, crop=True, smooth=True):
    """Process a single image file."""
    if output_path is None:
        directory, filename = os.path.split(input_path)
        name, ext = os.path.splitext(filename)
        if ext.lower() == '.gif':
            output_path = os.path.join(directory, f"{name}_transparent{ext}")
        else:
            output_path = os.path.join(directory, f"{name}_transparent.png")
    
    try:
        with Image.open(input_path) as im:
            if input_path.lower().endswith('.gif'):
                frames = []
                durations = []
                background_color = get_background_color(im.convert("RGB"), tolerance)
                for frame in ImageSequence.Iterator(im):
                    processed_frame = remove_background(frame, background_color, tolerance)
                    if smooth:
                        processed_frame = smooth_edges(processed_frame, 2)
                    if crop:
                        processed_frame = crop_image(processed_frame)
                    frames.append(processed_frame)
                    durations.append(frame.info.get('duration', 100))
                frames[0].save(output_path, save_all=True, append_images=frames[1:], 
                               loop=0, duration=durations, disposal=2, format="GIF")
            else:
                background_color = get_background_color(im, tolerance)
                processed_image = remove_background(im, background_color, tolerance)
                if smooth:
                    processed_image = smooth_edges(processed_image, 2)
                if crop:
                    processed_image = crop_image(processed_image)
                processed_image.save(output_path, "PNG")
        
        return output_path  # 返回输出文件路径
    except Exception as e:
        return f"Error: {str(e)}"  # 返回错误信息

def process_directory(directory_path, tolerance=10, crop=True, smooth=True):
    """Process all supported image files in a directory."""
    supported_formats = ('.png', '.jpg', '.jpeg', '.gif')
    processed_files = []
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(directory_path, filename)
            result = process_image(input_path, tolerance=tolerance, crop=crop, smooth=smooth)
            processed_files.append(result)
    return processed_files

def print_usage():
    """Print usage instructions."""
    print("Usage: python background_remover.py <input_path> [tolerance] [nocrop] [nosmooth]")
    print("  <input_path>: Path to input image or directory")
    print("  [tolerance]: Optional color tolerance value (default: 10)")
    print("  [nocrop]: Include this to disable cropping")
    print("  [nosmooth]: Include this to disable edge smoothing")
    print("\nSupported image formats: PNG, JPG, JPEG, GIF")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
    else:
        input_path = sys.argv[1]
        tolerance = 10
        crop = True
        smooth = True
        
        for arg in sys.argv[2:]:
            if arg.isdigit():
                tolerance = int(arg)
            elif arg.lower() == 'nocrop':
                crop = False
            elif arg.lower() == 'nosmooth':
                smooth = False
        
        if os.path.isfile(input_path):
            result = process_image(input_path, tolerance=tolerance, crop=crop, smooth=smooth)
            print(result)
        elif os.path.isdir(input_path):
            results = process_directory(input_path, tolerance=tolerance, crop=crop, smooth=smooth)
            for result in results:
                print(result)
        else:
            print(f"Error: {input_path} is not a valid file or directory.")