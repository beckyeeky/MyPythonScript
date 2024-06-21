# ClipboardNumberStepper.py
# 这个脚本用于修改剪贴板中的数字，每次步进1，直到剪贴板中的数字达到用户指定的终点值时停止。
# Custom Unicode字符保留原样。
# pip install pyperclip

# 导入所需的库
import pyperclip
import re
import time

# 定义一个函数来步进数字
def increment_numbers_in_clipboard(target_value):
    while True:
        # 获取剪贴板中的文本
        text = pyperclip.paste()

        # 定义一个用于匹配数字的正则表达式
        number_pattern = re.compile(r'\d+')

        # 使用正则表达式找到文本中的所有数字
        numbers = number_pattern.findall(text)

        # 如果没有找到数字，则返回
        if not numbers:
            print("剪贴板中没有数字。")
            return

        # 标志变量，用于检查是否有数字达到了终点值
        reached_target = False

        # 遍历所有找到的数字
        for number in numbers:
            # 将数字转换为整数并步进1
            incremented_number = int(number) + 1

            # 用步进后的数字替换原来的数字
            text = text.replace(number, str(incremented_number), 1)

            # 将修改后的文本重新写入剪贴板
            pyperclip.copy(text)

            # 打印当前剪贴板内容
            print(f"当前剪贴板内容: {text}")

            # 如果步进后的数字等于目标值，则停止
            if incremented_number == target_value:
                reached_target = True
                break

        # 如果已经达到了目标值，则退出循环
        if reached_target:
            print(f"数字已经变成{target_value}，停止步进。")
            return

        # 延迟一秒钟，以便于观察变化
        time.sleep(1)

if __name__ == "__main__":
    # 获取用户指定的终点值
    target_value = int(input("请输入要步进到的终点值: "))

    while True:
        # 每次运行脚本时等待用户确认
        input("请将文本复制到剪贴板后按回车键继续...")
        
        # 调用函数处理剪贴板中的数字
        increment_numbers_in_clipboard(target_value)

        # 提示用户处理完成
        print("处理完成。如果需要再次运行，请重新复制文本并按回车键。")
