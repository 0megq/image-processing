import tkinter as tk
from tkinter import filedialog

root = tk.Tk(); root.withdraw()  # hide main window
directory = filedialog.askdirectory(title="Select a directory", initialdir=".")
if directory:
    print("Selected directory:", directory)
else:
    print("No directory selected")