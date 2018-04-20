# coding=utf-8

# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2


class Shape(object):
    def __init__(self):
        pass

    def midpoint(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
    
    def get_rectangle(self, image, width_range=None, height_range=None):
        # load the image, convert it to grayscale, and blur it slightly
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        _, gray = cv2.threshold(image, 250, 255, cv2.THRESH_BINARY)
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # perform edge detection, then perform a dilation + erosion to
        # close gaps in between object edges
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # find contours in the edge map
        cnts = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        # print len(cnts)
        # # print cnts
        # grb_gray = cv2.cvtColor(edged, cv2.COLOR_GRAY2RGB)
        # cv2.drawContours(grb_gray, cnts, -1, (0,255,0),3)
        # cv2.imshow("binary2", cv2.resize(grb_gray, (540, 960)))
        # cv2.waitKey(0)

        # sort the contours from left-to-right and initialize the
        # 'pixels per metric' calibration variable
        (cnts, _) = contours.sort_contours(cnts)

        # loop over the contours individually
        rectangles = []
        for c in cnts:
            # if the contour is not sufficiently large, ignore it
            # if cv2.contourArea(c) < 100:
            #     continue

            # compute the rotated bounding box of the contour
            # orig = gray.copy()
            box = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")

            # unpack the ordered bounding box, then compute the midpoint
            # between the top-left and top-right coordinates, followed by
            # the midpoint between bottom-left and bottom-right coordinates
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = self.midpoint(tl, tr)
            (blbrX, blbrY) = self.midpoint(bl, br)

            # compute the midpoint between the top-left and top-right points,
            # followed by the midpoint between the top-righ and bottom-right
            (tlblX, tlblY) = self.midpoint(tl, bl)
            (trbrX, trbrY) = self.midpoint(tr, br)

            width = int(blbrX) - int(tltrX)
            height = int(tlblY) - int(trbrY)
            # print(width, height)

            if width_range[0] < width < width_range[1] and height_range[0] < height < height_range[1]:
                rectangles.append((int(tltrX), int(trbrY), int(blbrX), int(tlblY), width, height))
            else:
                continue

            # # draw lines between the midpoints
            # cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
            # cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)

            # show the output image
            # temp_img = cv2.resize(orig , (540, 960))
            # cv2.imshow("Image", temp_img)
            # cv2.waitKey(0)

        return list(set(rectangles))
        