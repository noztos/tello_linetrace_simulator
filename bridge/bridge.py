from collections import OrderedDict
from enum import Enum
import airsim
import math
import numpy as np
import socket
import subprocess
import threading
import time

CONTROL_UDP_PORT = 8889
STATE_UDP_PORT = 8890
VIDEO_UDP_PORT = 11111

class Mode(Enum):
    BINARY = 0
    SDK = 1

class VideoStream(Enum):
    OFF = 0
    ON = 1

class TelloAirSimBridge:
    def __init__(self):
        self.lock = threading.Lock()
        self._running = False
        self._mode = Mode.BINARY
        self._controller_ip = None
        self._video_stream = VideoStream.OFF
        self.control_comm_thread = threading.Thread(target = self._control_comm_proc)
        self.state_comm_thread = threading.Thread(target = self._state_comm_proc)
        self.video_comm_thread = threading.Thread(target = self._video_comm_proc)

    def wait_for_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                s.connect(('127.0.0.1', 41451))
                s.close()
                return
            except socket.error as e:
                time.sleep(1)

    @property
    def running(self):
        with self.lock:
            return self._running

    @running.setter
    def running(self, value):
        with self.lock:
            self._running = value

    @property
    def mode(self):
        with self.lock:
            return self._mode

    @property
    def controller_ip(self):
        with self.lock:
            return self._controller_ip

    def set_mode_and_controller_ip(self, mode, controller_ip):
        with self.lock:
            self._mode = mode
            self._controller_ip = controller_ip

    @property
    def video_stream(self):
        with self.lock:
            return self._video_stream

    @video_stream.setter
    def video_stream(self, value):
        with self.lock:
            self._video_stream = value

    def start(self):
        self.running = True
        self.control_comm_thread.start()
        self.state_comm_thread.start()
        self.video_comm_thread.start()

    def stop(self):
        self.running = False
        self.control_comm_thread.join()
        self.state_comm_thread.join()
        self.video_comm_thread.join()


    def _control_comm_proc(self):
        def _move_to_position(x, y, z):
            POS_SCALE = 5
            _x =  POS_SCALE * 0.01 * x
            _y =  POS_SCALE * 0.01 * y
            _z =  POS_SCALE * 0.01 * z
            state = airsim_client.getMultirotorState()
            pos = state.kinematics_estimated.position
            airsim_client.moveToPositionAsync(pos.x_val + _x, pos.y_val + _y, pos.z_val + _z, 1.0)

        rc_time  = time.time()
        def _move_by_velocity(vx, vy, vz, yaw):
            V_SCALE = 0.01
            YAW_SCALE = 0.1
            _vx = V_SCALE * vx
            _vy = V_SCALE * vy
            _vz = V_SCALE * vz
            _yaw_mode = {'is_rate': True, 'yaw_or_rate': YAW_SCALE * yaw}
            nonlocal rc_time
            if time.time() - rc_time > 0.5:
                rc_time = time.time()
                airsim_client.moveByVelocityBodyFrameAsync(_vx, _vy, _vz, 1.0, yaw_mode = _yaw_mode)

        def _cmd_command(args):
            self.set_mode_and_controller_ip(Mode.SDK, addr[0])
            return 'ok'

        def _cmd_takeoff(args):
            # Tello auto takeoff
            airsim_client.takeoffAsync()
            return 'ok'

        def _cmd_land(args):
            # Tello auto land
            airsim_client.landAsync()
            return 'ok'

        def _cmd_streamon(args):
            # Set video stream on
            self.video_stream = VideoStream.ON
            return 'ok'

        def _cmd_streamoff(args):
            # Set video stream off
            self.video_stream = VideoStream.OFF
            return 'ok'

        def _cmd_up(args):
            # Tello fly up with distance x cm
            # x: 20-500
            x = float(args[0])
            _move_to_position(0, 0, -x)
            return 'ok'

        def _cmd_down(args):
            # Tello fly down with distance x cm
            # x: 20-500
            x = float(args[0])
            _move_to_position(0, 0, +x)
            return 'ok'

        def _cmd_left(args):
            # Tello fly left with distance x cm
            # x: 20-500
            x = float(args[0])
            _move_to_position(0, -x, 0)
            return 'ok'

        def _cmd_right(args):
            # Tello fly right with distance x cm
            # x: 20-500
            x = float(args[0])
            _move_to_position(0, +x, 0)
            return 'ok'

        def _cmd_forward(args):
            # Tello fly forward with distance x cm
            # x: 20-500
            x = float(args[0])
            _move_to_position(+x, 0, 0)
            return 'ok'

        def _cmd_back(args):
            # Tello fly back with distance x cm
            # x: 20-500
            x = float(args[0])
            _move_to_position(-x, 0, 0)
            return 'ok'

        def _cmd_rc(args):
            # Send RC control via four channels.
            # a: left/right (-100~100)
            # b: forward/backward (-100~100)
            # c: up/down (-100~100)
            # d: yaw (-100~100)
            a, b, c, d = [float(arg) for arg in args]
            _move_by_velocity(b, a, c, d)
            return 'ok'

        commands = {
            'command'   : _cmd_command,
            'takeoff'   : _cmd_takeoff,
            'land'      : _cmd_land,
            'streamon'  : _cmd_streamon,
            'streamoff' : _cmd_streamoff,
            'up'        : _cmd_up,
            'down'      : _cmd_down,
            'left'      : _cmd_left,
            'right'     : _cmd_right,
            'forward'   : _cmd_forward,
            'back'      : _cmd_back,
            'rc'        : _cmd_rc,
        }

        airsim_client = airsim.MultirotorClient()
        airsim_client.confirmConnection()
        airsim_client.enableApiControl(True)
        airsim_client.armDisarm(True)

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_socket.bind(('', CONTROL_UDP_PORT))
        control_socket.settimeout(0.1)

        while self.running:
            try:
                command, addr = control_socket.recvfrom(1024)
            except socket.timeout:
                continue
            command = command.decode(encoding = 'ASCII')
            func, *args = command.split()
            if func in commands:
                response = commands[func](args)
            else:
                response = 'error'
            control_socket.sendto(response.encode('ASCII'), addr)


    def _state_comm_proc(self):
        def format(name, value):
            fmt = None
            if isinstance(value, int):
                fmt = '{:d}'
            elif isinstance(value, float):
                fmt = '{:.2f}'
            else:
                raise Exception
            return ':'.join([name, fmt.format(value)])

        airsim_client = airsim.MultirotorClient()
        airsim_client.confirmConnection()
        airsim_client.enableApiControl(True)

        state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while self.running:
            if self.mode == Mode.SDK:
                k = airsim_client.getMultirotorState().kinematics_estimated
                pitch, roll, yaw = airsim.utils.to_eularian_angles(k.orientation)
                state = OrderedDict()
                state['pitch'] = int(math.degrees(pitch))
                state['roll']  = int(math.degrees(roll))
                state['yaw']   = int(math.degrees(yaw))
                state['vgx']   = int(100 * k.linear_velocity.x_val)
                state['vgy']   = int(100 * k.linear_velocity.y_val)
                state['vgz']   = int(100 * k.linear_velocity.z_val)
                state['templ'] = int(0)
                state['temph'] = int(0)
                state['tof']   = int(0)
                state['h']     = int(100 * k.position.z_val)
                state['bat']   = float(0.0)
                state['baro']  = int(0)
                state['time']  = int(0)
                state['agx']   = float(k.linear_acceleration.x_val)
                state['agy']   = float(k.linear_acceleration.y_val)
                state['agz']   = float(k.linear_acceleration.z_val)

                data = ':'.join([format(name, value) for name, value in state.items()])
                data = data.encode('ASCII')
                state_socket.sendto(data, (self.controller_ip, STATE_UDP_PORT))
                time.sleep(0.1)


    def _video_comm_proc(self):
        airsim_client = airsim.MultirotorClient()
        airsim_client.confirmConnection()
        airsim_client.enableApiControl(True)

        while self.running:
            if self.mode == Mode.SDK:
                address = f'udp://{self.controller_ip}:{VIDEO_UDP_PORT}'
                command = (
                    'ffmpeg',
                    '-f', 'rawvideo',
                    '-pixel_format', 'bgr24',
                    '-video_size', '960x720',
                    '-framerate', '15',
                    '-i', '-',
                    '-an',
                    '-c:v', 'libx264',
                    '-g', '15',
                    '-preset', 'ultrafast',
                    '-tune', 'zerolatency',
                    '-f', 'mpegts',
                    address)
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                break

        while self.running:
            if self.video_stream == VideoStream.ON:
                requests = [airsim.ImageRequest('0', airsim.ImageType.Scene, False, False)]
                responses = airsim_client.simGetImages(requests)
                response = responses[0]
                frame = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                process.stdin.write(frame.tobytes())
                process.stdin.flush()
        
        process.kill()


def main():
    try:
        bridge = TelloAirSimBridge()
        bridge.wait_for_connection()
        bridge.start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        bridge.stop()


if __name__ == '__main__':
    main()
