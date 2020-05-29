import numpy as np

def get_normal_unit(p1, p2):
    k = np.subtract(p1, p2)
    x = np.array([(k / np.linalg.norm(k))[1], -1*(k / np.linalg.norm(k))[0]])  # Find perpendicular normal
    return x

def distance(self, pt1, pt2):
    return math.sqrt((pt2[0][1] - pt1[0][1])**2 + (pt2[0][0] - pt1[0][0])**2)