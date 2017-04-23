# Resources
# http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_calib3d/py_table_of_contents_calib3d/py_table_of_contents_calib3d.html#py-table-of-content-calib
# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.html#calibration

# USAGE
# python camera_calibration.py --input <calibration image directory> --output <output directory>
# python ball_tracking.py

import imutils
import argparse
import sys
import math
import numpy as np
import cv2
import glob

#Defines
min_cal_images = 10
min_pattern_width = 4
max_pattern_width = 16
min_pattern_height = 4
max_pattern_height = 16

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",
	help="path to the (optional) calibration image directory")
ap.add_argument("-o", "--output",
	help="path to the (optional) output directory")
ap.add_argument("--width",
	help="pattern width in number of squares")
ap.add_argument("--height",
	help="pattern height in number of squares")
args = vars(ap.parse_args())

# if an input directory was given
if args.get("input", False):
	cal_in_dir = args["input"]
# otherwise, ask the user for an input directory
else:
	cal_in_dir = raw_input("Enter the calibration image directory: ")
print("Input directory: [" + cal_in_dir + "]")

# if an output directory was given
if args.get("output", False):
	cal_out_dir = args["output"]
else:
	cal_out_dir = None

# get all the images
images = glob.glob(cal_in_dir + "*.jpg")
num_images = len(images)
print("Images found in directory: " + str(num_images))
if (len(images) < min_cal_images):
    print("You need at least " + str(min_cal_images) + " images to calibrate.")
    print("Goodbye...")
    quit()

# make sure they input a width
if args.get("width", False):
	pattern_width = int(args["width"])
# otherwise, ask the user for it
else:
	pattern_width = int(raw_input("Enter pattern width: "))
while(pattern_width < min_pattern_width or pattern_width > max_pattern_width):
	print("Pattern width must be at least " + str(min_pattern_width) + " and no greater than " + str(max_pattern_width) + ".")
	pattern_width = int(raw_input("Enter pattern width: "))
pattern_width = pattern_width - 1

# make sure they input a height
if args.get("height", False):
	pattern_height = int(args["height"])
# otherwise, ask the user for it
else:
	pattern_height = int(raw_input("Enter pattern height: "))
while(pattern_height < min_pattern_height or pattern_height > max_pattern_height):
	print("Pattern height must be at least " + str(min_pattern_height) + " and no greater than " + str(max_pattern_height) + ".")
	pattern_height = int(raw_input("Enter pattern height: "))
pattern_height = pattern_height - 1

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(pattern_width,pattern_height,0)
objp = np.zeros((pattern_height*pattern_width,3), np.float32)
objp[:,:2] = np.mgrid[0:pattern_width,0:pattern_height].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# Go through all the images
print("Processing " + str(num_images) + " images...")
for fname in images:
	print(fname + "...")

	img = cv2.imread(fname)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	# Find the pattern corners
	ret, corners = cv2.findChessboardCorners(gray, (pattern_width,pattern_height),None)

	# If found, add object points, image points (after refining them)
	if ret == True:
		print("Found the board!")
		objpoints.append(objp)

		cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
		imgpoints.append(corners)

		# Draw and display the corners
		cv2.drawChessboardCorners(img, (pattern_width,pattern_height), corners, ret)
		cv2.imshow("img",img)
		cv2.waitKey(500)

print("Done processing images")

cv2.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

img = cv2.imread(glob.glob("*.jpg")[0])
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

print(str(newcameramtx))

# undistort
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

# crop the image
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite("calibresult.png",dst)
