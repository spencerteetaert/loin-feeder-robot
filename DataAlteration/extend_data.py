import os
import glob 
import random as r
import cv2
from datetime import datetime
import numpy as np

#Distortion parameter limits 
MIN_WIDTH = 1000
MIN_HEIGHT = 1000
MAX_NOISE = 2000
MAX_SKEW = 0.8
MAX_COLOUR_DISTORT = 10 
MIN_QUALITY_REDUCTIION = 10
MAX_QUALITY_REDUCTION = 25

RESIZE_FREQ = 50
NOISE_FREQ = 50
SKEW_FREQ = 50
COLOUR_DISTORT_FREQ = 50

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\Raw Data\*.jpg"
now = datetime.now()
dt_string = now.strftime("%d.%m.%Y %H-%M-%S")
OUTPUT_PATH = "C:\\Users\\User\\Documents\\Hylife 2020\\Loin Feeder\\Data\\Output Data "+dt_string

def main(input_path=DATA_PATH, output_path=OUTPUT_PATH, resize_freq=RESIZE_FREQ, noise_freq=NOISE_FREQ, skew_freq=SKEW_FREQ, colour_distort_freq=COLOUR_DISTORT_FREQ):
    '''This function extends a data set for training purposes. 
    It applies a random assortment of distortions to each image
    including: 
    - Resizing 
    - Noise 
    - Skew 
    - Quality reduction  
    '''
    in_data = glob.glob(input_path)
    counter = 0

    try:
        os.mkdir(output_path)
    except:
        print("ERR: Invalid output path.")
    else:
        print("Output folder created successfully.")

    print("Extending dataset...\n\n")
    
    settings = "Input path:"+str(input_path)+"\nOutput path:"+str(output_path)+"\n\nDistortion Parameters:\n\tResize frequency:"+str(resize_freq) + "\n\tNoise frequency:" + str(noise_freq) + "\n\tSkew frequency:" + str(skew_freq) +"\n\tColour distortion frequency:" + str(colour_distort_freq)
    print(settings)

    for item_name in in_data:
        try:
            og = cv2.imread(item_name)
        except:
            continue
        else:
            print("Altering",item_name)

        export(og, counter, output_path)
        counter += 1 

        for i in range(0, 10):
            output = og
            if (r.randint(0, 100) <= resize_freq):
                output = recrop(output)
            if (r.randint(0, 100) <= noise_freq):
                output = make_noise(output)
            if (r.randint(0, 100) <= skew_freq):
                output = skew(output)
            # if (r.randint(0, 100) <= colour_distort_freq):
            #     output = colour_distort(output)
            # output = reduce_quality(output)

            export(output, counter, output_path)
            counter += 1

    print("Dataset extended.")

def recrop(img, min_width=MIN_WIDTH, min_height=MIN_HEIGHT):
    iH, iW, iD = img.shape
    
    #Chooses random size within constraints
    width = r.randint(min_width, iW-1)
    height = r.randint(min_height, iH-1)

    #Chooses random offsets based off new size
    height_offset = r.randint(0, iH - height)
    width_offset = r.randint(0, iW - width) 

    return img[height_offset:height_offset+height, width_offset:width_offset+width]

def make_noise(img, max_noise=MAX_NOISE):
    '''Function adapted from Shubham Pachori's answer at 
    https://stackoverflow.com/questions/22937589/how-to-add-noise-gaussian-salt-and-pepper-etc-to-image-in-python-with-opencv
    '''
    iH, iW, iD= img.shape
    mean = 0
    var = r.randint(0, max_noise)
    sigma = var**0.5
    gauss = np.random.normal(mean,sigma,(iH,iW,iD))
    gauss = gauss.reshape(iH,iW,iD)
    noisy = img + gauss
    return noisy

def skew(img, max_skew=MAX_SKEW):
    iH, iW, iD = img.shape

    sf = [1 - r.uniform(max_skew, 1) for i in range(0, 8)]

    pts1 = np.float32([[0,iH],[iW,iH],[iW,0],[0,0]])
    pts2 = np.float32([[0 + iW*sf[0],iH - iH*sf[1]],
        [iW - iW*sf[2],iH - iH*sf[3]],
        [iW - iW*sf[4],0 + iH*sf[5]],
        [0 + iW*sf[6],0 + iH*sf[7]]])

    M = cv2.getPerspectiveTransform(pts2,pts1)
    return cv2.warpPerspective(img, M, (iW, iH))

def reduce_quality(img, max_quality_reduction=MAX_QUALITY_REDUCTION):
    pass

def colour_distort(img, max_colour_distort=MAX_COLOUR_DISTORT):
    pass

def export(img, counter, output_path):
    cv2.imwrite(output_path + "\\" + str(counter) + ".png",img)

if __name__=='__main__':
    main()