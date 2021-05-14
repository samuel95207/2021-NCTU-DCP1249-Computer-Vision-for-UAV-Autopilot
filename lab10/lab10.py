from droneCVUAV import Drone
import cv2
import numpy as np
import time

drone = Drone('G1')

drone.kp = np.array([0.9, 1.25, 0.75, 25])
drone.ki = np.array([0.011, 0.015, 0, 0])
drone.kd = np.array([1.25, 1, 1.25, 0])

err = np.zeros((4,))
errSum = np.zeros((4,))
prevErr = np.zeros((4,))

""" 0. take off """
while not drone.is_flying:
    frame = drone.background_frame_read.frame
    cv2.imshow('drone', frame)
    cv2.waitKey(50)
drone.move_up(30)
""" 1. aimmed """
CENTER_ID = 4
moved = True
while True:
    frame = drone.background_frame_read.frame
    arucos = drone.find_arucos(frame)
    if CENTER_ID in arucos:
        # aim the aruco
        rvec, tvec = drone.estimatePose(arucos[CENTER_ID])
        # tune range of aimming
        if abs(tvec[0]) < 15 and abs(tvec[1]) < 10 and (tvec[2] < 85):
            drone.stop()
            break
        err = np.array([tvec[0], 0 - tvec[1], tvec[2] - 80, 0])
        result, errSum, prevErr = drone.PID(err, errSum, prevErr)
        drone.send_rc_control(int(result[0]), int(result[2]), int(result[1]), 0)
        moved = True
    else:
        if moved:
            drone.send_rc_control(0, -15, 0, 0)
            moved = False
    cv2.imshow('drone', frame)
    cv2.waitKey(50)

print('-> aimmed!')


drone.move_right(55)

""" 2. line following """

def lineDetection(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_range = np.array([100, 50, 50])
    upper_range = np.array([140, 255, 255])

    mask = cv2.inRange(hsv, lower_range, upper_range)

    res = cv2.bitwise_and(img, img, mask=mask)

    return res


def grid99(img):
    size = img.shape

    threshold = 0.01
    grid = np.array([[0.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0]])
    x_ratio = [0.33, 0.33, 0.34]
    y_ratio = [0.33, 0.33, 0.34]

    x_pixel = [int(size[1] * x_ratio[0]),
               int(size[1] * x_ratio[1]),
               size[1] - (int(size[1] * x_ratio[0]) + int(size[1] * x_ratio[1]))
               ]

    y_pixel = [int(size[0] * y_ratio[0]),
               int(size[0] * y_ratio[1]),
               size[0] - (int(size[0] * y_ratio[0]) + int(size[0] * y_ratio[1]))
               ]

    x_range = ((0, x_pixel[0]),
               (x_pixel[0], x_pixel[0] + x_pixel[1]),
               (x_pixel[0] + x_pixel[1], size[1])
               )

    y_range = ((0, y_pixel[0]),
               (y_pixel[0], y_pixel[0] + y_pixel[1]),
               (y_pixel[0] + y_pixel[1], size[0])
               )

    for gridx in range(3):
        for gridy in range(3):
            count = 0
            blueCount = 0
            for x in range(x_range[gridx][0], x_range[gridx][1], 5):
                for y in range(y_range[gridy][0], y_range[gridy][1], 5):
                    count += 1
                    if(img[y][x].all(0)):
                        blueCount += 1

            if(blueCount/count >= threshold):
                grid[gridy][gridx] = 1

    return grid


def line_following(line_pos, dir="right"):
    direction = dir

    # if(line_pos[1, 1] != 1):
    #     # not centered
    #     if(section == 0):
    #         # horizontal
    #         if line_pos[0, 1]:
    #             direction = "sdown"
    #         elif line_pos[2, 1]:
    #             direction = "sup"
    #         else:
    #            direction = "stop"
    #     else:
    #         # vertical
    #         if (line_pos[1, 0]):
    #             direction = "sright"
    #         elif line_pos[2, 1]:
    #             direction = "sleft"
    #         else:
    #            direction = "stop"

    if True:
        # centered
        if line_pos[1, 2] == 1:
            # right
            if line_pos[0, 1] == 1:
                # up

                pass
                # if dir == "left":
                #     direction = "up"
                # elif dir == "down":
                #     if line_pos[1, 0] != 1:
                #         direction = "right"
            elif line_pos[2, 1] == 1:
                # down
                if dir == "left":
                    if line_pos[1, 0] != 1:
                        direction = "down"
                elif dir == "up":
                    direction = "right"

        elif line_pos[1, 0] == 1:
            # left
            if line_pos[0, 1] == 1:
                # up
                if dir == "right":
                    direction = "up"
                elif dir == "down":
                    direction = "left"
            elif line_pos[2, 1] == 1:
                # down
                if dir == "right":
                    direction = "down"
                elif dir == "up":
                    if line_pos[1, 2] != 1:
                        direction = "left"
    return direction


# pos = np.zeros((3,3))
# pos[1,1] = 1
# pos[1,2] = 1
# pos[2,1] = 1
# section = 0
# print(pos)

def move(dir):
    if dir == "up":
        drone.send_rc_control(0,0,15,0)
    elif dir == "down":
        drone.send_rc_control(0,0,-15,0)
    elif dir == "left":
        drone.send_rc_control(-15,0,0,0)
    elif dir == "right":
        drone.send_rc_control(15,0,0,0)

dir = "right"
while True:
    frame = drone.background_frame_read.frame
    res = lineDetection(frame)
    pos = grid99(res)
    new_dir = line_following(pos, dir)
    if new_dir != dir:
        drone.stop()
        pass
    dir = new_dir
    print(dir)
    cv2.imshow('drone', res)
    cv2.waitKey(50)
    # if dir == "up":
    #     drone.move_up(20)
    # elif dir == "down":
    #     drone.move_down(20)
    # elif dir == "left":
    #     drone.move_left(20)
    # elif dir == "right":
    #     drone.move_right(20)
    move(dir)
    arucos = drone.find_arucos(frame)
    if CENTER_ID in arucos:
        drone.land()

