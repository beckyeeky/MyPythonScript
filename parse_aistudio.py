import json
import base64
import os
import argparse
import glob
import sys

def parse_ai_studio_json(json_file_path, output_image_dir):
    """
    解析单个 AI Studio JSON 文件
    """
    if not os.path.exists(json_file_path):
        print(f"❌ 跳过：文件不存在 -> {json_file_path}")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取错误 ({json_file_path}): {e}")
        return

    # 兼容两种结构
    chunks = data.get('chunkedPrompt', {}).get('chunks', [])
    if not chunks:
        chunks = data.get('contents', [])

    if not chunks:
        print(f"⚠️  跳过：{os.path.basename(json_file_path)} (未找到对话数据)")
        return

    print(f"🚀 正在处理: {os.path.basename(json_file_path)}")
    
    image_count = 0
    safe_basename = os.path.splitext(os.path.basename(json_file_path))[0]

    for index, chunk in enumerate(chunks):
        # 提取 Base64 图片逻辑
        inline_images = []
        if 'inlineImage' in chunk:
            inline_images.append(chunk['inlineImage'])
        if 'parts' in chunk:
            for part in chunk['parts']:
                if 'inline_data' in part: inline_images.append(part['inline_data'])
                elif 'inlineData' in part: inline_images.append(part['inlineData'])

        for img_data in inline_images:
            b64_str = img_data.get('data', '')
            mime = img_data.get('mimeType', 'image/jpeg')
            if b64_str:
                ext = 'png' if 'png' in mime.lower() else 'jpg'
                # 文件名：原文件名_img_序号.jpg
                out_name = f"{safe_basename}_img_{index}_{image_count}.{ext}"
                out_path = os.path.join(output_image_dir, out_name)
                
                try:
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(b64_str))
                    print(f"   └── 🖼️  保存图片: {out_name}")
                    image_count += 1
                except:
                    pass
    
    if image_count == 0:
        print("   └── (无图片)")
    else:
        print(f"   └── ✅ 提取了 {image_count} 张图片")
    print("-" * 40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Studio JSON 批量解析工具 (支持通配符)")
    
    # 修改点 1: nargs='+' 表示接收一个或多个文件
    parser.add_argument("files", nargs='+', help="JSON 文件路径，支持通配符如 *.json")
    parser.add_argument("-o", "--output", default="output_images", help="图片保存目录")

    args = parser.parse_args()

    # 创建输出目录
    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)

    # 修改点 2: 处理通配符 (Windows 兼容核心逻辑)
    all_files = []
    for path_str in args.files:
        # 如果包含通配符，使用 glob 展开
        if any(c in path_str for c in ['*', '?', '[']):
            matched = glob.glob(path_str)
            if matched:
                all_files.extend(matched)
            else:
                print(f"⚠️  警告: 通配符 '{path_str}' 未匹配到任何文件")
        else:
            # 普通文件路径直接添加
            all_files.append(path_str)

    # 去重并排序
    all_files = sorted(list(set(all_files)))

    if not all_files:
        print("❌ 未找到任何文件，请检查路径。")
    else:
        print(f"📂 图片将保存至: {args.output}")
        print(f"🔍 共找到 {len(all_files)} 个文件，开始处理...\n" + "="*40)
        
        for file_path in all_files:
            parse_ai_studio_json(file_path, args.output)
            
        print("\n🎉 全部处理完成！")