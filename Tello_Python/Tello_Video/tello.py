import socket
import threading
import time
import cv2

class Tello:
    def __init__(self, local_ip, local_port, command_timeout=.3, tello_ip='192.168.10.1', tello_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.

        :param local_ip (str): Local IP address to bind.
        :param local_port (int): Local port to bind.
        :param command_timeout (int|float): Number of seconds to wait for a response to a command.
        :param tello_ip (str): Tello IP.
        :param tello_port (int): Tello port.
        """
        self.abort_flag = False
        self.command_timeout = command_timeout
        self.response = None
        self.frame = None  # numpy array BGR -- current camera output frame
        self.is_freeze = False  # freeze current camera output
        self.last_frame = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.tello_address = (tello_ip, tello_port)
        self.local_video_port = 11111  # port for receiving video stream
        self.last_height = 0
        self.socket.bind((local_ip, local_port))

        # to receive video -- send cmd: command, streamon
        self.socket.sendto(b'command', self.tello_address)
        print('sent: command')
        self.socket.sendto(b'streamon', self.tello_address)
        print('sent: streamon')

        # thread-1 for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True # close with main thread
        self.receive_thread.start()

        # thread-2 for receiving video
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True # close with main thread
        self.receive_video_thread.start()

        time.sleep(5)


    def __del__(self):
        self.socket.close()

    def read(self):
        """Return the frame from camera.
        Return None if no frame
        """
        if self.is_freeze:
            return self.last_frame
        else:
            return self.frame

    def video_freeze(self, is_freeze=True):
        """Pause video output -- set is_freeze to True"""
        self.is_freeze = is_freeze
        if is_freeze:
            self.last_frame = self.frame

    def _receive_thread(self):
        """Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned.
        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)
                # print(self.response)
            except socket.error as exc:
                print("Caught exception socket.error : %s" % exc)

    def _receive_video_thread(self):
        video_ip = f'udp://0.0.0.0:{self.local_video_port}'
        video_capture = cv2.VideoCapture(video_ip)
        retval, self.frame = video_capture.read()
        while retval:
            retval, frame = video_capture.read()
            self.frame = frame # BGR
            # self.frame = frame[..., ::-1]  # From BGR to RGB


    def send_command(self, command):
        """
        Send a command to the Tello and wait for a response.

        :param command: Command to send.
        :return (str): Response from Tello. ('OK' or 'FALSE'.)
        """

        print(">> send cmd: {}".format(command))
        self.abort_flag = False
        timer = threading.Timer(self.command_timeout, self.set_abort_flag)

        self.socket.sendto(command.encode('utf-8'), self.tello_address)

        timer.start()
        while self.response is None:
            if self.abort_flag is True:
                break
        timer.cancel()

        if self.response is None:
            response = 'none_response'
        else:
            response = self.response.decode('utf-8')

        self.response = None

        return response

    def set_abort_flag(self):
        """
        Sets self.abort_flag to True.
        Used by the timer in Tello.send_command() to indicate to that a response
        timeout has occurred.
        """
        self.abort_flag = True

    def takeoff(self):
        return self.send_command('takeoff')

    def speed(self, speed):
        """
        Sets speed.
        Args:
            speed: 1 to 100 centimeters/second.
        """
        return self.send_command(f'speed {int(speed)}')

    def cw(self, degrees):
        """
        Rotates clockwise.
        Args:
            degrees (int): Degrees to rotate, 1 to 360.
        """
        return self.send_command('cw %s' % degrees)

    def ccw(self, degrees):
        """
        Rotates counter-clockwise.
        Args:
            degrees (int): Degrees to rotate, 1 to 360.
        """
        return self.send_command('ccw %s' % degrees)

    def flip(self, direction):
        """
        Flips.
        Args:
            direction (str): Direction to flip, 'l', 'r', 'f', 'b'.
        """
        return self.send_command('flip %s' % direction)

    def get_response(self):
        response = self.response
        return response

    def get_height(self):
        """Returns height(dm) of tello.
        Returns:
            int: Height(dm) of tello.
        """
        height = self.send_command('height?')
        height = str(height)
        height = filter(str.isdigit, height)
        try:
            height = int(height)
            self.last_height = height
        except:
            height = self.last_height
            pass
        return height

    def get_battery(self):
        """ Returns percent battery life remaining. (%) """
        battery = self.send_command('battery?')
        try:
            battery = int(battery)
        except:
            pass
        return battery

    def get_flight_time(self):
        # Returns the number (int) of seconds elapsed during flight.
        flight_time = self.send_command('time?')

        try:
            flight_time = int(flight_time)
        except:
            pass

        return flight_time

    def get_speed(self):
        """Returns the current speed (m/s).
        """
        speed = self.send_command('speed?')

        try:
            speed = int(speed)
        except:
            pass
        return speed

    def land(self):
        return self.send_command('land')

    def move(self, direction, distance):
        """Moves in a direction for a distance.

        This method expects meters or feet. The Tello API expects distances
        from 20 to 500 centimeters.

        Args:
            direction (str): Direction to move,
                'forward', 'back', 'right', 'left', 'up', 'down'.
            distance (int|float): Distance to move.
        """
        distance = int(distance)
        return self.send_command('%s %s' % (direction, distance))


    def keyboard(self, key):
        print("key:", key)
        distance = 20
        degree = 30
        if key == ord('1'):
            self.takeoff()
        if key == ord('2'):
            self.land()

        if key == ord('i'):
            self.move('forward', distance)
            print("forward!!!!")
        if key == ord('k'):
            self.move('back', distance)
            print("backward!!!!")
        if key == ord('j'):
            self.move('left', distance)
            print("left!!!!")
        if key == ord('l'):
            self.move('right' ,distance)
            print("right!!!!")
        if key == ord('s'):
            self.move('down', distance)
            print("down!!!!")
        if key == ord('w'):
            self.move('up', distance)
            print("up!!!!")
        if key == ord('d'):
            self.cw(degree)
            print("rotate!!!!")
        if key == ord('a'):
            self.ccw(degree)
            print("counter rotate!!!!")

        if key == ord('h'):
            print(self.get_height())
        if key == ord('b'):
            print(self.get_battery())
        if key == ord('r'):
            print(self.get_response())
