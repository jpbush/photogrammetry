import imutils
import argparse
import sys
import math
import numpy as np
import cv2
import glob
import os

a = np.array([1, 2, 3])
print(str(a))
np.save("a_out.npy", a)
c = np.load("a_out.npy")
print(str(c))
