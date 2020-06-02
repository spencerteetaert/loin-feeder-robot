from source.path_planning.frame_handler import FrameHandler

def main(data_path=DATA_PATH):
    frame_handler = FrameHandler()

    while True:
        temp = 0 # Read frame into here
        try:
            frame_handler.process_frame(temp)
        except:
            print("ERROR: Frame unable to be processed.")
            break

main()