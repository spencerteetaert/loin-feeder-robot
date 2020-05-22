import numpy as np

from ..Model.Point import Point
from .. import GlobalParameters

class PathFinder:
    def __init__(self):
        self.environment = GlobalParameters.SAFE_ENVIRONMENT

    def __call__(self, start_point, end_point, speed):
        # Convert to arrays to make use of numpy functionality 
        end_p = end_point.toArray()
        start_p = start_point.toArray()
        ret = []
        ret += [start_point]

        norm = np.sqrt((end_p - start_p).dot(end_p - start_p))
        current = start_p + (end_p - start_p)/norm*speed
        
        fail_safe = 0
        while norm > speed:
            dists = []
            closest_point = []
            for i in range(0, len(self.environment)):
                a = np.asarray(self.environment[i][0])
                b = np.asarray(self.environment[i][1])
                c = np.asarray(current)

                n, v = b - a, c - a
                t = max(0, min(np.dot(v, n)/np.dot(n, n), 1))

                # Finds closest point p on line to the current point
                p = a + t*n

                # If this point is closer than every other line, keep it
                dist = np.linalg.norm(c - p)
                dists += [dist]
                if min(dists) == dist:
                    closest_point = p

            # Only keep the point if it's sufficiently far away from the original 
            # (to prevent bunching)
            temp = Point(closest_point[0], closest_point[1])
            if (temp - ret[-1]).mag() > speed:
                ret += [temp]

            # Set next point in the direction of end 
            norm = np.sqrt((end_p - closest_point).dot(end_p - closest_point))
            current = closest_point + (end_p - closest_point)/norm*speed

            # Break point to avoid infinite looping if path isn't found 
            fail_safe += 1
            if (fail_safe > GlobalParameters.RUNTIME_LIMIT):
                print("ERROR: Path not found.")
                break            

        ret += [end_point]

        # Runs through all path points and sets an angle increment 
        diff = end_point.angle - start_point.angle
        if diff > 180:
            dA = -1*(360 - diff)/(len(ret) - 3)
        elif diff < -180:
            dA = -1*(360 + diff)/(len(ret) - 3)
        else:
            dA = diff/(len(ret) - 3)

        for i in range(0, len(ret)-2):
            ret[i+1].angle = start_point.angle + dA*i

        return ret