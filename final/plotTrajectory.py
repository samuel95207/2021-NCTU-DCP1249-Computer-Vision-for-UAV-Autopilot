import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import os
import json


def parseNvm(filename, fps):
    file = open(filename)

    version = file.readline()
    emptyLine = file.readline()
    trajectoryCount = int(file.readline())

    # print(version)
    # print(trajectoryCount)

    cameraTrajectory = [None for i in range(trajectoryCount)]

    for i in range(trajectoryCount):
        line = file.readline()
        lineData = line.split(" ")
        # print(lineData)

        imgFilename = lineData[0]
        cameraPos = [float(i) for i in lineData[6:9]]

        imgIndex = int(imgFilename.split(".")[0])-1

        second = round(imgIndex*(1/fps), 6)

        # if(second > 40 and second < 70):
        #     print(f'{second} {cameraPos}')

        cameraTrajectory[imgIndex] = (round(second, 6), cameraPos)

    return cameraTrajectory


def parseOrbSlam(filename):
    file = open(filename)
    lines = file.readlines()

    cameraTrajectory = []

    for line in lines:
        lineData = line.split(" ")

        second = lineData[0]
        cameraPos = [float(i) for i in lineData[1:4]]

        cameraTrajectory.append((second, cameraPos))

    return cameraTrajectory


def orbslamTransform(trajectory, params):
    cameraTrajectory = []

    for item in trajectory:
        time = item[0]
        pos = item[1]
        x = pos[0]
        y = pos[1]
        z = pos[2]

        xDeg = params["degree"][0]
        yDeg = params["degree"][1]
        zDeg = params["degree"][2]

        xOffset = params["offset"][0]
        yOffset = params["offset"][1]
        zOffset = params["offset"][2]

        xScale = params["scale"][0]
        yScale = params["scale"][1]
        zScale = params["scale"][2]

        xRad = xDeg * np.pi / 180
        yRad = yDeg * np.pi / 180
        zRad = zDeg * np.pi / 180

        posMatrix = np.array([[x],
                              [y],
                              [z]])

        scaleMatrix = np.array([[xScale, 0, 0],
                                [0, yScale, 0],
                                [0, 0, zScale]])

        XrotateMatrix = np.array([[1, 0, 0],
                                  [0, np.cos(xRad), -np.sin(xRad)],
                                  [0, np.sin(xRad), np.cos(xRad)]])

        YrotateMatrix = np.array([[np.cos(yRad), 0, np.sin(yRad)],
                                  [0, 1, 0],
                                  [-np.sin(yRad), 0, np.cos(yRad)]])

        ZrotateMatrix = np.array([[np.cos(zRad), -np.sin(zRad), 0],
                                  [np.sin(zRad), np.cos(zRad), 0],
                                  [0, 0, 1]])

        shiftMatrix = np.array([[xOffset],
                                [yOffset],
                                [zOffset]])

        # newPos = (-4*x+0.2, -4*y-1.8, z)
        transferMatrix = \
            np.matmul(ZrotateMatrix,
                      np.matmul(YrotateMatrix,
                                np.matmul(XrotateMatrix, scaleMatrix)))

        # transferMatrix = np.array([[-1.46862857,  5.78274528, 12.50658204],
        #                           [2.43946566, 10.77358724, 12.62022154],
        #                           [-4.53691127, -13.3943088,  -16.25176196]])

        # shiftMatrix = np.array([[-3.10366568],
        #                         [ -1.46793762],
        #                         [ 2.64887193]])


        newPosMatrix = np.matmul(transferMatrix, posMatrix) + shiftMatrix


        newPos = (newPosMatrix[0][0], newPosMatrix[1][0], newPosMatrix[2][0])
        cameraTrajectory.append((time, newPos))

    return cameraTrajectory


def renderGraph(figure, colmapTrajectory, orbSlamTrajectory):
    colmapPosColumns = ([item[1][0] for item in colmapTrajectory], [item[1][1]
                                                                    for item in colmapTrajectory], [item[1][2] for item in colmapTrajectory])
    orbSlamPosColumns = ([item[1][0] for item in orbSlamTrajectory], [item[1][1]
                                                                      for item in orbSlamTrajectory], [item[1][2] for item in orbSlamTrajectory])

    ax_xy = figure.add_subplot(2, 2, 1)
    ax_xz = figure.add_subplot(2, 2, 2)
    ax_yz = figure.add_subplot(2, 2, 3)
    ax_3d = figure.add_subplot(2, 2, 4, projection='3d')

    ax_xy.scatter(colmapPosColumns[0],
                  colmapPosColumns[1], c="red", marker='.', s=1, linewidths=1)
    ax_xy.scatter(orbSlamPosColumns[0],
                  orbSlamPosColumns[1], c="blue", marker='.', s=1, linewidths=1)

    ax_xz.scatter(colmapPosColumns[0],
                  colmapPosColumns[2], c="red", marker='.', s=1, linewidths=1)
    ax_xz.scatter(orbSlamPosColumns[0],
                  orbSlamPosColumns[2], c="blue", marker='.', s=1, linewidths=1)

    ax_yz.scatter(colmapPosColumns[1],
                  colmapPosColumns[2], c="red", marker='.', s=1, linewidths=1)
    ax_yz.scatter(orbSlamPosColumns[1],
                  orbSlamPosColumns[2], c="blue", marker='.', s=1, linewidths=1)

    ax_3d.scatter(colmapPosColumns[0], colmapPosColumns[1],
                  colmapPosColumns[2], c="red", marker='.', s=1, linewidths=1)
    ax_3d.scatter(orbSlamPosColumns[0], orbSlamPosColumns[1],
                  orbSlamPosColumns[2], c="blue", marker='.', s=1, linewidths=1)

    ax_xy.axis('equal')
    ax_xy.set_xlabel('X')
    ax_xy.set_ylabel('Y')

    ax_xz.axis('equal')
    ax_xz.set_xlabel('X')
    ax_xz.set_ylabel('Z')

    ax_yz.axis('equal')
    ax_yz.set_xlabel('Y')
    ax_yz.set_ylabel('Z')

    ax_3d.set_box_aspect(aspect=(1, 1, 1))
    ax_3d.set_xlabel('X')
    ax_3d.set_ylabel('Y')
    ax_3d.set_zlabel('Z')



