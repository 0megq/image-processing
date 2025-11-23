import tkinter as tk
import numpy as np
import pandas as pd
import cv2
from PIL import Image, ImageTk
from typing import Tuple

DOT_RADIUS = 3

class ImageData:
	def __init__(self, bgr):
		self.src = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
		self.edges = 0
		self.aspect = self.src.shape[1] / self.src.shape[0]
		self.points = [(-1, -1)] * 4

	def calculate_edges(self, thresh1, thresh2):
		print(thresh1, thresh2)
		grayScale = cv2.cvtColor(self.src, cv2.COLOR_RGB2GRAY)
		blurred = cv2.GaussianBlur(grayScale, (5,5), 1.4)
		self.edges = cv2.Canny(blurred, float(thresh1), float(thresh2))

	
	def get_src_with_edges(self):
		res = self.src.copy()
		edge_y, edge_x = np.where(self.edges == 255)
		res[edge_y, edge_x] = (0, 255, 0)
		return res

	def get_src_with_edges_and_points(self):
		res = self.get_src_with_edges()
		for point in self.points:
			if point == (-1, -1):
				continue
			cv2.circle(res, point, DOT_RADIUS, (255, 0, 0), -1)
		return res


	def nearest_edge(self, px, py):
		ys, xs = np.where(self.edges == 255)
		if len(xs) == 0:
			return None
		d2 = (xs - px) ** 2 + (ys - py) ** 2
		idx = np.argmin(d2)
		return int(xs[idx]), int(ys[idx])


class DisplayFrame(tk.Frame):
	

	def __init__(self, parent):
		self.width = 800
		self.height = 600
		self.thresh1 = 20
		self.thresh2 = 150
		self.aspect = self.width / self.height

		super().__init__(parent, width=self.width, height=self.height, bg='lightblue')
		self.pack_propagate(False)
		self.ui = 0
		self.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
		self.bind("<Configure>", self.on_frame_resize)

		self.mouse_down = False
		self.selected_point = -1

		self.dots = []
		self.init_canvas()
		self.set_img(cv2.resize(cv2.imread("./images/0%.jpg"), None, fx=1/4, fy=1/4))

		# Add a button to the left Frame
		# left_button = tk.Button(self, text="Left Button", command=lambda: print("Left Button clicked!"))
		# left_button.pack(pady=10)


	def init_canvas(self):
		self.canvas = tk.Canvas(self, bg='lightblue', width=self.width, height=self.height)
		self.canvas.pack()
		self.canvas.bind("<Motion>", self.on_mouse_move)
		self.canvas.bind("<ButtonPress-1>", self.on_click)
		self.canvas.bind("<ButtonRelease-1>", self.on_release)
		# self.dots = [self.canvas.create_oval(0,0,0,0, fill="red"),self.canvas.create_oval(0,0,0,0, fill="red"),self.canvas.create_oval(0,0,0,0, fill="red"),self.canvas.create_oval(0,0,0,0, fill="red")]
		# self.img_label.bind("<Enter>", self.on_img_entered)
		# self.img_label.bind("<Leave>", self.on_img_exited)

	# this function expects a regular cv2 image at high res
	def set_img(self, img):
		# Convert colors and update aspect ratio
		self.img = ImageData(img)
		self.img.calculate_edges(self.thresh1, self.thresh2)
		self.update_canvas()


	def on_frame_resize(self, event):
		self.width = event.width
		self.height = event.height
		self.aspect = self.width / self.height
	
		self.update_canvas()	

	def on_mouse_move(self, event):
		x, y = event.x / self.scale_factor, event.y / self.scale_factor
		self.ui.mouse_pos_lbl.config(text="Mouse Pos: (%d, %d)" % (x, y))

		if not self.mouse_down: return
		if self.selected_point == -1: return

		nearest = self.img.nearest_edge(x, y)
		if nearest is None:
			print("No edge pixels found.")
			return
		point_idx = self.selected_point
		self.img.points[point_idx] = nearest
		# self.canvas.coords(self.dots[point_idx], nearest[0] - DOT_RADIUS, nearest[1] - DOT_RADIUS, nearest[0] + DOT_RADIUS, nearest[1] + DOT_RADIUS)
		self.update_canvas()

	def on_click(self, event):
		self.mouse_down = True
		x, y = event.x / self.scale_factor, event.y / self.scale_factor

		# find closest point
		min_d2 = -1
		min_idx = -1
		for i, point in enumerate(self.img.points):
			if point == (-1, -1):
				continue
			px, py = point
			d2 = (x - px) ** 2 + (y - py) ** 2
			if min_d2 == -1 or d2 < min_d2:
				min_d2 = d2
				min_idx = i

		# is it close enough?
		if min_d2 != -1 and min_d2 < 30 * 30:
			self.selected_point = min_idx
			# get closest point to mouse
			nearest = self.img.nearest_edge(x, y)
			if nearest is None:
				print("No edge pixels found.")
				return
			# update point
			self.img.points[min_idx] = nearest
			self.update_canvas()
			# self.canvas.coords(self.dots[min_idx], nearest[0] - DOT_RADIUS, nearest[1] - DOT_RADIUS, nearest[0] + DOT_RADIUS, nearest[1] + DOT_RADIUS)
			return
		# place dot here
		point_idx = -1
		for i, point in enumerate(self.img.points):
			if point == (-1, -1):
				print("new point placed")
				point_idx = i
				break
		if point_idx == -1:
			print("all points already placed!")
			return
		
		self.selected_point = point_idx
	
		# create new point
		nearest = self.img.nearest_edge(x, y)
		if nearest is None:
			print("No edge pixels found.")
			return

		self.img.points[point_idx] = nearest
		self.update_canvas()
		# DRAW POINTS AND UPDATE
		# self.canvas.coords(self.dots[point_idx], nearest[0] - DOT_RADIUS, nearest[1] - DOT_RADIUS, nearest[0] + DOT_RADIUS, nearest[1] + DOT_RADIUS)


	def on_release(self, event):
		self.selected_point = -1
		self.mouse_down = False


	def update_canvas(self):
		if self.img.aspect > self.aspect:
			# width is higher than height
			# so scale to height
			self.scale_factor = (self.width) / self.img.src.shape[1]
		else:
			self.scale_factor = (self.height) / self.img.src.shape[0]

		img = cv2.resize(self.img.get_src_with_edges_and_points(), None, fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_AREA)

		# create tk image
		im = Image.fromarray(img)
		self.imgtk = ImageTk.PhotoImage(image=im)
		self.canvas_img = self.canvas.create_image(0,0, anchor="nw", image=self.imgtk)
		self.canvas.configure(width=self.width, height=self.height)
		if self.ui != 0:
			self.ui.size_lbl.config(text="Size: %d x %d" % (self.img.src.shape[1], self.img.src.shape[0]))	

	# def adjust_zoom(self):


