import time

import numpy as np 
import cv2
import matplotlib.pyplot as plt

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

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)

def main(data_path=DATA_PATH):
    global streamer, profile_model, drawing_model
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output15.mp4', 0x7634706d, 30, (850,830))

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    delay = 0
    flip_flop = False 

    meats = [0]
    queue = []

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

        iH, _, _ = frame.shape
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
                queue += [[len(meats) - 1, len(meats) - 2]]
                
        if drawing_model.phase == 0 and len(queue) > 0 and not path_runner.running:
            dist = (GlobalParameters.PICKUP_POINT - meats[queue[0][0]].get_center_as_point()).y

            if dist > 0:
                sp1 = meats[queue[0][0]].get_center_as_point().copy() + Point(0, dist)
                sp2 = meats[queue[0][1]].get_center_as_point().copy() + Point(0, dist)
                profile_model.moveMeat(sp1, sp2, ep1, ep2, dist // GlobalParameters.CONVEYOR_SPEED)
                drawing_model.moveMeat(sp1, sp2, ep1, ep2, dist // GlobalParameters.CONVEYOR_SPEED)
                queue = queue[1:]

                # Given the start and end conditions, calculate the profile_model motor profiles
                path_runner.start()
                # while profile_model.update():
                #     pass

                
            else:
                print("ERROR: Conveyor Speed too fast for current settings")
                queue = queue[1:]

        # Use this code if you want to see the robot in real time
        if drawing_model.phase != 0:
            drawing_model.update()
        # profile_model = path_runner.profile_model

        ###############
        ### Display ###
        ###############        
        
        if (len(meats) != 1):
            for i in range(1, len(meats)):
                meats[i].draw(frame, color=(255, 255, 0))
        drawing_model.draw(frame)
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
        elif k == ord('s'):
            k2 = cv2.waitKey(0) & 0xFF
            if k2 == ord('p'):
                xs, ys, _, _ = path_runner.read()
                ax1_label = "(m)"
                ax2_label = "(°)"
                title = "Position profiles"
            elif k2 == ord('v'):
                xs, _, ys, _ = path_runner.read()
                ax1_label = "(m/s)"
                ax2_label = "(°/s)"
                title = "Velocity profiles"
            elif k2 == ord('a'):
                xs, _, _, ys = path_runner.read()
                ax1_label = "(m/s^2)"
                ax2_label = "(°/s^2)"
                title = "Acceleration profiles"

            fig, ax1 = plt.subplots()
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Linear extension ' + ax1_label)
            ax1.plot(xs, ys[:,0], label="Main Track linear")
            ax1.plot(xs, ys[:,1], label="Main arm linear")
            ax1.plot(xs, ys[:,3], label="Secondary arm linear 1")
            ax1.plot(xs, ys[:,4], label="Secondary arm linear 2")

            ax2 = ax1.twinx()
            ax2.set_ylabel('Rotation ' + ax2_label)
            ax2.plot(xs, ys[:,2], label="Main arm rotational")
            ax2.plot(xs, ys[:,5], label="Secondary arm rotational")
            ax2.plot(xs, ys[:,6], label="Carriage 1 rotational")
            ax2.plot(xs, ys[:,7], label="Carriage 2 rotational")

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
            plt.show()

        # out.write(frame)

        # Artifically slow the program to the desired frame rate
        # cv2.waitKey(max(GlobalParameters.FRAME_RATE - round((time.time() - force_timer )*1000 + 1), 1))

    # out.release()
    streamer.stop()
    path_runner.stop()
    cv2.destroyAllWindows()

main()