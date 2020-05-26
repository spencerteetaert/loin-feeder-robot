import time

import numpy as np 
import cv2
import matplotlib.pyplot as plt
plt.rcParams.update({'text.color' : "white", 'axes.labelcolor' : "white", 'ytick.color' : "white", 'xtick.color' : "white"})

from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification.VideoReader import FileVideoStream
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample.PathPlanning.PathRunner import PathRunner
from sample import GlobalParameters

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"

# Model for creating acceleration profiles
profile_model = Robot(Point(280, 600), GlobalParameters.VIDEO_SCALE)
path_runner = PathRunner(profile_model)
# Model for display
drawing_model = Robot(Point(280, 600), GlobalParameters.VIDEO_SCALE)

streamer = FileVideoStream(DATA_PATH)
streamer.start()
time.sleep(1)

current_graph = np.zeros([830, 830, 3], dtype=np.uint8)

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)

def figure_to_array(fig):
    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    ret = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    ret.shape = (w, h, 4)

    return ret[:,:,1:4]

def update_current_graph():
    global path_runner, current_graph
    xs, ys, _, _ = path_runner.read()
    ax1_label = "(m)"
    ax2_label = "(°)"
    title = "Position profiles"

    fig, ax1 = plt.subplots()
            
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Linear extension ' + ax1_label)
    ax1.plot(xs, ys[:,0], label="Main Track linear")
    ax1.plot(xs, ys[:,1], label="Main arm linear")
    ax1.plot(xs, ys[:,3], label="Secondary arm linear 1")
    ax1.plot(xs, ys[:,4], label="Secondary arm linear 2")
    ax1.set_facecolor('black')
    ax1.spines['bottom'].set_color('white')
    ax1.spines['top'].set_color('white') 
    ax1.spines['right'].set_color('white')
    ax1.spines['left'].set_color('white')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Rotation ' + ax2_label)
    ax2.plot(xs, ys[:,2], label="Main arm rotational")
    ax2.plot(xs, ys[:,5], label="Secondary arm rotational")
    ax2.plot(xs, ys[:,6], label="Carriage 1 rotational")
    ax2.plot(xs, ys[:,7], label="Carriage 2 rotational")
    ax2.set_facecolor('black')
    ax2.spines['bottom'].set_color('white')
    ax2.spines['top'].set_color('white') 
    ax2.spines['right'].set_color('white')
    ax2.spines['left'].set_color('white')

    axes = (ax1, ax2)
    ex = [ax.get_ylim() for ax in axes]
    top = [e[1] / (e[1] - e[0]) for e in ex]
    # Ensure that plots (intervals) are ordered bottom to top:
    if top[0] > top[1]:
        axes, ex, top = [list(reversed(l)) for l in (axes, ex, top)]

    # Bounds overflow from shift
    tot_span = top[1] - top[0] + 1

    temp1 = ex[0][0] + tot_span * (ex[0][1] - ex[0][0])
    temp2 = ex[1][1] - tot_span * (ex[1][1] - ex[1][0])
    axes[0].set_ylim(ex[0][0], temp1)
    axes[1].set_ylim(temp2, ex[1][1])

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc="upper left")
    plt.title(title)

    fig.tight_layout()

    fig.set_size_inches(830 / 100, 830 / 100)
    fig.set_facecolor('black')
    temp = figure_to_array(fig)
    current_graph = temp

def main(data_path=DATA_PATH):
    global streamer, profile_model, drawing_model, current_graph
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output16.mp4', 0x7634706d, 30, (1680,830))

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    delay = 0
    flip_flop = False 
    flip_flop2 = False

    meats = [0]
    queue1 = []
    queue2 = []

    while(streamer.more()):
        ################################################
        ### Video Processing and Meat Identification ###
        ################################################
        
        force_timer = time.time()

        # Keeps streamer queue size within a lag free range (>0 and <128)
        qsize = streamer.Q.qsize()
        if qsize < 40:
            streamer.sleep_time = 0
        elif qsize > 88:
            streamer.sleep_time = 0.005
        
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        frame = streamer.read()
        frame = image_sizing.scale(frame)
        frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        iH, iW, iD = frame.shape
        box, _ = bbox.get_bbox(frame)

        if (box != 0):
            for i in range(0, len(box)):
                if delay > 50:
                    try:
                        M = cv2.moments(box[i])
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])

                        if iH / 3 - 5 < cY and iH / 3 + 5 > cY:
                            if flip_flop:
                                meats += [meat.Meat(box[i], side="Right", center=[cX, cY])]
                            else:
                                meats += [meat.Meat(box[i], side="Left", center=[cX, cY])]
                            flip_flop = not flip_flop
                            
                            delay = 0
                    except:
                        pass
        delay += 1

        ########################################
        ### Path planning and Robot Movement ###
        ########################################

        ep1 = Point(625, 735, angle=90)
        ep2 = Point(250, 735, angle=90)

        if len(meats) > 3:
            if len(meats) % 2 == 0 and delay == 1:
                # Queue [P1 index, P2 index], so that meat can be accounted for even if robot is currently in motion 
                queue1 += [[len(meats) - 1, len(meats) - 2]]
                queue2 += [[len(meats) - 1, len(meats) - 2]]
                
        # Profiler model creates motion profiles, it updates as fast as possible in a separate thread
        if profile_model.phase == 0 and len(queue1) > 0 and not path_runner.running:
            dist = (GlobalParameters.PICKUP_POINT - meats[queue1[0][0]].get_center_as_point()).y

            if dist > 0:
                sp1 = meats[queue1[0][0]].get_center_as_point().copy() + Point(0, dist)
                sp2 = meats[queue1[0][1]].get_center_as_point().copy() + Point(0, dist)
                profile_model.moveMeat(sp1, sp2, ep1, ep2, dist // GlobalParameters.CONVEYOR_SPEED)
                queue1 = queue1[1:]

                # Given the start and end conditions, calculate the profile_model motor profiles
                path_runner.start()
                flip_flop2 = True
                temp = dist
        
        if flip_flop2 and not path_runner.running:
            update_current_graph()
            flip_flop2 = False
        
        # Drawing model is just for drawing purposes, it updates at the frame rate displayed
        if drawing_model.phase == 0 and len(queue2) > 0:
            dist = (GlobalParameters.PICKUP_POINT - meats[queue2[0][0]].get_center_as_point()).y

            if dist > 0:
                sp1 = meats[queue2[0][0]].get_center_as_point().copy() + Point(0, dist)
                sp2 = meats[queue2[0][1]].get_center_as_point().copy() + Point(0, dist)
                drawing_model.moveMeat(sp1, sp2, ep1, ep2, dist // GlobalParameters.CONVEYOR_SPEED, counter=temp-dist)
                queue2 = queue2[1:]
            else:
                print("ERROR: Conveyor Speed too fast for current settings")
                queue2 = queue2[1:]
        drawing_model.update()

        ###############
        ### Display ###
        ###############        
        
        if (len(meats) != 1):
            for i in range(1, len(meats)):
                meats[i].draw(frame, color=(255, 255, 0))
        drawing_model.draw(frame)

        frame = np.concatenate((frame, current_graph), axis=1)
        cv2.imshow(win, frame)

        ################
        ### Controls ###
        ################

        for i in range(1, len(meats)):
            meats[i].step()

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)
        
        # out.write(frame)

        # Artifically slow the program to the desired frame rate
        # cv2.waitKey(max(GlobalParameters.FRAME_RATE - round((time.time() - force_timer )*1000 + 1), 1))

    # out.release()
    streamer.stop()
    path_runner.stop()
    cv2.destroyAllWindows()

main()