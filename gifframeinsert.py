from PIL import Image, ImageSequence
import sys

def insert_frames(input_path, output_path, factor=2):
    # Read GIF file
    original_gif = Image.open(input_path)
    frames = [frame.convert('RGBA') for frame in ImageSequence.Iterator(original_gif)]
    
    # Insert frames
    new_frames = []
    for i in range(len(frames) - 1):
        new_frames.append(frames[i])
        for j in range(1, factor):
            alpha = j / factor
            interpolated_frame = Image.blend(frames[i], frames[i + 1], alpha)
            new_frames.append(interpolated_frame)
    new_frames.append(frames[-1])
    
    # Save new GIF
    new_frames[0].save(output_path, save_all=True, append_images=new_frames[1:], loop=0, duration=original_gif.info['duration'] // factor)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py input.gif output.gif factor")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        factor = int(sys.argv[3])
        insert_frames(input_path, output_path, factor)
