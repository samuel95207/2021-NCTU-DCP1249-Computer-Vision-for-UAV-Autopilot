from djitellopy import Tello
from pynput import keyboard
# https://pynput.readthedocs.io/en/latest/keyboard.html
import time
import cv2
import numpy as np

""" CVUAV CVUAV CVUAV CVUAV CVUAV CVUAV CVUAV CVUAV CVUAV CVUAV"""

CALI_FILE_DIR = './'
# CALI_FILE_DIR = '../utils/'


class Drone(Tello):
    # aruco
    DICTIONARY = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
    PARAMETERS = cv2.aruco.DetectorParameters_create()

    def __init__(self, name, cali=True, video=True) -> None:
        Tello.__init__(self)
        self.connect()  # command
        print(f'battery: {self.get_battery()}')

        # Video
        if video:
            self.streamon()
            self.get_frame_read()

        # camera calibration - read files
        if cali:
            f = cv2.FileStorage(f'{CALI_FILE_DIR}{name}_cali.xml', cv2.FILE_STORAGE_READ)
            if not f.isOpened():
                print('ERROR: Fail to open calibration file...')
                exit()
            self.intrinsic = f.getNode("intrinsic").mat()
            self.distortion = f.getNode("distortion").mat()
            try:
                self.newCamMtx = f.getNode("newcameramtx").mat()
            except:
                self.newCamMtx = None
            f.release()

        # keyboard control
        self.keyboardMonitor()
        self.joystick_move = False

        # wait for booting
        time.sleep(0.5)
        print('start...')

    def stop(self):
        state = self.get_current_state()
        # forward, x<0; right, y<0; up, z>0
        theta = np.deg2rad(state['yaw'])
        rotate = [[np.cos(theta), -1*np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]]
        vgx, vgy = state['vgx'], state['vgy']
        vec = np.dot([vgx, vgy], rotate)
        self.send_rc_control(int(50*vec[1]), int(50*vec[0]), 0, 0)
        speed = (vgx**2+vgy**2)**0.5
        time.sleep(speed/15)
        self.send_rc_control(0, 0, 0, 0)

    def joystick(self, key):
        speed = 70
        if key == 'o':
            if not self.is_flying:
                self.send_rc_control(0, 0, 0, 0)
                self.takeoff()
        elif key == 'p':
            if self.is_flying:
                self.send_rc_control(0, 0, 0, 0)
                self.land()

        elif key == 'b':
            print(self.get_battery())
        elif key == 'c':
            self.connect(False)
        elif key == 'n':
            self.stop()
        elif key == '0':
            self.emergency()

        if self.is_flying == False:
            return

        # movement control
        self.joystick_move = True
        if key == 'i':
            self.send_rc_control(0, speed, 0, 0)
            # print("forward!!!!")
        elif key == 'k':
            self.send_rc_control(0, -1*speed, 0, 0)
            # print("backward!!!!")
        elif key == 'j':
            self.send_rc_control(-1*speed, 0, 0, 0)
            # print("left!!!!")
        elif key == 'l':
            self.send_rc_control(speed, 0, 0, 0)
            # print("right!!!!")
        elif key == 's':
            self.send_rc_control(0, 0, -1*speed, 0)
            # print("down!!!!")
        elif key == 'w':
            self.send_rc_control(0, 0, speed, 0)
            # print("up!!!!")
        elif key == 'a':
            self.send_rc_control(0, 0, 0, -2*speed)
            # print("counter rotate!!!!")
        elif key == 'd':
            self.send_rc_control(0, 0, 0, 2*speed)
            # print("rotate!!!!")
        else:
            self.joystick_move = False

    def on_press(self, key):
        try:
            # print(f'alphanumeric key {key.char} pressed')
            control_key = key.char
            self.joystick(control_key)
        except AttributeError:
            pass
            # print(f'special key {key} pressed')

    def on_release(self, key):
        # stop moving, hovering
        if self.joystick_move:
            self.send_rc_control(0, 0, 0, 0)
            self.joystick_move = False

        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def keyboardMonitor(self):
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.setDaemon(True)
        listener.start()
        return listener

    def state_monitor(self):
        state = self.get_current_state()
        print(f"pitch: {state['pitch']}, roll: {state['roll']}, yaw: {state['yaw']}")
        print(f"vgx: {state['vgx']}, vgy: {state['vgy']}, vgz: {state['vgz']}")
        theta = np.deg2rad(state['yaw'])
        rotate = [[np.cos(theta), -1*np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]]
        vgx, vgy = state['vgx'], state['vgy']
        speed = (vgx**2+vgy**2)**0.5
        vec = np.dot([vgx, vgy], rotate)
        print(vec)
        print(speed)
        # print(f"agx: {state['agx']}, agy: {state['agy']}, agz: {state['agz']}")
        # print(f"height: {state['h']}, barometer: {state['baro']}, battery: {state['bat']}")
        print()

    """ PID control """
    @staticmethod
    def flight_control(x, y, z, yaw):
        speed_limit = 60
        zspeed = (z - 80) * 1
        xspeed = x * 0.9
        yspeed = (y) * -1.2
        yawspeed = yaw * 40
        zspeed = max(-1*speed_limit, min(speed_limit, zspeed))
        xspeed = max(-1*speed_limit, min(speed_limit, xspeed))
        yspeed = max(-1*speed_limit, min(speed_limit, yspeed))
        yawspeed = max(-1*speed_limit, min(speed_limit, yawspeed))
        return xspeed, zspeed, yspeed, yawspeed

    def PID(self, err, errSum, prevErr, base=0):
        limit = 50
        errSum += err
        P = self.kp * err
        I = self.ki * errSum
        D = self.kd * (err - prevErr)
        result = P + I + D + base
        for i in range(4):
            result[i] = max(-1*limit, min(limit, result[i]))
        prevErr[:] = err
        return result, errSum, prevErr

    """ aruco related """

    def undistort(self, frame):
        frame = cv2.undistort(frame, self.intrinsic, self.distortion, None, self.newCamMtx)
        return frame

    @staticmethod
    def find_arucos(frame):
        markerCorners, markerIds, rejectedCandidates = \
            cv2.aruco.detectMarkers(frame, Drone.DICTIONARY, parameters=Drone.PARAMETERS)
        frame = cv2.aruco.drawDetectedMarkers(frame, markerCorners, markerIds)
        if markerIds is not None:
            markerIds = [i[0] for i in markerIds]
            arucos = {}
            for idx, id in enumerate(markerIds):
                arucos[id] = markerCorners[idx]
            return arucos
        return {}

    def estimatePose(self, corners, arucoSize=15):
        rvec, tvec, _objPoints = \
            cv2.aruco.estimatePoseSingleMarkers(corners, arucoSize, self.intrinsic, self.distortion)
        return rvec[0, 0], tvec[0, 0]
        # frame = cv2.aruco.drawAxis(frame, intrinsic, distortion, rvec[0], tvec[0], 10)