class Controller:

    def __init__(self):
        colmapPath = "./trajectory/desk_0611/colmap.nvm"
        orbSlamPath = "./trajectory/desk_0611/orbslam.txt"
        paramPath = './trajectory/desk_0611/param'

        fps = 30

        self.colmapTrajectory = parseNvm(colmapPath, fps)
        self.orbSlamTrajectory = parseOrbSlam(orbSlamPath)
        self.loadParam(paramPath)


        window = tk.Tk()
        window.title('window')
        window.geometry('1000x200')

        self.xRotate = tk.Scale(window, from_=-180, to=180, length=300,
                                orient="horizontal", command=self.updateValue)
        self.yRotate = tk.Scale(window, from_=-180, to=180, length=300,
                                orient="horizontal", command=self.updateValue)
        self.zRotate = tk.Scale(window, from_=-180, to=180, length=300,
                                orient="horizontal", command=self.updateValue)
        self.xOffset = tk.Scale(window, from_=-5, to=5, resolution=0.1, length=300,
                                orient="horizontal", command=self.updateValue)
        self.yOffset = tk.Scale(window, from_=-5, to=5, resolution=0.1, length=300,
                                orient="horizontal", command=self.updateValue)
        self.zOffset = tk.Scale(window, from_=-5, to=5, resolution=0.1, length=300,
                                orient="horizontal", command=self.updateValue)
        self.scale = tk.Scale(window, from_=-5, to=5, resolution=0.1, length=300, 
                                orient="horizontal", command=self.updateValue)
        self.saveParamButton = tk.Button(window, text="Save Param", command=lambda:self.saveParam(paramPath))

        self.xRotate.grid(column=0, row=0)
        self.yRotate.grid(column=1, row=0)
        self.zRotate.grid(column=2, row=0)
        self.xOffset.grid(column=0, row=1)
        self.yOffset.grid(column=1, row=1)
        self.zOffset.grid(column=2, row=1)
        self.scale.grid(column=0, row=2)
        self.saveParamButton.grid(column=1, row=2)



        self.xRotate.set(self.param['degree'][0])
        self.yRotate.set(self.param['degree'][1])
        self.zRotate.set(self.param['degree'][2])
        self.xOffset.set(self.param['offset'][0])
        self.yOffset.set(self.param['offset'][1])
        self.zOffset.set(self.param['offset'][2])
        self.scale.set(self.param['scale'][0])




        transferOrbSlamTrajectory = orbslamTransform(
            self.orbSlamTrajectory, self.param)

        self.figure, self.axs = plt.subplots(2, 2)
        renderGraph(self.figure, self.colmapTrajectory,
                    transferOrbSlamTrajectory)
        plt.show(block=False)

        window.mainloop()

    def updateValue(self, pos):
        # plt.close()

        self.param = {
            "offset":
            (self.xOffset.get(), self.yOffset.get(), self.zOffset.get()),
            "degree":
            (self.xRotate.get(), self.yRotate.get(), self.zRotate.get()),
            "scale": (self.scale.get(), self.scale.get(), self.scale.get())
        }

        transferOrbSlamTrajectory = orbslamTransform(
            self.orbSlamTrajectory, self.param)

        self.figure.clear()
        renderGraph(self.figure, self.colmapTrajectory,
                    transferOrbSlamTrajectory)

        plt.draw()

        # plt.show(block=False)


    def loadParam(self, filepath):
        if(os.path.exists(filepath)):
            file = open(filepath)
            self.param = json.load(file)
        else:
            self.param = {
            "offset":
            (-2.9, -1.3, 1.6),
            "degree":
            (74, 55, 125),
            "scale": (4.5, 4.5, 4.5)
        }

    def saveParam(self, filepath):
        file = open(filepath,'w')
        json.dump(self.param, file)





myControl = Controller()


# 67.4  [1.74794, -1.38784, 2.74392] -0.3748021 -0.6775266 0.6571839
# 51.0  [-0.871686, 1.41934, -2.61509] 0.9050288 -0.5900814 0.5575801
# 42.9  [-3.26053, -0.71568, 1.18936]  0.3260848 -0.0745549 0.0602215
# 61.6  [-3.00876, -0.673189, 1.24175]  0.2542186 -0.0603289 0.0653356
