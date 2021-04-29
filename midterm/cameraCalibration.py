import numpy as np
import cv2
from djitellopy import Tello

FILE_NAME = 'G0_cali.xml'


def cameraCalibration(filename):
    CALI_IMG_NUM = 50
    # termination criteria for cv2.cornerSubPix
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,5,0) // (x, y, 0)
    objp = np.zeros((9*6, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.

    drone = Tello()
    drone.connect()
    drone.streamon()
    drone.get_frame_read()
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # capturing img for calibration
    print('Capturing...')
    cnt = 0
    while(True):
        frame = drone.background_frame_read.frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)
        if ret == True:
            print(f'chessboard_{cnt}')
            cnt += 1
            if cnt > CALI_IMG_NUM:
                break
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            frame = cv2.drawChessboardCorners(frame, (9, 6), corners2, ret)
        cv2.imshow('chessboard', frame)
        key = cv2.waitKey(200)
    cv2.destroyAllWindows()

    # calibration
    print('calibrating...')
    ret, cameraMatrix, distCoeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None)
    # shape[::-1] : reversed slicing
    # refine parameters
    h, w = 720, 960  # telloCam shape
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, (w, h), 0, (w, h))

    f = cv2.FileStorage(filename, cv2.FILE_STORAGE_WRITE)
    f.write("intrinsic", cameraMatrix)
    f.write("distortion", distCoeffs)
    f.write("newcameramtx", newcameramtx)
    f.release()
    print('calibration finished!!')
    exit()


if __name__ == '__main__':
    input(f'Filename = {FILE_NAME}')
    cameraCalibration(FILE_NAME)

# reference:
# 1. camera calibration theory
# https://medium.com/%E6%95%B8%E5%AD%B8%E5%B7%A5%E5%BB%A0/camera-calibration%E7%9B%B8%E6%A9%9F%E6%A0%A1%E6%AD%A3-1d94ffa7cbb4
# 2. opencv example code
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html
