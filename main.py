import cv2
import numpy as np
import pandas as pd
import tkinter as tk
import threading, time, queue
from typing import List
from pathlib import Path

scale_factor = 1/4
originalName = "original"
outlineName = "outline"
next_event = threading.Event()
update_event = threading.Event()
exit_event = threading.Event()

msg_q = queue.Queue()


def wait_until_tk_event(tk_event: threading.Event, params, poll_ms: int = 10):
	"""
	Block until tk_event.is_set(), while keeping OpenCV windows responsive.
	- tk_event: threading.Event that the Tk button will set().
	- poll_ms: cv2.waitKey polling interval in milliseconds.
	Returns when tk_event is set.
	"""
	global exit_event
	while not tk_event.is_set():
		# let OpenCV process window events (mouse callbacks, redraw)
		cv2.waitKey(poll_ms)

		if exit_event.is_set():
			return
		
		if update_event.is_set():
			update_display(params)
			update_event.clear()
		
		msg_q.put_nowait(params)
	

		# tiny sleep to avoid busy loop (optional)
		time.sleep(max(0.001, poll_ms / 1000.0))
	# do not clear event here; caller may clear if they want to reuse
	tk_event.clear()

# Calculating the nearest edge
def nearest_edge(px, py, edge_img):
	"""Return (ex, ey) of the closest edge pixel (value==255) to (px,py)."""
	ys, xs = np.where(edge_img == 255)
	if len(xs) == 0:
		return None
	d2 = (xs - px) ** 2 + (ys - py) ** 2
	idx = np.argmin(d2)
	return int(xs[idx]), int(ys[idx])

def update_display(param):
	global originalName, outlineName
	# draw a red filled circle on **both** mutable displays
	param["orig"] = param["orig_fr"].copy()
	# Redraw outline with new edges
	disp_outl = param["orig_fr"].copy()
	edge_y, edge_x = np.where(param["edges"] == 255)
	disp_outl[edge_y, edge_x] = (0, 255, 0)
	param["outl"] = disp_outl

	outl_overlay = param["outl"].copy()
	orig_overlay = param["orig"].copy()

	for point in param["points"]:
		if point == (-1, -1):
			continue

		cv2.circle(outl_overlay, point, 4, (0, 0, 255), -1)
		cv2.circle(orig_overlay, point, 4, (0, 0, 255), -1)
	
	param["outl"] = cv2.addWeighted(outl_overlay, 0.7, param["outl"], 0.3, 0)
	param["orig"] = cv2.addWeighted(orig_overlay, 0.7, param["orig"], 0.3, 0)

	# refresh both windows
	if not is_window_open(outlineName):
		cv2.namedWindow(outlineName,  cv2.WINDOW_AUTOSIZE)
		cv2.setMouseCallback(outlineName, on_mouse, param)
		
		# create trackbars for canny thresholds
		cv2.createTrackbar('threshold 1', outlineName, param["thresh1"], 500, lambda val: update_thresh1(val, param))
		cv2.createTrackbar('threshold 2', outlineName, param["thresh2"], 500, lambda val: update_thresh2(val, param))
	if not is_window_open(originalName):
		cv2.namedWindow(originalName,  cv2.WINDOW_AUTOSIZE)
		cv2.setMouseCallback(originalName, on_mouse, param)

	cv2.imshow(outlineName, zoom_image(param["outl"], param["zoom"], param["top_left"]))
	cv2.imshow(originalName, zoom_image(param["orig"], param["zoom"], param["top_left"]))

def zoom_image(img, zoom, top_left):
	h, w = img.shape[0], img.shape[1]
	cropped = img[int(top_left[1]):int(top_left[1] + h/zoom), int(top_left[0]):int(top_left[0] + w/zoom)]
	scaled_up = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_NEAREST)
	return scaled_up


def update_thresh1(val, param):
	param["thresh1"] = val
	update_edges(param)

def update_thresh2(val, param):
	param["thresh2"] = val
	update_edges(param)


# Trackbar callback to updates edges
def update_edges(param):
	global originalName, outlineName
	"""Called when trackbar values change."""
	
	# Recompute edges with new thresholds
	edges = cv2.Canny(param["gray"], param["thresh1"], param["thresh2"])
	param["edges"] = edges
	
	update_display(param)


def is_window_open(name: str) -> bool:
    try:
        v = cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)
        return v > 0
    except cv2.error:
        return False

