import multiprocessing as mp
import queue
import time
from ctypes import c_bool

import cv2

from .config import VideoSourceConfig


class VideoSource:
    def __init__(self, config: VideoSourceConfig, frame_queue: mp.Queue) -> None:
        if config.__class__.__name__ != 'VideoSourceConfig':
            raise TypeError('Config must be of type VideoSourceConfig')
        self.config = config
        self.running = mp.Value(c_bool, True)
        self.video_loop = _VideoLoop(self.running, frame_queue, config.uri)

    def start(self):
        self.video_loop.start()

    def stop(self):
        self.running.value = False
        # print('Calling join ', mp.current_process().pid)
        # self.video_loop.join()
        # print('Called join')

class _VideoLoop(mp.Process):
    def __init__(self, running: mp.Value, frame_queue: mp.Queue, uri: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = running
        self.frame_queue = frame_queue
        self.uri = uri

    def run(self):
        cap = cv2.VideoCapture(self.uri)
        if not cap.isOpened():
            raise IOError(f'Cannot open video source at {self.uri}')

        while self.running.value:
            frame_ok, frame = cap.read()
            if not frame_ok:
                break

            try:
                self.frame_queue.put(frame, block=False)
            except queue.Full:
                time.sleep(0.01)

        cap.release()
        # print(mp.current_process().pid)