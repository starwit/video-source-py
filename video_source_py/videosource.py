import logging

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-10s %(message)s')
root_logger = logging.getLogger()

import time
from typing import Any

from prometheus_client import Counter, Histogram, Summary
from visionapi.messages_pb2 import Shape, VideoFrame

from .config import VideoSourceConfig
from .framegrabber import FrameGrabber

FRAME_COUNTER = Counter('video_source_frame_counter', 'The number of frames the video source has retrieved from the grabber')
GET_DURATION = Histogram('video_source_get_duration', 'The time it takes from the call of get() until the proto object is returned',
                            buckets=(0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.1, 0.2))
WAIT_NEXT_FRAME_DURATION = Summary('video_source_wait_next_frame_duration', 'The time the video source waits for the next frame in order to meet the fps target')


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

    @GET_DURATION.time()
    def get(self):
        self._source_fps = self._framegrabber.source_fps
        self._wait_next_frame()

        frame = self._framegrabber.get_frame()
        if frame is None:
            time.sleep(0.1)
            return None
        
        FRAME_COUNTER.inc()

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
    
    @WAIT_NEXT_FRAME_DURATION.time()
    def _wait_next_frame(self):
        if self.config.max_fps > 0:
            current_time = time.time()

            wait_target = self._last_frame_ts + 1/self.config.max_fps
            time_to_sleep = wait_target - current_time
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