# image analysis, window mouse callback
def on_mouse(event, px, py, flags, param):
	global originalName, outlineName
	# account for zoom and pan
	x, y = param["top_left"][0] + px / param["zoom"], param["top_left"][1] + py / param["zoom"]
	param["mouse_pos"] = (x, y)
	# try to place a new point
	if event == cv2.EVENT_LBUTTONDOWN:
		param["lmb_down"] = True

		# find closest point
		min_d2 = -1
		min_idx = -1
		for i, point in enumerate(param["points"]):
			if point == (-1, -1):
				continue
			px, py = point
			d2 = (x - px) ** 2 + (y - py) ** 2
			if min_d2 == -1 or d2 < min_d2:
				min_d2 = d2
				min_idx = i

		# is it close enough?
		if min_d2 != -1 and min_d2 < 30 * 30:
			param["selected_point"] = min_idx
			# get closest point to mouse
			nearest = nearest_edge(x, y, param["edges"])
			if nearest is None:
				print("No edge pixels found.")
				return
			# update point
			param["points"][min_idx] = nearest
			update_display(param)
			return
	
		# try to create a new point
		point_idx = -1
		for i, point in enumerate(param["points"]):
			if point == (-1, -1):
				point_idx = i
				break
		if point_idx == -1:
			print("all points already placed!")
			return
		
		param["selected_point"] = point_idx
	
		# create new point
		nearest = nearest_edge(x, y, param["edges"])
		if nearest is None:
			print("No edge pixels found.")
			return

		param["points"][point_idx] = nearest
		update_display(param)

	elif event == cv2.EVENT_LBUTTONUP:
		param["selected_point"] = -1
		param["lmb_down"] = False
		update_display(param)
	elif event == cv2.EVENT_MOUSEMOVE:
		if param["lmb_down"] and param["selected_point"] != -1:
			nearest = nearest_edge(x, y, param["edges"])
			if nearest is None:
				print("No edge pixels found.")
				return
			point_idx = param["selected_point"]
			param["points"][point_idx] = nearest
			update_display(param)
		elif param["pan_down"]:
			width = param["orig_fr"].shape[1]
			height = param["orig_fr"].shape[0]
			zoom = param["zoom"]
			delta_x = px - param["pan_down_pos"][0]
			delta_y = py - param["pan_down_pos"][1]
			top_left_x, top_left_y = (param["top_left_prev"][0] - delta_x / zoom, param["top_left_prev"][1] - delta_y / zoom)
			top_left_x = min(max(top_left_x, 0), width - width / zoom)
			top_left_y = min(max(top_left_y, 0), height - height / zoom)
			new_top_left = (int(top_left_x), int(top_left_y))
			old_top_left = param["top_left"]
			param["top_left"] = new_top_left
			# print(delta_x, delta_y)
			# print((new_top_left[0] - old_top_left[0]) ** 2 + (new_top_left[1] - old_top_left[1]) ** 2)

			update_display(param)
	elif event == cv2.EVENT_MOUSEWHEEL:
		delta = flags >> 16
		# max zoom of 2, min zoom of 1 (AKA no zoom)
		old_zoom = param["zoom"]
		new_zoom = min(max(old_zoom * 1.1 ** (delta / 120), 1), 10)
		width = param["orig_fr"].shape[1]
		height = param["orig_fr"].shape[0]
		# zoom in/out from the center, and then clamp top_left to a valid spot
		
		top_left_x = x - px / new_zoom
		top_left_y = y - py / new_zoom
		# top_left_x -= (width/new_zoom - width/old_zoom) / 2
		# top_left_y = y - py / new_zoom

		top_left_x = min(max(top_left_x, 0), width - width / new_zoom)
		top_left_y = min(max(top_left_y, 0), height - height / new_zoom)
		param["top_left"] = (top_left_x, top_left_y)
		param["zoom"] = new_zoom
		update_display(param)
	elif event == cv2.EVENT_MBUTTONDOWN:
		param["top_left_prev"] = (param["top_left"][0], param["top_left"][1])
		param["pan_down_pos"] = (px, py)
		param["pan_down"] = True
	elif event == cv2.EVENT_MBUTTONUP:
		param["pan_down"] = False


