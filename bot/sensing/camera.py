import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox
import os
import pygame
import sys
import subprocess

class camera:

    def __init__(self):
        self.classNames

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

    classNames = {0: 'background',
                1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
                7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
                13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
                18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
                24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
                32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
                37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
                41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
                46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
                51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
                56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
                61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
                67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
                75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
                80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
                86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}


    def id_class_name(self, class_id, classes):
        for key, value in classes.items():
            if class_id == key:
                return value

    def detect_objects_v2(self, save_image=True):
        tmp_img_name = 'tmp_img.jpg'
        subprocess.Popen("sudo fswebcam "+tmp_img_name,
                         shell=True).communicate()
        # Loading model
        model = cv2.dnn.readNetFromTensorflow('models/frozen_inference_graph.pb',
                                            'models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        image = cv2.imread(tmp_img_name)

        image_height, image_width, _ = image.shape

        model.setInput(cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=True))
        output = model.forward()

        for detection in output[0, 0, :, :]:
            confidence = detection[2]
            if confidence > .5:
                class_id = detection[1]
                class_name=self.id_class_name(class_id,self.classNames)
                print(str(str(class_id) + " " + str(detection[2])  + " " + class_name))
                if save_image:
                    box_x = detection[3] * image_width
                    box_y = detection[4] * image_height
                    box_width = detection[5] * image_width
                    box_height = detection[6] * image_height
                    cv2.rectangle(image, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (23, 230, 210), thickness=1)
                    cv2.putText(image,class_name ,(int(box_x), int(box_y+.05*image_height)),cv2.FONT_HERSHEY_SIMPLEX,(.0005*image_width),(0, 0, 255))
                    file_name = class_name + ".jpg"
                    cv2.imwrite(file_name,image)
                    print('Saved detected picture to', file_name)
