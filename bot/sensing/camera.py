import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox
import os
import pygame
import sys
import subprocess


class camera:

    def detect_objects(self):
        tmp_img_name = 'tmp_img.jpg'
        subprocess.Popen("sudo fswebcam "+tmp_img_name,
                         shell=True).communicate()
        im = cv2.imread(tmp_img_name)
        bbox, label, conf = cv.detect_common_objects(im)
        output_image = draw_bbox(im, bbox, label, conf)
        # cv2.imwrite('obj_detect_output.png',output_image)

        height, width, channels = im.shape

        print('width:', width)
        if len(bbox) < 0:
            print(bbox)
            print('center:', abs(bbox[0][0]-bbox[0]
                                 [2]), abs(bbox[0][1]-bbox[0][3]))
            print(label)
            print(conf)
        else:
            print('Could not detect any objects.')
