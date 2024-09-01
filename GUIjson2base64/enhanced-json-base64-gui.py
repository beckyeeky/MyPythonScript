import base64
import gzip
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import codecs

GLAMOURER_VERSION_BYTE = b'\x06'

def remove_bom(file_content):
    return file_content.lstrip('\ufeff')

def glamourer_encode(data):
    json_string = json.dumps(data)
    compressed_data = gzip.compress(json_string.encode('utf-8'))
    return base64.b64encode(GLAMOURER_VERSION_BYTE + compressed_data).decode('utf-8')

def standard_encode(data, compress=False):
    json_string = json.dumps(data)
    if compress:
        compressed_data = gzip.compress(json_string.encode('utf-8'))
        return base64.b64encode(compressed_data).decode('utf-8')
    else:
        return base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

def glamourer_decode(base64_data):
    decoded_data = base64.b64decode(base64_data)
    if decoded_data[0:1] != GLAMOURER_VERSION_BYTE:
        raise ValueError("Invalid Glamourer version byte")
    decompressed_data = gzip.decompress(decoded_data[1:]).decode('utf-8')
    return json.loads(decompressed_data)

def standard_decode(base64_data, compressed=False):
    decoded_data = base64.b64decode(base64_data)
    if compressed:
        decompressed_data = gzip.decompress(decoded_data).decode('utf-8')
    else:
        decompressed_data = decoded_data.decode('utf-8')
    return json.loads(decompressed_data)

def is_glamourer_encoded(base64_data):
    try:
        decoded_data = base64.b64decode(base64_data)
        return decoded_data[0:1] == GLAMOURER_VERSION_BYTE
    except:
        return False

def is_compressed(base64_data):
    try:
        decoded_data = base64.b64decode(base64_data)
        gzip.decompress(decoded_data)
        return True
    except:
        return False

def decode_and_decompress(base64_data):
    if is_glamourer_encoded(base64_data):
        return glamourer_decode(base64_data)
    elif is_compressed(base64_data):
        return standard_decode(base64_data, compressed=True)
    else:
        return standard_decode(base64_data, compressed=False)

def load_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if file_path:
        try:
            with codecs.open(file_path, 'r', 'utf-8-sig') as f:
                file_content = f.read()
                if not file_content.strip():
                    raise ValueError("The file is empty.")
                file_content = remove_bom(file_content)
                data = json.loads(file_content)
            
            json_text.delete('1.0', tk.END)
            json_text.insert(tk.END, json.dumps(data, indent=4))
            encode_and_update()
            encoding_status.set("JSON file loaded successfully")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format: {str(e)}")
            encoding_status.set("Error: Invalid JSON format")
        except ValueError as e:
            messagebox.showerror("File Error", str(e))
            encoding_status.set("Error: Empty file")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            encoding_status.set("Error: Failed to load file")

def save_json_file():
    json_data = json_text.get('1.0', tk.END).strip()
    try:
        data = json.loads(json_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", "File saved successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def encode_and_update(*args):
    json_data = json_text.get('1.0', tk.END).strip()
    encoding_type = encoding_var.get()
    try:
        data = json.loads(json_data)
        if encoding_type == "Glamourer":
            encoded_data = glamourer_encode(data)
        elif encoding_type == "Base64 (Compressed)":
            encoded_data = standard_encode(data, compress=True)
        else:  # "Base64 (Uncompressed)"
            encoded_data = standard_encode(data, compress=False)
        
        base64_text.delete('1.0', tk.END)
        base64_text.insert(tk.END, encoded_data)
        encoding_status.set(f"Encoded: {encoding_type}")
    except json.JSONDecodeError:
        base64_text.delete('1.0', tk.END)
        base64_text.insert(tk.END, "Invalid JSON")
        encoding_status.set("Error: Invalid JSON")
    except Exception as e:
        base64_text.delete('1.0', tk.END)
        base64_text.insert(tk.END, f"Error: {str(e)}")
        encoding_status.set("Error: Encoding failed")

def decode_and_update(*args):
    base64_data = base64_text.get('1.0', tk.END).strip()
    try:
        decoded_data = decode_and_decompress(base64_data)
        json_text.delete('1.0', tk.END)
        json_text.insert(tk.END, json.dumps(decoded_data, indent=4))
        if is_glamourer_encoded(base64_data):
            encoding_status.set("Decoded: Glamourer")
        elif is_compressed(base64_data):
            encoding_status.set("Decoded: Base64 (Compressed)")
        else:
            encoding_status.set("Decoded: Base64 (Uncompressed)")
    except Exception as e:
        json_text.delete('1.0', tk.END)
        json_text.insert(tk.END, f"Error: {str(e)}")
        encoding_status.set("Error: Decoding failed")

# GUI setup
root = tk.Tk()
root.title("JSON Base64 Encoder/Decoder with Glamourer Support")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# JSON tab
json_frame = ttk.Frame(notebook)
notebook.add(json_frame, text="JSON")

json_text = tk.Text(json_frame, wrap='word', height=10, width=60)
json_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Encoding options
encoding_frame = ttk.Frame(json_frame)
encoding_frame.pack(fill=tk.X, padx=5, pady=5)

encoding_var = tk.StringVar(value="Glamourer")
encoding_label = ttk.Label(encoding_frame, text="Encoding:")
encoding_label.pack(side=tk.LEFT)
encoding_menu = ttk.Combobox(encoding_frame, textvariable=encoding_var, 
                             values=["Glamourer", "Base64 (Compressed)", "Base64 (Uncompressed)"])
encoding_menu.pack(side=tk.LEFT, padx=5)
encoding_menu.bind('<<ComboboxSelected>>', encode_and_update)

encode_button = ttk.Button(encoding_frame, text="Encode", command=encode_and_update)
encode_button.pack(side=tk.LEFT, padx=5)

# Base64 tab
base64_frame = ttk.Frame(notebook)
notebook.add(base64_frame, text="Base64")

base64_text = tk.Text(base64_frame, wrap='word', height=10, width=60)
base64_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

decode_button = ttk.Button(base64_frame, text="Decode", command=decode_and_update)
decode_button.pack(pady=5)

# Status bar
status_frame = ttk.Frame(root)
status_frame.pack(fill=tk.X, padx=10, pady=5)

encoding_status = tk.StringVar(value="Ready")
status_label = ttk.Label(status_frame, text="Status:")
status_label.pack(side=tk.LEFT)
status_value = ttk.Label(status_frame, textvariable=encoding_status)
status_value.pack(side=tk.LEFT)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

load_button = tk.Button(button_frame, text="Load JSON File", command=load_json_file)
load_button.pack(side=tk.LEFT, padx=5)

save_button = tk.Button(button_frame, text="Save JSON File", command=save_json_file)
save_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
