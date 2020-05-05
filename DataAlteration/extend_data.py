import os
import glob 
import random as r
import cv2
from datetime import datetime

#Distortion parameter limits 
MIN_WIDTH = 1000
MIN_HEIGHT = 1000
MAX_NOISE = 10
MAX_SKEW = 8 
MAX_COLOUR_DISTORT = 10 
MAX_QUALITY_REDUCTION = 25

RESIZE_FREQ = 2
NOISE_FREQ = 2
SKEW_FREQ = 2
COLOUR_DISTORT_FREQ = 2

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

    print("Extending dataset...\n\nInput path:",
        input_path,"\nOutput path:", output_path, 
        "\n\nDistortion Parameters:\n\tResize frequency:",
        resize_freq, "\n\tNoise frequency:",noise_freq, 
        "\n\tSkew frequency:", skew_freq,
        "\n\tColour distortion frequency:", colour_distort_freq)

    for item_name in in_data:
        print("Viewing",item_name)
        try:
            og = cv2.imread(item_name)
        except:
            print("ERR: Item",item_name,"not an image.")
            continue
        else:
            print("Image detected.")

        export(og, counter, output_path)
        counter += 1 

        for i in range(0, 10):
            output = og
            if (r.randint(0, resize_freq-1) == 0):
                output = recrop(output)
            # if (r.randint(0, noise_freq-1) == 0):
            #     output = make_noise(output)
            # if (r.randint(0, skew_freq-1) == 0):
            #     output = skew(output, "h")
            # if (r.randint(0, skew_freq-1) == 0):
            #     output = skew(output, "v")
            # if (r.randint(0, colour_distort_freq-1) == 0):
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

    print("new bounds:\n\t", height_offset,":",height_offset+height,"\n\t",width_offset,":",width_offset+width)

    return img[height_offset:height_offset+height, width_offset:width_offset+width]

def make_noise(img, MAX_NOISE=MAX_NOISE):
    pass

def skew(img, orientation, max_skew=MAX_SKEW):
    pass

def reduce_quality(img, max_quality_reduction=MAX_QUALITY_REDUCTION):
    pass

def colour_distort(img, max_colour_distort=MAX_COLOUR_DISTORT):
    pass

def export(img, counter, output_path):
    cv2.imwrite(output_path + "\\" + str(counter) + ".png",img)

if __name__=='__main__':
    main()