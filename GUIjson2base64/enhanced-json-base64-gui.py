import base64
import gzip
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

GLAMOURER_HEADER = b'\x06'

def glamourer_encode(data):
    json_data = json.dumps(data)
    compressed_data = gzip.compress(json_data.encode('utf-8'))
    return base64.b64encode(GLAMOURER_HEADER + compressed_data).decode('utf-8')

def glamourer_decode(base64_data):
    decoded_data = base64.b64decode(base64_data)
    if decoded_data[0:1] != GLAMOURER_HEADER:
        raise ValueError("Invalid Glamourer header")
    decompressed_data = gzip.decompress(decoded_data[1:]).decode('utf-8')
    return json.loads(decompressed_data)

def is_glamourer_encoded(base64_data):
    try:
        decoded_data = base64.b64decode(base64_data)
        return decoded_data[0:1] == GLAMOURER_HEADER
    except:
        return False

def compress_and_encode(data):
    json_data = json.dumps(data)
    compressed_data = gzip.compress(json_data.encode('utf-8'))
    return base64.b64encode(compressed_data).decode('utf-8')

def encode_without_compression(data):
    json_data = json.dumps(data)
    return base64.b64encode(json_data.encode('utf-8')).decode('utf-8')

def is_gzip_compressed(base64_data):
    try:
        decoded_data = base64.b64decode(base64_data)
        gzip.decompress(decoded_data)
        return True
    except:
        return False

def decode_and_decompress(base64_data):
    if is_glamourer_encoded(base64_data):
        return glamourer_decode(base64_data)
    decoded_data = base64.b64decode(base64_data)
    if is_gzip_compressed(base64_data):
        decompressed_data = gzip.decompress(decoded_data).decode('utf-8')
    else:
        decompressed_data = decoded_data.decode('utf-8')
    return json.loads(decompressed_data)

def load_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as f:
            data = json.load(f)
        encoded_data = glamourer_encode(data)
        base64_text.delete('1.0', tk.END)
        base64_text.insert(tk.END, encoded_data)
        update_preview()

def save_json_file():
    base64_data = base64_text.get('1.0', tk.END).strip()
    try:
        data = decode_and_decompress(base64_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", "File saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def update_preview(*args):
    base64_data = base64_text.get('1.0', tk.END).strip()
    try:
        data = decode_and_decompress(base64_data)
        preview_text.delete('1.0', tk.END)
        preview_text.insert(tk.END, json.dumps(data, indent=4))
        if is_glamourer_encoded(base64_data):
            compression_status.set("Glamourer Encoded")
        elif is_gzip_compressed(base64_data):
            compression_status.set("Compressed")
        else:
            compression_status.set("Not compressed")
    except:
        preview_text.delete('1.0', tk.END)
        preview_text.insert(tk.END, "Invalid Base64 or JSON data")
        compression_status.set("Unknown")

# GUI setup (unchanged)
root = tk.Tk()
root.title("Enhanced JSON Base64 Encoder/Decoder with Glamourer Support")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

base64_frame = ttk.Frame(notebook)
notebook.add(base64_frame, text="Base64")

base64_text = tk.Text(base64_frame, wrap='word', height=10, width=60)
base64_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
base64_text.bind('<KeyRelease>', update_preview)

preview_frame = ttk.Frame(notebook)
notebook.add(preview_frame, text="Preview")

preview_text = tk.Text(preview_frame, wrap='word', height=10, width=60)
preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

status_frame = ttk.Frame(root)
status_frame.pack(fill=tk.X, padx=10, pady=5)

compression_status = tk.StringVar(value="Unknown")
status_label = ttk.Label(status_frame, text="Encoding status:")
status_label.pack(side=tk.LEFT)
status_value = ttk.Label(status_frame, textvariable=compression_status)
status_value.pack(side=tk.LEFT)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

load_button = tk.Button(button_frame, text="Load JSON File", command=load_json_file)
load_button.pack(side=tk.LEFT, padx=5)

save_button = tk.Button(button_frame, text="Save JSON File", command=save_json_file)
save_button.pack(side=tk.LEFT, padx=5)

root.mainloop()