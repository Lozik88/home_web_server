import cv2
import numpy as np

# index = 0
# arr = []
# while True:
#     cap = cv2.VideoCapture(index)
#     if not cap.read()[0]:
#         break
#     else:
#         arr.append(index)
#     cap.release()

#     index += 1
# arr



# all_camera_idx_available = []
# for camera_idx in range(10000):
#     cap = cv2.VideoCapture(camera_idx)
#     if cap.isOpened():
#         print(f'Camera index available: {camera_idx}')
#         all_camera_idx_available.append(camera_idx)
#         cap.release()
cam = cv2.VideoCapture(2)

cv2.namedWindow("test")

img_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()