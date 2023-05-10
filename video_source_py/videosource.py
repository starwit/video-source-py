import multiprocessing as mp
import queue
import time

import cv2
from visionapi.videosource_pb2 import VideoFrame

from .config import VideoSourceConfig
from .errors import *


class VideoSource:
    def __init__(self, config: VideoSourceConfig) -> None:
        if config.__class__.__name__ != 'VideoSourceConfig':
            raise TypeError('Config must be of type VideoSourceConfig')
        self.config = config
        self.stop_event = mp.Event()
        self.frame_queue = mp.Queue(5)
        self.video_loop = _VideoLoop(self.stop_event, self.frame_queue, config.uri)

    def start(self):
        self.video_loop.start()

    def stop(self):
        self.stop_event.set()
    
    def get_frame(self, block=True, timeout=10):
        '''
            Raises NoFrameError if no frame is available (after having waited for timeout if block is True).
            Must not be called after .stop().
        '''
        if self.stop_event.is_set():
            raise ClosedError('VideoSource has already been closed')
        try:
            return self.frame_queue.get(block, timeout)
        except queue.Empty:
            raise NoFrameError(f'No frame has been received after waiting for {timeout}s')

class _VideoLoop(mp.Process):
    def __init__(self, stop_event, frame_queue: mp.Queue, uri: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stop_event = stop_event
        self.frame_queue = frame_queue
        self.uri = uri

    def run(self):
        cap = cv2.VideoCapture(self.uri)
        if not cap.isOpened():
            raise IOError(f'Cannot open video source at {self.uri}')

        while not self.stop_event.is_set():
            frame_ok, frame = cap.read()
            if not frame_ok:
                break

            try:
                self.frame_queue.put(self._to_proto(frame), block=False)
            except queue.Full:
                time.sleep(0.01)

        cap.release()

        # Technically the queue needs to be drained before exiting (otherwise the queue feeder thread will block indefinitely)
        # As we do not care about the data in this case, we can take the shortcut below.
        self.frame_queue.cancel_join_thread()

    def _to_proto(self, frame):
        vf = VideoFrame()
        vf.timestamp_utc_ms = time.time_ns() // 1000
        vf.shape[:] = frame.shape
        vf.frame = frame.tobytes()

        return vf.SerializeToString()

