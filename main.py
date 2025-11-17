import cv2
import numpy as np

scale_factor = 1

img = cv2.imread('./images/0%.jpg')
img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

w = img.shape[1]
left_delimeter = int(0.372 * w)
left = img[:, :left_delimeter]                 # colour image (BGR)

gray_left = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)

# -------------------------------------------------
# 2️⃣ Edge detection (binary image)
# -------------------------------------------------
canny_thr = (20, 150)
edges = cv2.Canny(gray_left, *canny_thr)      # 0 / 255, same size as left

# -------------------------------------------------
# 3️⃣ Prepare two display images
# -------------------------------------------------
# a) original colour copy
disp_orig = left.copy()

# b) colour copy with the whole edge outline drawn (so the user sees the contour)
disp_outl = left.copy()
# draw every edge pixel as a thin green point
edge_y, edge_x = np.where(edges == 255)
disp_outl[edge_y, edge_x] = (0, 255, 0)        # BGR green

# -------------------------------------------------
# 4️⃣ Helper: nearest edge pixel
# -------------------------------------------------
def nearest_edge(px, py, edge_img):
    """Return (ex, ey) of the closest edge pixel (value==255) to (px,py)."""
    ys, xs = np.where(edge_img == 255)
    if len(xs) == 0:
        return None
    d2 = (xs - px) ** 2 + (ys - py) ** 2
    idx = np.argmin(d2)
    return int(xs[idx]), int(ys[idx])

# -------------------------------------------------
# 5️⃣ Mouse callback (shared by both windows)
# -------------------------------------------------
def on_click(event, x, y, flags, param):
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    nearest = nearest_edge(x, y, edges)
    if nearest is None:
        print("No edge pixels found.")
        return

    ex, ey = nearest
    print(ey / scale_factor)

    # draw a red filled circle on **both** mutable displays
    cv2.circle(param["orig"], (ex, ey), 5, (0, 0, 255), -1)   # red
    cv2.circle(param["outl"], (ex, ey), 5, (0, 0, 255), -1)

    # refresh both windows
    cv2.imshow('original', param["orig"])
    cv2.imshow('outline', param["outl"])

# -------------------------------------------------
# 6️⃣ Register callbacks and start UI loop
# -------------------------------------------------
cv2.namedWindow('original', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('outline',  cv2.WINDOW_AUTOSIZE)

# Pass the two mutable images in a dict so the callback can modify them
callback_data = {"orig": disp_orig, "outl": disp_outl}
cv2.setMouseCallback('original', on_click, callback_data)
cv2.setMouseCallback('outline',  on_click, callback_data)

# Show the initial frames
cv2.imshow('original', disp_orig)
cv2.imshow('outline',  disp_outl)

cv2.waitKey(0)
cv2.destroyAllWindows()