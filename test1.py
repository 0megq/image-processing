import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk

class DisplayFrame(tk.Frame):
	def __init__(self, parent):
		width = 400
		height = 400
		super().__init__(parent, width=width, height=height, bg='lightblue')
		
		self.pack_propagate(False)
		self.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
		self.bind("<Configure>", self.on_resize)

		#Load the image
		self.src_img = cv2.imread('./images/0%.jpg')

		#Rearrange colors BGR -> RGB
		self.src_img = cv2.cvtColor(self.src_img, cv2.COLOR_BGR2RGB)
		scale_factor = (width - 20) / self.src_img.shape[1]
		img = cv2.resize(self.src_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
		# cv2.imshow('hello', img)

		# create tk image
		im = Image.fromarray(img)
		imgtk = ImageTk.PhotoImage(image=im)

		# Add a label to the left Frame
		self.img_label = tk.Label(self, image=imgtk)
		self.img_label.pack(pady=20)

		# Add a button to the left Frame
		left_button = tk.Button(self, text="Left Button", command=lambda: print("Left Button clicked!"))
		left_button.pack(pady=10)

	def on_resize(self, event):
		width = event.width
		height = event.height
	
		scale_factor = (width - 20) / self.src_img.shape[1]
		img = cv2.resize(self.src_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

		# create tk image
		im = Image.fromarray(img)
		imgtk = ImageTk.PhotoImage(image=im)
		self.img_label


class UIFrame(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent, width=200, height=200, bg='lightgreen')
		# Create the right Frame
		self.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)

		# Add a label to the right Frame
		right_label = tk.Label(self, text="Right Frame", bg='lightgreen')
		right_label.pack(pady=20)

		# Add a button to the right Frame
		right_button = tk.Button(self, text="Right Button", command=lambda: print("Right Button clicked!"))
		right_button.pack(pady=10)
	

# Create the main application window
root = tk.Tk()
root.title("Tube Helper")

left_frame = DisplayFrame(root)
right_frame = UIFrame(root)

# Start the Tkinter event loop
root.mainloop()