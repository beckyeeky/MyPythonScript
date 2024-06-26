import os
from PIL import Image, ImageSequence

def get_background_color(image, tolerance=0):
    image = image.convert("RGB")
    datas = image.getdata()

    black_count = 0
    white_count = 0

    for item in datas:
        if item[0] < tolerance and item[1] < tolerance and item[2] < tolerance:
            black_count += 1
        elif item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
            white_count += 1

    if black_count > white_count:
        return "black"
    else:
        return "white"

def remove_background(image_path, output_path, background_color, tolerance=0):
    im = Image.open(image_path)
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(im):
        frame = frame.convert("RGBA")
        datas = frame.getdata()

        new_data = []
        for item in datas:
            if background_color == "black":
                if item[0] < tolerance and item[1] < tolerance and item[2] < tolerance:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            elif background_color == "white":
                if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)

        frame.putdata(new_data)
        frames.append(frame)
        durations.append(frame.info.get('duration', 100))

    frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=durations, disposal=2)

def process_directory(directory_path, tolerance=0):
    for filename in os.listdir(directory_path):
        if filename.endswith(".gif"):
            file_path = os.path.join(directory_path, filename)
            print(f"Processing {file_path}")
            im = Image.open(file_path)
            background_color = get_background_color(next(ImageSequence.Iterator(im)), tolerance)
            remove_background(file_path, file_path, background_color, tolerance)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script.py <directory_path> [tolerance]")
    else:
        directory_path = sys.argv[1]
        tolerance = int(sys.argv[2]) if len(sys.argv) == 3 else 0
        process_directory(directory_path, tolerance)
