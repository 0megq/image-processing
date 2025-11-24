import tkinter as tk
from tkinter import filedialog

root = tk.Tk(); root.withdraw()
files = filedialog.askopenfilenames(title="Select one or more files", initialdir=".", filetypes=[("All files","*.*")])
if files:
    for f in files:
        print(f)
else:
    print("No files selected")