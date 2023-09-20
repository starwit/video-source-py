import logging

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-10s %(message)s')
root_logger = logging.getLogger()

import time
from typing import Any

from visionapi.messages_pb2 import Shape, VideoFrame

from .config import VideoSourceConfig
from .framegrabber import FrameGrabber


class VideoSource:
    def __init__(self, config: VideoSourceConfig):
        self.config = config
        root_logger.setLevel(self.config.log_level.value)
        self._logger = logging.getLogger(__name__)
        self._framegrabber = FrameGrabber(self.config.uri)
        self._source_fps = None
        self._last_frame_ts = 0

    def __call__(self, *args, **kwargs) -> Any:
        return self.get()

    def get(self):
        self._source_fps = self._framegrabber.source_fps
        self._wait_next_frame()

        frame = self._framegrabber.get_frame()
        if frame is None:
            return None

        self._last_frame_ts = time.time()
        
        return self._to_proto(frame)

    def close(self):
        self._framegrabber.stop()

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
        if self.config.max_fps is not None:
            current_time = time.time()

            wait_target = self._last_frame_ts + 1/self.config.max_fps
            time_to_sleep = wait_target - current_time
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
