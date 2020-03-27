import cv2
import matplotlib.pyplot as plt
from cvlib.object_detection import draw_bbox
import os
import pygame
import sys
import subprocess
from datetime import datetime


class camera:

    # What is the angle, the camera is seeing
    CAMERA_ANGLE_DEGREE = 50

    def __init__(self):
        self.CAMERA_ANGLE_DEGREE
        # Loading model
        self.model = cv2.dnn.readNetFromTensorflow(
            'models/frozen_inference_graph.pb',
            'models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')
        self.classNames

    def take_picture(self, file_name):
        cam = cv2.VideoCapture(0)
        s, image = cam.read()
        cv2.imwrite(file_name, image)
        

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

    def look_for_object(self, obj_name, confidence_threshold=0.5):
        cam = cv2.VideoCapture(0)
        s, image = cam.read()
        image_height, image_width, _ = image.shape

        degree_per_pixel = self.CAMERA_ANGLE_DEGREE / image_width

        self.model.setInput(cv2.dnn.blobFromImage(
            image, size=(300, 300), swapRB=True))
        output = self.model.forward()
        for detection in output[0, 0, :, :]:
            confidence = detection[2]
            if confidence > confidence_threshold:
                class_id = detection[1]
                class_name = self.id_class_name(class_id, self.classNames)
                print('Detected:', class_name)
                if obj_name == class_name:
                    print('Found', obj_name, '!')
                    box_x = detection[3] * image_width
                    box_y = detection[4] * image_height
                    box_width = detection[5] * image_width
                    box_height = detection[6] * image_height
                    print(box_x, box_y, box_width, box_height)

                    box_center_x = box_x + ((box_width - box_x) / 2)
                    image_center_x = image_width / 2
                    x_diff = image_center_x - box_center_x
                    x_diff_scaled = x_diff * degree_per_pixel

                    image_size = image_width * image_height
                    box_size = (box_width - box_x) * (box_height - box_y)
                    box_image_ratio = box_size / image_size

                    print('Image size:', image_size)
                    print('Box size:', box_size)
                    print('Box Image Ratio:', box_image_ratio)

                    print('box_center_x:', box_center_x)
                    print('image_center_x:', image_center_x)
                    print('x_diff:', x_diff)
                    print('x_diff_scaled:', x_diff_scaled)

                    # debugging save image
                    cv2.rectangle(image, (int(box_x), int(box_y)), (int(
                        box_width), int(box_height)), (23, 230, 210),
                        thickness=1)
                    cv2.putText(
                        image, class_name + " | conf.: " + str(confidence*100),
                        (int(box_x), int(
                            box_y+.05*image_height)), cv2.FONT_HERSHEY_SIMPLEX,
                        (.001*image_width), (0, 0, 255))
                    file_name = "detected_objects/" + \
                        datetime.now().strftime("%Y-%m-%dT%H:%M:%S_") + \
                        class_name + ".jpg"
                    cv2.imwrite(file_name, image)
                    print(datetime.now(), 'Saved detected picture to',
                          file_name)
                    # debugging save image

                    return x_diff_scaled, box_image_ratio

                else:
                    continue
        return 0, 0

    def detect_objects_v2(self, save_image=True):
        print(datetime.now(), 'Taking picture')
        # 0 -> index of camera
        cam = cv2.VideoCapture(0)
        s, image = cam.read()
        print(datetime.now(), 'Took picture')

        image_height, image_width, _ = image.shape

        self.model.setInput(cv2.dnn.blobFromImage(
            image, size=(300, 300), swapRB=True))
        output = self.model.forward()

        for detection in output[0, 0, :, :]:
            confidence = detection[2]
            if confidence > .3:
                class_id = detection[1]
                class_name = self.id_class_name(class_id, self.classNames)
                print(datetime.now(), 'Detected:',
                      class_name, '| Conf.:', detection[2])
                if save_image:
                    box_x = detection[3] * image_width
                    box_y = detection[4] * image_height
                    box_width = detection[5] * image_width
                    box_height = detection[6] * image_height
                    cv2.rectangle(image, (int(box_x), int(box_y)), (int(
                        box_width), int(box_height)), (23, 230, 210),
                        thickness=1)
                    cv2.putText(
                        image, class_name + " | conf.: " + str(confidence*100),
                        (int(box_x), int(
                            box_y+.05*image_height)), cv2.FONT_HERSHEY_SIMPLEX,
                        (.001*image_width), (0, 0, 255))
                    file_name = "detected_objects/" + \
                        datetime.now().strftime("%Y-%m-%dT%H:%M:%S_") + \
                        class_name + ".jpg"
                    cv2.imwrite(file_name, image)
                    print(datetime.now(), 'Saved detected picture to',
                          file_name)
