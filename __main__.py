from dataclasses import dataclass, field
from pathlib import Path
import sys
from threading import Thread
import tkinter as tk
from tkinter import filedialog
from typing import List

from file_drag_drop import do_drag_drop

@dataclass
class Settings:
    root_directory: str = ""
    file_types: List[str] = field(default_factory=lambda: ["m4a", "mp3", "mp4", "wav", "flac", "ogg"])

def run_gui(settings: Settings):
    root = tk.Tk()
    listbox = tk.Listbox(root)
    listbox.pack(side=tk.LEFT, fill = tk.BOTH, expand=1)
    scrollbar = tk.Scrollbar(listbox)
    scrollbar.pack(side =tk.RIGHT, fill = tk.BOTH)
    listbox.config(yscrollcommand = scrollbar.set)
    scrollbar.config(command = listbox.yview)
    B = tk.Button(root, text ="Loading...", state=tk.DISABLED)
    B.pack(side=tk.RIGHT)

    def load_files():
        path = Path(settings.root_directory)
        files = [str(file) for suffix in settings.file_types for file in path.rglob("*." + suffix)]
        listbox.insert(tk.END, *files)
        B.configure(state=tk.NORMAL, text=f"{len(files)} files")
        B.bind("<ButtonPress-1>", lambda _: do_drag_drop(files))

    Thread(target=load_files).start()
    root.mainloop()

if __name__ == "__main__":
    root_directory = filedialog.askdirectory()
    if not root_directory:
        sys.exit()
    settings = Settings(root_directory=root_directory)
    run_gui(settings)
