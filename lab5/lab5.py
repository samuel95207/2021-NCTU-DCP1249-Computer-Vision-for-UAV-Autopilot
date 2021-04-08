import cv2
import numpy as np
import time

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Tello_Python.Tello_Video.tello as tello


cameraMode = 'drone'

f = cv2.FileStorage("calibration.yaml", cv2.FILE_STORAGE_READ)
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


# Get Images
while True:
    if(cameraMode == 'drone'):
        frame = drone.read()
    elif(cameraMode == 'webcam'):
        _, frame = cap.read()

    markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(
        frame, dictionary, parameters=parameters)

    if(not isinstance(markerIds, type(None))):
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)

        rvec, tvec, _objPoints = \
            cv2.aruco.estimatePoseSingleMarkers(
                markerCorners, 15, intrinsic, distortion)

        frame = \
            cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec, tvec, 10)

        string = f"x: {tvec[0][0][0]}  y: {tvec[0][0][1]} z: {tvec[0][0][2]}"

        cv2.putText(frame, string, (10, 10), cv2.FONT_HERSHEY_DUPLEX,
                    0.5, (0, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('frame', frame)
    cv2.waitKey(30)
