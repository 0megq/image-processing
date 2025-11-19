import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk

def resize_image(image_path, max_size):
    with Image.open(image_path) as img:
        img.thumbnail(max_size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    
#Create an instance of tkinter frame
root = tk.Tk()
root.geometry("1200x800+200+200")
root.title("Tube Helper")

#Load the image
img = cv2.imread('images/0%.jpg')

#Rearrange colors BGR -> RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# create tk image
im = Image.fromarray(img)
imgtk = ImageTk.PhotoImage(image=im)

#Create a Label to display the image
label = tk.Label(root, image= imgtk).pack()

# Close button
button = tk.Button(root, text="Close", command=root.quit)
button.pack()

root.mainloop()