# provides image analysis of a single image
def analyze_segment(img) -> List:
	global originalName, outlineName
	# get grayscale
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	# Edge detection
	canny_thr = (20, 150)
	edges = cv2.Canny(gray, *canny_thr)	  # 0 / 255, same size as left

	# a) coloured copy
	disp_orig = img.copy()
	# b) coloured copy for edge overlay
	disp_outl = img.copy()
	# draw every edge pixel as a thin green point
	edge_y, edge_x = np.where(edges == 255)
	disp_outl[edge_y, edge_x] = (0, 255, 0)		# BGR green

	# Pass the two mutable images in a dict so the callback can modify them
	callback_data = {
		"orig_fr": img.copy(), "orig": disp_orig, "outl": disp_outl, "edges": edges, "gray": gray,
		"thresh1": 20, "thresh2": 150,
		"points": [(-1, -1)] * 4,
		"lmb_down": False,
		"selected_point": -1,
		"mouse_pos": (0, 0),
		"zoom": 1,
		"top_left": (0, 0),
		"pan_down": False,
		"pan_down_pos": (0, 0),
		"top_left_prev": (0, 0)
	}

	update_display(callback_data)


	wait_until_tk_event(next_event, callback_data)
	cv2.destroyAllWindows()
	
	# collect the points
	points = callback_data["points"]
	
	# sort them and return
	points.sort(key=lambda p: p[1])
	
	return points


def analyze_image(file_path: str, file_name: str) -> List:
	global originalName, outlineName
	img = cv2.imread(file_path)
	img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

	width = img.shape[1]
	left_delimeter = int(0.372 * width)
	right_delimeter = int(.6488 * width)
	left = img[:, :left_delimeter]
	middle = img[:, left_delimeter:right_delimeter]
	right = img[:, right_delimeter:]

	originalName = file_name + " Left Tube"
	left_points = analyze_segment(left)
	originalName = file_name + " Middle Tube"
	middle_points = analyze_segment(middle)
	originalName = file_name + " Middle Tube"
	right_points = analyze_segment(right)
	return [left_points, middle_points, right_points]


# setup data
data = {
	"File Name": [],
	"Tube": [],
	"y1": [],
	"y2": [],
	"y3": [],
	"y4": [],
	"x1": [],
	"x2": [],
	"x3": [],
	"x4": [],
}

def run_cv():
	path: Path = Path('./images')
	files = [f for f in path.iterdir() if f.is_file()]
	files = files[0:1]
	# print(files)

	for file in files:
		image_points = analyze_image(str(file), file.name)
		data["File Name"].append(file.name)
		data["File Name"].append(file.name)
		data["File Name"].append(file.name)
		data["Tube"].append("Left")
		data["Tube"].append("Middle")
		data["Tube"].append("Right")
		for points in image_points:
			for i, point in enumerate(points):
				data["x" + str(i + 1)].append(point[0] / scale_factor)
				data["y" + str(i + 1)].append(point[1] / scale_factor)

	df = pd.DataFrame(data)
	df.to_csv('out.csv', index=False)



cv_thread = threading.Thread(target=run_cv, daemon=True)
cv_thread.start()
root = tk.Tk()
root.title("Controls")
root.geometry("200x400")
root.pack_propagate(True)
tk.Label(root, text="Controls").pack(pady=10, padx=10)
tk.Button(root, text="Reopen", command=lambda : update_event.set()).pack(padx=10, pady=5)
tk.Button(root, text="Next", command=lambda : next_event.set()).pack(padx=10, pady=5)
mouse_pos_lbl = tk.Label(root, text="No data yet")
mouse_pos_lbl.pack()
selected_pos_lbl = tk.Label(root, text="No point selected")
selected_pos_lbl.pack()
tk.Button(root, text="Quit", command=lambda : root.destroy()).pack(padx=10, pady=5)
def poll():
	try:
		while True:                  # drain all available messages
			info = msg_q.get_nowait()
			text = "Mouse Pos (%d, %d)" % (info["mouse_pos"][0] / scale_factor, info["mouse_pos"][1] / scale_factor)
			mouse_pos_lbl.config(text=text)
			if info["selected_point"] != -1:
				text = "Selected Point Pos (%d, %d)" % (info["points"][info["selected_point"]][0] / scale_factor, info["points"][info["selected_point"]][1] / scale_factor)
				selected_pos_lbl.config(text=text)
	except queue.Empty:
		root.after(50, poll)

root.after(50, poll)
root.mainloop()
exit_event.set()
cv_thread.join()