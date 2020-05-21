import numpy as np

from ..Model.Point import Point
from .. import GlobalParameters

class PathFinder:
    def __init__(self, environment):
        self.environment = environment

    def __call__(self, start_point, end_point, speed):
        end_p = end_point.toArray()
        start_p = start_point.toArray()
        ret = []
        ret += [start_point]

        current = start_p + (end_p - start_p)/np.sqrt((end_p - start_p).dot(end_p - start_p))*speed

        fail_safe = 0
        norm = speed + 1
        while norm > speed:
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

            temp = Point(closest_point[0], closest_point[1])
            if (temp - ret[-1]).mag() > speed:
                ret += [temp]

            norm = np.sqrt((end_p - closest_point).dot(end_p - closest_point))
            current = closest_point + (end_p - closest_point)/norm*speed

            fail_safe += 1
            if (fail_safe > 1000):
                print("ERROR: Path not found.")
                break            

        ret += [end_point]

        diff = end_point.angle - start_point.angle
        if diff > 180:
            dA = -1*(360 - diff)/(len(ret) - 2)
        elif diff < -180:
            dA = -1*(360 + diff)/(len(ret) - 2)
        else:
            dA = diff/(len(ret) - 2)

        for i in range(1, len(ret)-1):
            ret[i].angle = start_point.angle + dA*i

        return ret