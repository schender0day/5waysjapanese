import cv2
import numpy as np

RESOLUTION_OPTIONS = {
    '1': (1280, 720),  # 720p
    '2': (1920, 1080),  # 1080p
    '3': (3840, 2160),  # 4K
    '4': (1080, 1920),  # tiktok / shorts
}

# Get user input
print("Please select the resolution:")
print("1. 720p\n2. 1080p\n3. 4K\n4. Tiktok / Shorts")
selection = input("Enter your selection (1-4): ")

if selection not in RESOLUTION_OPTIONS:
    print("Invalid selection.")
    exit()

resolution = RESOLUTION_OPTIONS[selection]

# Open the video file
video = cv2.VideoCapture('media/169_thumbnail.mp4')

# Define the event
def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_MOUSEMOVE:
        print("Mouse coordinates: x={0}, y={1}".format(x, y))

# Create a window
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', resolution[0], resolution[1])

# Bind the function to the window
cv2.setMouseCallback('image',draw_circle)

while(True):
    # Read a frame from the video
    ret, frame = video.read()

    # If the frame was read successfully, display it
    if ret:
        cv2.imshow('image',frame)
        if cv2.waitKey(20) & 0xFF == 27:
            break
    else:
        # Reset the video to the first frame
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)

cv2.destroyAllWindows()
video.release()
