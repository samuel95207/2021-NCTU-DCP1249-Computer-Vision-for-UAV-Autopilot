import Tello_Python.Tello_Video.tello as tello
import cv2
import numpy as np
import time

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

distance = 20
z_threshold = (70, 90)
y_threshold = (-20, 10)
x_threshold = (-10, 10)

pitch_threshold = (-0.15, 0.15)


cameraMode = 'drone'

f = cv2.FileStorage("cali.xml", cv2.FILE_STORAGE_READ)
intrinsic = f.getNode("intrinsic").mat()
distortion = f.getNode("distortion").mat()
f.release()

dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()


if(cameraMode == 'drone'):
    drone = tello.Tello('', 8889)
    time.sleep(10)
elif(cameraMode == 'webcam'):
    cap = cv2.VideoCapture(2)

cap = cv2.VideoCapture(1)


# Get Images
count = 0
while True:
    if(cameraMode == 'drone'):
        frame = drone.read()
        pass
    elif(cameraMode == 'webcam'):
        _, frame = cap.read()

    markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(
        frame, dictionary, parameters=parameters)

    # drone.send_command("command")

    if(not isinstance(markerIds, type(None))):
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

        rvec, tvec, _objPoints = \
            cv2.aruco.estimatePoseSingleMarkers(
                markerCorners, 15, intrinsic, distortion)

        # frame = \
        #     cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec, tvec, 10)

        linear = (round(tvec[0][0][0], 2), round(
            tvec[0][0][1], 2), round(tvec[0][0][2], 2))
        angular = (round(rvec[0][0][0], 2), round(
            rvec[0][0][1], 2), round(rvec[0][0][2], 2))

        string = f"x: {linear[0]}  y: {linear[1]} z: {linear[2]}\nraw: {angular[0]}  yaw: {angular[1]}  pitch: {angular[2]}"

        cv2.putText(frame, string, (10, 10), cv2.FONT_HERSHEY_DUPLEX,
                    0.5, (255, 0, 0), 1, cv2.LINE_AA)

        count += 1
        count %= 4

        if(count == 0):
            if(linear[2] > z_threshold[1]):
                drone.move("forward", distance)
            elif(linear[2] < z_threshold[0]):
                drone.move("back", distance*1.5)
        elif(count == 1):
            if(linear[1] < y_threshold[0]):
                drone.move("up", distance)
            elif(linear[1] > y_threshold[1]):
                drone.move("down", distance)
        elif(count == 2):
            if(linear[0] < x_threshold[0]):
                drone.move("left", distance)
            elif(linear[0] > x_threshold[1]):
                drone.move("right", distance)
        elif(count == 3):
            if(angular[2] > pitch_threshold[1]):
                drone.cw(20)
            elif(angular[2] < pitch_threshold[0]):
                drone.ccw(20)

    key = cv2.waitKey(1)
    if(key != -1):
        print(key)
        drone.keyboard(key)

    cv2.imshow('frame', frame)
    cv2.waitKey(30)
