import logging
import time
from typing import Any

import cv2
from visionapi.messages_pb2 import Shape, VideoFrame

from .config import VideoSourceConfig

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s')
logger = logging.getLogger(__name__)


class VideoSource:
    def __init__(self, config: VideoSourceConfig):
        self.config = config
        logger.setLevel(self.config.log_level.value)

        self.cap = None
        self.source_fps = None
        self.last_frame_ts = 0

    def __call__(self, *args, **kwargs) -> Any:
        return self.get()

    def get(self):
        if not self._ensure_videosource():
            time.sleep(self.config.reconnect_backoff_time)
            return None

        self._wait_next_frame()

        frame_ok, frame = self.cap.read()
        if not frame_ok:
            return None

        self.last_frame_ts = time.monotonic_ns()
        
        return self._to_proto(frame)

    def close(self):
        self.cap.release()

    def _ensure_videosource(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.config.uri)
            if self.cap.isOpened():
                self.source_fps = self.cap.get(cv2.CAP_PROP_FPS)
                logger.info(f'Successfully established connection to {self.config.uri}')
                return True
            else:
                logger.warn(f'Could not open source at {self.config.uri}')
                return False

        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            logger.warn(f'Source not available anymore at {self.config.uri}')
            return False
        
        return True

    def _to_proto(self, frame):
        vf = VideoFrame()
        vf.source_id = self.config.id
        vf.timestamp_utc_ms = time.time_ns() // 1_000_000
        shape = Shape()
        shape.height, shape.width, shape.channels = frame.shape[0], frame.shape[1], frame.shape[2]
        vf.shape.CopyFrom(shape)
        vf.frame_data = frame.tobytes()

        return vf.SerializeToString()
    
    def _wait_next_frame(self):
        if self.config.use_source_fps and self.source_fps > 0:
            current_time = time.monotonic_ns()
            frame_time = 1/self.source_fps * 1_000_000_000

            wait_target = self.last_frame_ts + frame_time
            time_to_sleep = wait_target - current_time
            if time_to_sleep > 0:
                time.sleep(time_to_sleep / 1_000_000_000)