if __name__ == '__main__':
    drone = Drone('TD23', video=1)
    drone.kp = np.array([1.08, 1.2, 1, 25])
    drone.ki = np.array([0.012, 0.015, 0, 0])
    drone.kd = np.array([1.16, 1.05, 1.15, 0])
    err = np.zeros((4,))
    errSum = np.zeros((4,))
    prevErr = np.zeros((4,))
    while True:
        frame = drone.background_frame_read.frame
        arucos = drone.find_arucos(frame)
        if 3 in arucos:
            rvec, tvec = drone.estimatePose(arucos[3], 15)
            print(tvec)
        else:
            pass

        cv2.imshow('img', frame)
        cv2.waitKey(33)



    while not drone.is_flying:
        frame = drone.background_frame_read.frame
        arucos = drone.find_arucos(frame)
        if 4 in arucos:
            rvec, tvec = drone.estimatePose(arucos[4], 8.5)
            cv2.putText(frame, tvec.__str__(), (10, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, rvec.__str__(), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            # break
        cv2.imshow('img', frame)
        cv2.waitKey(33)

    drone.connect()

    while True:
        frame = drone.background_frame_read.frame
        arucos = drone.find_arucos(frame)
        if 4 in arucos:
            rvec, tvec = drone.estimatePose(arucos[4], 8.5)
            cv2.putText(frame, tvec.__str__(), (10, 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, rvec.__str__(), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
            break

        cv2.imshow('img', frame)
        cv2.waitKey(33)

    # max(-1*limit, min(limit, result[i]))
    drone.go_xyz_speed(int(tvec[2]-40), int(-1.24*tvec[0]), int(1.2*(-10-tvec[1])), 100)

    drone.send_rc_control(0, 0, 0, 0)
    drone.land()
    exit()


    mid = False
    moved = True
    while True:
        frame = drone.background_frame_read.frame
        arucos = drone.find_arucos(frame)
        if 4 in arucos:
            rvec, tvec = drone.estimatePose(arucos[4], 15)
        # if 0 in arucos:
        #     rvec, tvec = drone.estimatePose(arucos[0], 8.5)
        #     if abs(rvec[2]) > 0.5:
        #         # err = np.array([0, 0, tvec[2] - 90, rvec[2]])
        #         pass
        #     else:
        #         err = np.array([tvec[0], 0 - tvec[1], tvec[2] - 90, 0])
        #     result, errSum, prevErr = drone.PID(err, errSum, prevErr)
        #     (xspeed, yspeed, zspeed, yawspeed) = result
        #     moved = True
        # elif 4 in arucos:
        #     rvec, tvec = drone.estimatePose(arucos[4], 8.5)
        #     if mid == False and (abs(tvec[0]) > 5 or abs(tvec[1]) > 10):
        #         err = np.array([tvec[0], 0 - tvec[1], 0, rvec[2]])
        #         result, errSum, prevErr = drone.PID(err, errSum, prevErr)
        #         (xspeed, yspeed, zspeed, yawspeed) = result
        #     else:
        #         pass
        #         # mid = True
        #         # if tvec[2] > 100:
        #         #     err = np.array([0, 0, tvec[2] - 80, -1*rvec[2]])
        #         #     result, errSum, prevErr = Drone.PID(err, errSum, prevErr, rvec[2])
        #         #     (xspeed, yspeed, zspeed, yawspeed) = result
        #         # else:
        #         #     drone.stop()
        #         #     drone.move_up(80)
        #         #     drone.move_forward(150)
        #         #     drone.land()
        # else:
        #     if moved:
        #         drone.send_rc_control(0, 0, 0, 0)
        #         moved = False
        # if moved:
        #     drone.send_rc_control(int(xspeed), int(zspeed), int(yspeed), int(yawspeed))

        cv2.imshow('img', frame)
        cv2.waitKey(33)
