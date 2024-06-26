import os
import subprocess

def convert_webp_to_correct_format():
    input_folder = os.getcwd()  # 获取当前工作目录
    output_folder = os.path.join(input_folder, 'output')  # 创建输出文件夹路径

    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".webp"):
            input_path = os.path.join(input_folder, filename)
            
            # 识别文件类型
            file_type = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
                capture_output=True, text=True
            ).stdout.strip()
            
            if file_type == 'vp8' or file_type == 'vp9':
                # 是WebM视频文件，转换为GIF
                output_path = os.path.join(output_folder, filename.replace(".webp", ".gif"))
                subprocess.run(['ffmpeg', '-i', input_path, output_path])
                print(f"转换完成: {filename} -> {output_path}")
            else:
                # 只是WebP图片文件，直接复制到输出文件夹
                output_path = os.path.join(output_folder, filename)
                os.rename(input_path, output_path)
                print(f"复制完成: {filename} -> {output_path}")

convert_webp_to_correct_format()
