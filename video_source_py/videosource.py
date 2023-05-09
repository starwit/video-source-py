from .config import VideoSourceConfig
import time
import cv2
from typing import Callable
from multiprocessing import Value, Queue
from ctypes import c_bool

class VideoSource:
    def __init__(self, config: VideoSourceConfig, frame_queue: Queue) -> None:
        if config.__class__.__name__ != 'VideoSourceConfig':
            raise TypeError('Config must be of type VideoSourceConfig')
        self.config = config
        self.frame_queue = frame_queue
        self.running = Value(c_bool, True)

    def run(self):
        cap = cv2.VideoCapture(self.config.uri)
        if not cap.isOpened():
            raise IOError(f'Cannot open video source at {self.config.uri}')

        while self.running.value:
            frame_ok, frame = cap.read()
            if not frame_ok:
                break

            self.frame_queue(frame)

        cap.release()

    def stop(self):
        self.running.value = False

