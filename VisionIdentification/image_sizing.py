import numpy as np
import cv2

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\Raw Data\*.jpg"
DEST_WIDTH = 1000
DEST_HEIGHT = 1000

def main(input_path=DATA_PATH):
    import glob
    
    in_data = glob.glob(input_path)

    for item_name in in_data:
        try:
            og = cv2.imread(item_name)
        except:
            continue

        test1 = crop(og) 
        test1 = scale(test1) 

        test2 = scale(og)

        output_path = "C:\\Users\\User\\Documents\\Hylife 2020\\Loin Feeder\\Data"

        cv2.imwrite(output_path + "\\test1.png",test1)
        cv2.imwrite(output_path + "\\test2.png",test2)

def crop(img):
    '''Crops image to be largest square possible'''
    iH, iW, iD = img.shape
    crop_size = min(iH, iW)
    ret = img[(iH - crop_size)//2:(iH - crop_size)//2 + crop_size,(iW - crop_size)//2:(iW - crop_size)//2+crop_size]
    return ret

def scale(img, dest_height=DEST_HEIGHT, dest_width=DEST_WIDTH):
    iH, iW, iD = img.shape
    res = cv2.resize(img, dsize=(dest_height, dest_width), interpolation=cv2.INTER_CUBIC)
    return res

if __name__=='__main__':
    main()