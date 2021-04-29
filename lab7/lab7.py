from droneCVUAV import Drone
import cv2
import numpy as np
import time

# constant setup
CALIFILE = 'cali.xml'
# aruco
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters_create()
# read calibration doc
f = cv2.FileStorage(CALIFILE, cv2.FILE_STORAGE_READ)
intrinsic = f.getNode("intrinsic").mat()
distortion = f.getNode("distortion").mat()
# newCamMtx = f.getNode("newcameramtx").mat()
f.release()


def find_all_markerCorners(frame, arucoSize=15, draw=False):
    # find marker
    markerCorners, markerIds, rejectedCandidates = \
        cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
    if(not markerIds is None):
        markerIds = [i[0] for i in markerIds]
        arucos = {}
        for idx, id in enumerate(markerIds):
            arucos[id] = markerCorners[idx]
        return arucos
    return {}
    # rvec, tvec, _objPoints = \
    #     cv2.aruco.estimatePoseSingleMarkers(markerCorner, arucoSize, intrinsic, distortion)
    # if draw:
    #     frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
    #     frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec[0], tvec[0], 10)
    #     cv2.putText(frame, tvec[0].__str__(), (10, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    #     cv2.putText(frame, rvec[0].__str__(), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    # return rvec[0, 0], tvec[0, 0]


def estimatePose(corners, arucoSize=15):
    rvec, tvec, _objPoints = \
        cv2.aruco.estimatePoseSingleMarkers(corners, arucoSize, intrinsic, distortion)
    # frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
    # frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec[0], tvec[0], 10)
    # cv2.putText(frame, tvec[0].__str__(), (10, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    # cv2.putText(frame, rvec[0].__str__(), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    return rvec[0, 0], tvec[0, 0]


def p1(tvec, rvec, drone):
    if tvec is not None:
        # print(tvec[0, 0], tvec[0, 1], tvec[0, 2])
        # xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(tvec[0], tvec[1], tvec[2], rvec[2])
        xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(tvec[0], tvec[1], 80, rvec[2])
    else:
        xspeed, zspeed, yspeed, yawspeed = 0, 0, 0, 0
    drone.send_rc_control(int(xspeed), int(zspeed), int(yspeed), int(yawspeed))


def p2(tvec, rvec, drone):
    if tvec is not None:
        # print(tvec[0, 0], tvec[0, 1], tvec[0, 2])
        xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(0, 0, tvec[2], rvec[2])
        # xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(tvec[0], tvec[1], 80, rvec[2])
    else:
        xspeed, zspeed, yspeed, yawspeed = 0, 0, 0, 0
    drone.send_rc_control(int(xspeed), int(zspeed), int(yspeed), int(yawspeed))


mid = False


def jump(rvec, tvec, drone):
    global mid
    print(tvec[0], tvec[1])
    if mid == False and abs(tvec[0]) > 5 or abs(tvec[1]) > 10:
        xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(tvec[0], tvec[1], 80, rvec[2])
    else:
        mid = True
        if tvec[2] > 100:
            xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(0, 0, tvec[2], rvec[2])
        else:
            drone.stop()
            drone.move_up(80)
            drone.move_forward(150)
            # drone.land()
    return xspeed, zspeed, yspeed, yawspeed


def main():
    # init tello with function we need
    drone = Drone()
    frameReader = drone.background_frame_read

    while not drone.is_flying:
        pass

    # drone.move_up(50)

    # green (phase2)
    # drone.move_forward(50)
    # drone.move_right(150)

    while True:
        frame = cv2.undistort(frameReader.frame, intrinsic, distortion, None, None)
        corners = find_all_markerCorners(frame)

        GUIDE_ID = 0
        JUMP_ID = 4
        TUNNEL_ID = 3
        if GUIDE_ID in corners:
            rvec, tvec = estimatePose(corners[GUIDE_ID])
            # guide
            xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(tvec[0], tvec[1], tvec[2], rvec[2])
        elif TUNNEL_ID in corners:
            rvec, tvec = estimatePose(corners[TUNNEL_ID])
            xspeed, zspeed, yspeed, yawspeed = Drone.flight_control(tvec[0], tvec[1], tvec[2], rvec[2])

        elif JUMP_ID in corners:
            rvec, tvec = estimatePose(corners[JUMP_ID])
            xspeed, zspeed, yspeed, yawspeed = jump(rvec, tvec, drone)
        else:
            xspeed, zspeed, yspeed, yawspeed = 0, 0, 0, 0
        drone.send_rc_control(int(xspeed), int(zspeed), int(yspeed), int(yawspeed))

        cv2.imshow('img', frame)
        cv2.waitKey(33)


main()
