# USAGE
# python calibrate_camera.py --input <calibration image directory> --output <output directory> --width <pattern width> --height <pattern height>

import imutils
import argparse
import sys
import math
import numpy as np
import cv2
import glob
import os

#Defines
min_cal_images = 10
min_pattern_width = 4
max_pattern_width = 16
min_pattern_height = 4
max_pattern_height = 16

# construct the argument parser and parse the arguments
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

print("")
# if an input directory was given
if args.get("input", False):
	input_path = args["input"]
# otherwise, ask the user for an input directory
else:
	input_path = raw_input("Enter the calibration image directory: ")
# make sure the input directory is valid
while(not os.path.isdir(input_path)):
	print("Input directory must exist.")
	input_path = raw_input("Enter the calibration image directory: ")
print("Input directory: [" + input_path + "]")

# get all the images
print("Finding images...")
images = glob.glob(input_path + "*.jpg")
num_images = len(images)
print("Images found in directory: " + str(num_images))
if (len(images) < min_cal_images):
    print("You need at least " + str(min_cal_images) + " images to calibrate.")
    print("Goodbye...")
    quit()
# make sure all the images are the same size
print("Making sure images have the same dimensions...")
img_size = cv2.imread(images[0]).shape[:2]
img_height,  img_width = img_size
for img in images:
	h,  w = cv2.imread(img).shape[:2]
	if(h != img_height or w != img_width):
	    print("Input images have mismatched dimensions.")
	    print("Goodbye...")
	    quit()
print("Image dimensions look good!")

# if an output directory was given
if args.get("output", False):
	output_path = args["output"]
else:
	output_path = raw_input("Enter the output directory: ")
while(not os.path.isdir(output_path)):
	print("Output directory must exist.")
	output_path = raw_input("Enter the output directory: ")
print("Output directory: [" + output_path + "]")

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

######## Input parsed

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(pattern_width,pattern_height,0)
objp = np.zeros((pattern_height*pattern_width,3), np.float32)
objp[:,:2] = np.mgrid[0:pattern_width,0:pattern_height].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# Go through all the images
print("\n\rProcessing " + str(num_images) + " images...")
for img_path_file in images:
	path, filename = os.path.split(img_path_file)
	print(filename)
	img = cv2.imread(img_path_file)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	# Find the pattern corners
	ret, corners = cv2.findChessboardCorners(gray, (pattern_width,pattern_height),None)

	# If found, add object points, image points (after refining them)
	if ret == True:
		print("Pattern found!")
		objpoints.append(objp)

		cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
		imgpoints.append(corners)

		# Draw and display the corners
		#cv2.drawChessboardCorners(img, (pattern_width,pattern_height), corners, ret)
		#cv2.imshow("img",img)
		#cv2.waitKey(500)
	else:
		print("Pattern NOT found.")

print("Done processing images.\n\r")
#cv2.destroyAllWindows()

# GET THE CAMERA MATRIX!!
ret, camera_mtx, camera_dist_coeff, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
new_camera_mtx, valid_pix_roi =cv2.getOptimalNewCameraMatrix(camera_mtx,camera_dist_coeff,(img_width,img_height),1,(img_width,img_height))

# print("\nUndistorting pattern images...")
# undistorted_path = output_path + os.sep + "undistorted"
# if not os.path.exists(undistorted_path):
#     os.makedirs(undistorted_path)
# for img_path_file in images:
# 	path, filename = os.path.split(img_path_file)
# 	print(filename)
# 	img = cv2.imread(img_path_file)
# 	# undistort
# 	dst = cv2.undistort(img, camera_mtx, camera_dist_coeff, None, new_camera_mtx)
# 	cv2.imwrite(undistorted_path + os.sep + filename, dst)
# print("Undistorting complete.")

ret, camera_mtx, camera_dist_coeff, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
new_camera_mtx, valid_pix_roi =cv2.getOptimalNewCameraMatrix(camera_mtx,camera_dist_coeff,(img_width,img_height),1,(img_width,img_height))
# save a human readable form
output_filename = "calibation_output.txt"
output_path_file = output_path + os.sep + output_filename
print("\nSaving human readable camera parameters to output directory as: " + output_filename)
output_file = open(output_path_file, "w+")
output_file.write("Image Dimensions:\n" + str(img_size))
output_file.write("\n\nCamera Matrix:\n" + str(camera_mtx))
output_file.write("\n\nCamera Distortion Coefficients:\n" + str(camera_dist_coeff))
output_file.write("\n\nNew Camera Matrix:\n" + str(new_camera_mtx))
output_file.write("\n\nOutput rectangle outlining all-good-pixels after undistort:\n" + str(valid_pix_roi))
output_file.close()
print("Saved.")

# save camera Matrix
print("\nSaving some .npy arrays to output directory:")
img_size_filename = "image_size.npy"
camera_mtx_filename = "camera_mtx.npy"
camera_dist_coeff_filename = "camera_dist_coeff.npy"
new_camera_mtx_filename = "new_camera_mtx.npy"
valid_pix_roi_filename = "valid_pix_roi.npy"

print(img_size_filename)
np.save(output_path + os.sep + img_size_filename, img_size)
print(camera_mtx_filename)
np.save(output_path + os.sep + camera_mtx_filename, camera_mtx)
print(camera_dist_coeff_filename)
np.save(output_path + os.sep + camera_dist_coeff_filename, camera_dist_coeff)
print(new_camera_mtx_filename)
np.save(output_path + os.sep + new_camera_mtx_filename, new_camera_mtx)
print(valid_pix_roi_filename)
np.save(output_path + os.sep + valid_pix_roi_filename, valid_pix_roi)
print("Saved.")

print("Done.")
