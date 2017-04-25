# USAGE
# python resize_images.py
#   --input <image directory>
#   --output <(optional) output directory>
#       if no output directory is given a new output directory will be made at
#       the same level as input directory
#   --width <desired image width>
#   --height <desired image height>
#   --vscale <float to scale vertical by>
#   --hscale <float to scale horizontal by>
#
# NOTE: if only one dimention scale is given, the other will match it and keep
# aspect ratio

import argparse
import sys
import cv2
import glob
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",
	help="path to the image directory")
ap.add_argument("-o", "--output",
	help="path to the (optional) output directory")
ap.add_argument("--width",
	help="desired image width")
ap.add_argument("--height",
	help="desired image height")
ap.add_argument("--hscale",
    help="float to scale horizontal by")
ap.add_argument("--vscale",
    help="float to scale vertical by")
args = vars(ap.parse_args())

print("")
# if an input directory was given
if args.get("input", False):
	input_path = args["input"]
# otherwise, ask the user for an input directory
else:
	input_path = raw_input("Enter the image directory: ")
# make sure the input directory is valid
while(not os.path.isdir(input_path)):
	print("Input directory must exist.")
	input_path = raw_input("Enter the image directory: ")
print("Input directory: [" + input_path + "]")

print("Finding images...")
# get all the jpg and png images
types = (input_path + "*.jpg", input_path + "*.png") # the tuple of file types
images = []
for files in types:
	images.extend(glob.glob(files))
# make sure some images were found
num_images = len(images)
print("Images found in directory: " + str(num_images))
if (num_images <= 0):
    print("No images found.")
    print("Goodbye...")
    quit()
# get the input image size
input_size = cv2.imread(images[0]).shape[:2]
input_height,  input_width = input_size

# make sure they have not over constrained the dimensions
if args.get("width", False) and args.get("hscale", False):
    print("Over constrained horizontal")
    print("Goodbye...")
    quit()
if args.get("height", False) and args.get("vscale", False):
    print("Over constrained vertical")
    print("Goodbye...")
    quit()
if (not args.get("height", False)) and (not args.get("vscale", False)) and (not args.get("width", False)) and (not args.get("hscale", False)):
    print("Underconstrained dimensions")
    print("Goodbye...")
    quit()

# find the output dimensions
output_width = None
output_height = None
output_hscale = None
output_vscale = None
if args.get("width", False):
    output_width = int(args["width"])
    if(output_height == None):
        output_height = int((float(output_width)/input_width)*input_height)
if args.get("height", False):
    output_height = int(args["height"])
    if(output_width == None):
        output_width = int((float(output_height)/input_height)*input_width)
if args.get("hscale", False):
    output_hscale = float(args["hscale"])
    if(output_vscale == None):
        output_vscale = output_hscale
    output_width = int(input_width * output_hscale)
    if(output_height == None):
        output_height = int(input_height * output_vscale)
if args.get("vscale", False):
    output_vscale = float(args["vscale"])
    if(output_hscale == None):
        output_hscale = output_vscale
    if(output_width == None):
        output_width = int(input_width * output_hscale)
    output_height = int(input_height * output_vscale)

print("Output width: " + str(output_width))
print("Output height: " + str(output_height))

# if an output directory was given
if args.get("output", False):
	output_path = args["output"]
else:
    print("No output directory given so one will be created.")
    # create output path simlar to input path
    output_path = input_path.rstrip(os.sep) + "_" + str(output_width) + "x" + str(output_height) + os.sep
print("Output directory: [" + output_path + "]")
# make the output directory
if not os.path.exists(output_path):
    os.makedirs(output_path)

######## Input parsed

# Go through all the images
print("\n\rProcessing " + str(num_images) + " images...")
for img_path_file in images:
    path, filename = os.path.split(img_path_file)
    print(filename)
    img = cv2.imread(img_path_file)

    # choose interpolation based on dimensions
    if (output_width < input_width):
        res = cv2.resize(img, (output_width, output_height), interpolation = cv2.INTER_AREA)
    else:
        res = cv2.resize(img, (output_width, output_height), interpolation = cv2.INTER_LINEAR)

    output_path_file = output_path + filename
    print("Saving image: [" + output_path_file + "]")
    cv2.imwrite(output_path_file, res)
    print("Saved.")

print("\nDone.")
