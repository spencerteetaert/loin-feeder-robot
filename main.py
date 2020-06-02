from source.path_planning.frame_handler import FrameHandler

import cv2

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"

def main():
    frame_handler = FrameHandler()
    stream = cv2.VideoCapture(DATA_PATH)

    while True:
        (grabbed, temp) = stream.read() # Read frame into here
        try:
            frame_handler.process_frame(temp)
        except:
            print("ERROR: Frame unable to be processed.")
            break
main()