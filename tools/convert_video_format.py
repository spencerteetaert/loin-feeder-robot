import cv2

input_path = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"

video_capture = cv2.VideoCapture(input_path)
out = cv2.VideoWriter(r'C:\Users\User\Desktop\output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (1080,2288))

counter = 0

while video_capture.isOpened():
    val, frame = video_capture.read()
    if val ==True:
        out.write(frame)
    else:
        break

video_capture.release()