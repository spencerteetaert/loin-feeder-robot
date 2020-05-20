import os
import glob
import random as r
from datetime import datetime
import skimage.measure as skim

import numpy as np
import cv2

#Distortion parameter limits 
MIN_WIDTH = 0.5
MIN_HEIGHT = 0.5
MAX_NOISE = 20
MAX_SKEW = 0.8
MIN_QUALITY_REDUCTION = 2
MAX_QUALITY_REDUCTION = 15
MAX_BRIGHTNESS_DISTORT = 0.5
MAX_CONTRAST_DISTORT = 0.5

RESIZE_FREQ = 80
REDUCTION_FREQ = 90
NOISE_FREQ = 80
SKEW_FREQ = 95
COLOUR_DISTORT_FREQ = 85

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
            if (r.randint(0, 100) <= REDUCTION_FREQ):
                output = reduce_quality(output)
            if (r.randint(0, 100) <= noise_freq):
                output = make_noise(output)
            if (r.randint(0, 100) <= skew_freq):
                output = skew(output)
            if (r.randint(0, 100) <= colour_distort_freq):
                output = lighting_distort(output)

            export(output, counter, output_path)
            counter += 1

    print("Dataset extended.")

def recrop(img, min_width=MIN_WIDTH, min_height=MIN_HEIGHT):
    iH, iW, iD = img.shape
    
    #Chooses random size within constraints
    width = r.randint(iW * min_width // 1, iW-1)
    height = r.randint(iH * min_height // 1, iH-1)

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

def reduce_quality(img, min_quality_reduction=MIN_QUALITY_REDUCTION, max_quality_reduction=MAX_QUALITY_REDUCTION):
    if min_quality_reduction == 1:
        return img
    compression_ratio = r.randint(MIN_QUALITY_REDUCTIION, MAX_QUALITY_REDUCTION)
    return skim.block_reduce(img, (compression_ratio, compression_ratio, 1), np.max)

def lighting_distort(img, max_brightness_distort=MAX_BRIGHTNESS_DISTORT, max_contrast_distort=MAX_CONTRAST_DISTORT):
    alpha = r.uniform(1-max_contrast_distort, 1)
    beta = r.uniform(1-max_brightness_distort, 1)
    new_image = np.zeros(img.shape, img.dtype)
    new_image = np.clip(alpha*img + beta, 0, 255)
    
    return new_image

def export(img, counter, output_path):
    cv2.imwrite(output_path + "\\" + str(counter) + ".png",img)

if __name__=='__main__':
    main()