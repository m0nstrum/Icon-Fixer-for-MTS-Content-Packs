import os
import json
import re
import zipfile
import tempfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def handle_file(pack, file_name: str, sub_folders: list, assets_path: Path) -> None:

    file_base = file_name[:-4] if file_name.endswith(".png") else file_name

    textures_path_str = f"{pack}:{'/'.join(['item'] + sub_folders)}/{file_base}"
    json_data = {
        "parent": "mts:item/basic",
        "textures": {
            "layer0": textures_path_str
        }
    }

    model_dir = assets_path / "mts" / "models" / "item"
    model_dir.mkdir(parents=True, exist_ok=True)
    json_file_path = model_dir / f"{pack}.{file_base}.json"
    with open(json_file_path, "w") as f:
        json.dump(json_data, f, indent=2)

def handle_directory(pack, directory: Path, sub_folders: list, assets_path: Path) -> None:

    for entry in os.listdir(directory):
        entry_path = directory / entry
        if entry_path.is_file() and entry.endswith(".png"):
            handle_file(pack, entry, sub_folders, assets_path)
        elif entry_path.is_dir():
            handle_directory(pack, entry_path, sub_folders + [entry], assets_path)

def fix_mods_toml_file(mods_toml_path: Path) -> None:

    with open(mods_toml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_version(match: re.Match) -> str:
        prefix = match.group(1)
        version_value = match.group(2)
        suffix = match.group(3)
        fixed_version = re.sub(r'[A-Za-z]', '', version_value)
        return f'{prefix}{fixed_version}{suffix}'

    new_content = re.sub(
        r'(version\s*=\s*")([^"]+)(")',
        replace_version,
        content
    )

    with open(mods_toml_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def process_jar(input_jar_path: Path, fix_mods: bool = False) -> Path:

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(input_jar_path, 'r') as jar:
            jar.extractall(temp_path)

        assets_path = temp_path / "assets"
        if not assets_path.exists():
            raise Exception("No 'assets' folder in jar-file!")

        content_packs = [
            d for d in os.listdir(assets_path)
            if (assets_path / d).is_dir() and d != "mts"
        ]

        if content_packs:
            (assets_path / "mts" / "models" / "item").mkdir(parents=True, exist_ok=True)

        for pack in content_packs:
            pack_path = assets_path / pack
            textures_path = pack_path / "textures"
            if not textures_path.exists():
                continue

            items_directory = textures_path / "items"
            item_directory = textures_path / "item"

            if items_directory.exists():
                try:
                    os.rename(items_directory, item_directory)
                except Exception as e:
                    print(f"Can't rename {items_directory} to {item_directory}: {e}")

            if not item_directory.exists():
                continue

            handle_directory(pack, item_directory, [], assets_path)

        if fix_mods:
            meta_inf_path = temp_path / "META-INF"
            mods_toml_path = meta_inf_path / "mods.toml"
            if mods_toml_path.exists():
                try:
                    fix_mods_toml_file(mods_toml_path)
                except Exception as e:
                    print(f"Error while processing mods.toml: {e}")

        output_jar_path = input_jar_path.parent / (input_jar_path.stem + "_fixed.jar")

        with zipfile.ZipFile(output_jar_path, 'w', zipfile.ZIP_DEFLATED) as new_jar:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = str(file_path.relative_to(temp_path))
                    new_jar.write(file_path, arcname)

        return output_jar_path


def select_jar():
    file_path = filedialog.askopenfilename(
        title="Select jar-file",
        filetypes=[("Jar files", "*.jar"), ("All", "*.*")]
    )
    if file_path:
        jar_path_var.set(file_path)

def start_processing():
    jar_file = jar_path_var.get()
    if not jar_file:
        messagebox.showerror("Error", "Please, select jar-file.")
        return
    try:
        input_jar = Path(jar_file)
        fix_mods = fix_mods_var.get()
        output_jar = process_jar(input_jar, fix_mods)
        messagebox.showinfo("Success", f"File successfully processed!\nNew jar: {output_jar}")
    except Exception as e:
        messagebox.showerror("Error", f"Error:\n{e}")

root = tk.Tk()
root.title("Icon Fixer for MTS Content Packs (1.16.5 -> 1.20.1)")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

jar_path_var = tk.StringVar()

label = tk.Label(frame, text="Select jar-file:")
label.grid(row=0, column=0, sticky="w")

entry = tk.Entry(frame, textvariable=jar_path_var, width=50)
entry.grid(row=1, column=0, padx=5, pady=5)

button_browse = tk.Button(frame, text="Select...", command=select_jar)
button_browse.grid(row=1, column=1, padx=5, pady=5)

fix_mods_var = tk.BooleanVar()
check_fix_mods = tk.Checkbutton(frame, text="Fix mods.toml", variable=fix_mods_var)
check_fix_mods.grid(row=2, column=0, columnspan=2, pady=5, sticky="w")

button_process = tk.Button(frame, text="Process", command=start_processing)
button_process.grid(row=3, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root.mainloop()
