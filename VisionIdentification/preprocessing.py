import numpy as np
import cv2
import glob

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\Raw Data\*.jpg"

def main(input_path=DATA_PATH):
    in_data = glob.glob(input_path)

    for item_name in in_data:
        try:
            og = cv2.imread(item_name)
        except:
            continue

        print(og.shape)
        test = crop(og) 
        print(test.shape)

        cv2.imshow("test",test)
        cv2.waitKey(0)


def crop(img):
    '''Crops image to be largest square possible'''
    iH, iW, iD = img.shape
    crop_size = min(iH, iW)
    ret = img[(iH - crop_size)//2:(iH - crop_size)//2 + crop_size,(iW - crop_size)//2:(iW - crop_size)//2+crop_size]
    return ret

if __name__=='__main__':
    main()