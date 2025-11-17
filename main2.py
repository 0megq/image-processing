import cv2

def _mouse_move(event, x, y, flags, param):
    """Prints the current (x, y) whenever the mouse moves inside a window."""
    if event == cv2.EVENT_MOUSEMOVE:
        # `param` is the window name that received the event
        win_name = param
        print(f"[{win_name}] x:{x}  y:{y}")

def enable_coord_logging(win_name: str):
    """
    Call this **once** after creating a window with `cv2.namedWindow`.
    It attaches the mouse‑move callback that prints coordinates.
    """
    cv2.setMouseCallback(win_name, _mouse_move, param=win_name)



img = cv2.imread('./images/0%.jpg')

img = cv2.resize(img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)

# gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# get segmented
width = img.shape[1]
left_delimeter = int(.372 * width)
# right_delimeter = int(.6488 * width)
left = img[:, 0:left_delimeter]
# center = img[:, left_delimeter:right_delimeter]
# right = img[:, right_delimeter:]

gray_left = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)

canny_thr = (20, 150)
edges = cv2.Canny(gray_left, *canny_thr)
print(edges)

# w = "window"
# cv2.namedWindow(w, cv2.WINDOW_AUTOSIZE)

cv2.imshow('left', left)
# cv2.imshow('gray', gray_left)
cv2.imshow('edges', edges)
# cv2.imshow('center', center)
# cv2.imshow('right', right)

# cv2.imshow('entire', gray_img)
cv2.waitKey(0)
cv2.destroyAllWindows()