class UIFrame(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent, width=150, height=200, bg='lightgreen')
		# Create the right Frame
		self.pack_propagate(False)
		self.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH)
		self.left = 0

		# Add a label to the right Frame
		right_label = tk.Label(self, text="Controls", bg='lightgreen')
		right_label.pack(pady=5, side="top")

		# Add a button to the right Frame
		thresh1_label = tk.Label(self, text="Thresholds", bg='lightgreen')
		thresh1_label.pack(pady=10, padx=10)
		self.thresh1_slider = tk.Scale(self, from_=0.0, to=200.0, orient="horizontal", bg='lightgreen', resolution=0.1, showvalue=True, command=self.on_thresh1)
		self.thresh2_slider = tk.Scale(self, from_=0.0, to=200.0, orient="horizontal", bg='lightgreen', resolution=0.1, showvalue=True, command=self.on_thresh2)
		self.thresh1_slider.set(20)
		self.thresh2_slider.set(150)
		self.thresh1_slider.pack(pady=5)
		self.thresh2_slider.pack(pady=5)

		
		self.size_lbl = tk.Label(self, text="Image size: ", bg='lightgreen')
		self.size_lbl.pack(pady=5, padx=5, side="bottom", anchor="w")
		self.mouse_pos_lbl = tk.Label(self, text="Mouse Pos: ", bg='lightgreen')
		self.mouse_pos_lbl.pack(padx=5, side="bottom", anchor="w")
	
	def on_thresh1(self, value):
		if self.left == 0: return
		self.left.thresh1 = value
		self.left.img.calculate_edges(self.left.thresh1, self.left.thresh2)
		self.left.update_canvas()
	
	def on_thresh2(self, value):
		if self.left == 0: return
		self.left.thresh2 = value
		self.left.img.calculate_edges(self.left.thresh1, self.left.thresh2)
		self.left.update_canvas()



# Create the main application window
root = tk.Tk()
root.title("Tube Helper")

left_frame = DisplayFrame(root)
ui_frame = UIFrame(root)
left_frame.ui = ui_frame
ui_frame.left = left_frame

# Start the Tkinter event loop
root.mainloop()