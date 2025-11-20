import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk

# Create the main application window
root = tk.Tk()
root.title("Two Frames Side by Side")

def resize_image(image_path, max_size):
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

# Create the left Frame
left_frame = tk.Frame(root, width=200, height=200, bg='lightblue')
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

#Load the image
img = cv2.imread('./images/0%.jpg')

#Rearrange colors BGR -> RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
scale_factor = 1/4
img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor)
# cv2.imshow('hello', img)

# create tk image
im = Image.fromarray(img)
imgtk = ImageTk.PhotoImage(image=im)

# Add a label to the left Frame
left_label = tk.Label(left_frame, image=imgtk)
left_label.pack(pady=20)

# Add a button to the left Frame
left_button = tk.Button(left_frame, text="Left Button", command=lambda: print("Left Button clicked!"))
left_button.pack(pady=10)

# Create the right Frame
right_frame = tk.Frame(root, width=200, height=200, bg='lightgreen')
right_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Add a label to the right Frame
right_label = tk.Label(right_frame, text="Right Frame", bg='lightgreen')
right_label.pack(pady=20)

# Add a button to the right Frame
right_button = tk.Button(right_frame, text="Right Button", command=lambda: print("Right Button clicked!"))
right_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()