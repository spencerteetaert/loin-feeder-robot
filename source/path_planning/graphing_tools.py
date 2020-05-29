from threading import Thread
from threading import Lock

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'text.color' : "white", 'axes.labelcolor' : "white", 'ytick.color' : "white", 'xtick.color' : "white"})

def figure_to_array(fig:plt.figure):
    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    ret = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    ret.shape = (w, h, 4)

    return ret[:,:,1:4]

class Grapher:
    ''' Class that produces a graph from the data collected by path_runner'''
    def __init__(self):
        self.stopped = False
        self.running = False

    def start(self, path_runner, size, switch):
        self.t = Thread(target=self.run, args=([path_runner, size, switch]))
        self.t.daemon = True
        self.t.start()
        return self

    def stop(self):
        self.stopped = True

    def run(self, path_runner, size, switch):
        self.running = True
        while path_runner.running:
            pass
        if switch == 'o':
            xs, ys, _ = path_runner.read()
            ax1_label = "(m)"
            ax2_label = "(°)"
            title = "Raw position profiles"
        elif switch == 'i':
            xs, _, ys = path_runner.read()
            ax1_label = "(m)"
            ax2_label = "(°)"
            title = "Integrated position profiles"
        else: 
            return np.zeros([size[0], size[1], 3])
        
        fig, ax1 = plt.subplots()
                
        # Sets axis for linear actuators 
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Linear extension ' + ax1_label)
        ax1.plot(xs, ys[:,0], label="Main Track linear", color='#ff0000') 
        ax1.plot(xs, ys[:,1], label="Main arm linear", color='#ffb300')
        ax1.plot(xs, ys[:,3], label="Secondary arm linear 1", color='#00ff1a')
        ax1.plot(xs, ys[:,4], label="Secondary arm linear 2", color='#00ffcc')
        ax1.set_facecolor('black')
        ax1.spines['bottom'].set_color('white')
        ax1.spines['top'].set_color('white') 
        ax1.spines['right'].set_color('white')
        ax1.spines['left'].set_color('white')
        # ax1.set_ylim(0, 1.2)

        # Sets axis for rotational motors
        ax2 = ax1.twinx()
        ax2.set_ylabel('Rotation ' + ax2_label)
        ax2.plot(xs, ys[:,2], label="Main arm rotational", color='#007fff')
        ax2.plot(xs, ys[:,5], label="Secondary arm rotational", color='#3300ff')
        ax2.plot(xs, ys[:,6], label="Carriage 1 rotational", color='#e600ff')
        ax2.plot(xs, ys[:,7], label="Carriage 2 rotational", color='#ff0066')
        ax2.set_facecolor('black')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['top'].set_color('white') 
        ax2.spines['right'].set_color('white')
        ax2.spines['left'].set_color('white')
        # ax2.set_ylim(0, 360)

        # Gets limits and shifts data to ensure graphs are lined up at 0
        axes = (ax1, ax2)
        ex = [ax.get_ylim() for ax in axes]
        top = [e[1] / (e[1] - e[0]) for e in ex]
        if top[0] > top[1]:
            axes, ex, top = [list(reversed(l)) for l in (axes, ex, top)]

        tot_span = top[1] - top[0] + 1

        temp1 = ex[0][0] + tot_span * (ex[0][1] - ex[0][0])
        temp2 = ex[1][1] - tot_span * (ex[1][1] - ex[1][0])
        axes[0].set_ylim(ex[0][0], temp1)
        axes[1].set_ylim(temp2, ex[1][1])

        # Style
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left", facecolor='black')
        plt.title(title)
        fig.tight_layout()
        fig.set_size_inches(size[0] / 100, size[1] / 100)
        fig.set_facecolor('black')

        # Converts result into an array for display 
        self.fig = figure_to_array(fig)
        plt.close()
        self.running = False
            
    def read(self):
        if not self.running:
            return self.fig
        else:
            with Lock():
                print("ERROR: Request for data made before results computed")
            return 