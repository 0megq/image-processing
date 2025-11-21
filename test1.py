import tkinter as tk
import numpy as np
import cv2
from PIL import Image, ImageTk

class DisplayFrame(tk.Frame):
	def __init__(self, parent):
		width = 800
		height = 600
		super().__init__(parent, width=width, height=height, bg='lightblue')
		self.right = 0
		self.pack_propagate(False)
		self.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
		self.bind("<Configure>", self.on_resize)

		#Load the image
		self.src_img = cv2.imread('./images/0%.jpg')

		#Rearrange colors BGR -> RGB
		self.src_img = cv2.cvtColor(self.src_img, cv2.COLOR_BGR2RGB)
		self.scale_factor = (height) / self.src_img.shape[0]
		img = cv2.resize(self.src_img, None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_AREA)
		# cv2.imshow('hello', img)

		# create tk image
		im = Image.fromarray(img)
		self.imgtk = ImageTk.PhotoImage(image=im)

		# Add a label to the left Frame
		self.img_label = tk.Label(self, image=self.imgtk, bg='lightblue')
		self.img_label.pack()
		self.img_label.bind("<Motion>", self.on_img_mouse_move)
		# self.img_label.bind("<Enter>", self.on_img_entered)
		# self.img_label.bind("<Leave>", self.on_img_exited)

		# Add a button to the left Frame
		# left_button = tk.Button(self, text="Left Button", command=lambda: print("Left Button clicked!"))
		# left_button.pack(pady=10)

	def on_resize(self, event):
		width = event.width
		height = event.height
	
		self.scale_factor = (height) / self.src_img.shape[0]
		img = cv2.resize(self.src_img, None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_AREA)

		# create tk image
		im = Image.fromarray(img)
		self.imgtk = ImageTk.PhotoImage(image=im)
		self.img_label.configure(image=self.imgtk)
		self.right.size_lbl.config(text="Size: %d x %d" % (self.src_img.shape[1], self.src_img.shape[0]))

	def on_img_mouse_move(self, event):
		self.right.mouse_pos_lbl.config(text="Mouse Pos: (%d, %d)" % (event.x / self.scale_factor, event.y / self.scale_factor))


	# def adjust_zoom(self):



class UIFrame(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent, width=150, height=200, bg='lightgreen')
		# Create the right Frame
		self.pack_propagate(False)
		self.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH)

		# Add a label to the right Frame
		right_label = tk.Label(self, text="Controls", bg='lightgreen')
		right_label.pack(pady=5, side="top")

		# Add a button to the right Frame
		right_button = tk.Button(self, text="Right Button", command=lambda: print("Right Button clicked!"))
		right_button.pack(pady=10, padx=10)
		
		self.size_lbl = tk.Label(self, text="Image size: ", bg='lightgreen')
		self.size_lbl.pack(padx=5, side="bottom", anchor="w")
		self.mouse_pos_lbl = tk.Label(self, text="Mouse Pos: ", bg='lightgreen')
		self.mouse_pos_lbl.pack(pady=5, padx=5, side="bottom", anchor="w")
	

# Create the main application window
root = tk.Tk()
root.title("Tube Helper")

left_frame = DisplayFrame(root)
right_frame = UIFrame(root)
left_frame.right = right_frame

# Start the Tkinter event loop
root.mainloop()