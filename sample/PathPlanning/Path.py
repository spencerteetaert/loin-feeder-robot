import numpy as np

from ..Model.Point import Point
from .. import GlobalParameters

class Path:
    def __init__(self, environment):
        self.environment = environment

    def __call__(self, start_point, end_point, speed):
        '''
            Given a pre-set list of finite lines that are safe to travel
            1) calculate line of length speed between the current point and the destination
            2) at the tip of that line, find the nearest point on a "safe line". 
                This is the next point
            3) Find another line of length speed from position on safe line and repeat this process 
                until the end point is within speed of the current point 
        '''
        end_p = end_point.toArray()
        ret = []
        ret += [start_point]

        current = start_point.toArray()
        fail_safe = 0
        norm = speed + 1
        while norm > speed:
            #Do something 
            dists = []
            closest_point = 0
            for i in range(0, len(self.environment)):
                a = np.asarray(self.environment[i][0])
                b = np.asarray(self.environment[i][1])
                c = np.asarray(current)

                n, v = b - a, c - a
                t = max(0, min(np.dot(v, n)/np.dot(n, n), 1))
                dist = np.linalg.norm(c - (a + t*n))
                dists += [dist]
                if min(dists) == dist:
                    closest_point = a + t*n
            ret += [Point(closest_point[0], closest_point[1])]

            norm = np.sqrt((end_p - closest_point).dot(end_p - closest_point))
            current = closest_point + (end_p - closest_point)/norm*speed

            fail_safe += 1
            if (fail_safe > 1000):
                print("ERROR: Path not found.")
                break            

        ret += [end_point]

        return ret