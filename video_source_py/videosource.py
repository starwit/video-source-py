import logging
import numpy as np

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-10s %(message)s')
root_logger = logging.getLogger()

import time
from typing import Any

import cv2
from prometheus_client import Counter, Histogram, Summary
from visionapi_yq.messages_pb2 import SaeMessage, Shape, VideoFrame

from .config import VideoSourceConfig
from .framegrabber import FrameGrabber

FRAME_COUNTER = Counter('video_source_frame_counter', 'The number of frames the video source has retrieved from the grabber')
GET_DURATION = Histogram('video_source_get_duration', 'The time it takes from the call of get() until the proto object is returned',
                            buckets=(0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.1, 0.2))
WAIT_NEXT_FRAME_DURATION = Summary('video_source_wait_next_frame_duration', 'The time the video source waits for the next frame in order to meet the fps target')
PROTO_SERIALIZATION_DURATION = Summary('video_source_proto_serialization_duration', 'The time it takes to create a serialized output proto')


class VideoSource:
    def __init__(self, config: VideoSourceConfig):
        self.config = config
        root_logger.setLevel(self.config.log_level.value)
        self._logger = logging.getLogger(__name__)
        self._framegrabber = FrameGrabber(config)
        self._source_fps = None
        self._last_frame_ts = 0
        self.frame_id = 0
        self.mask_img = self._load_mask(config.mask_polygon_location) if self.config.mask else None

        if config.jpeg_encode:
            from turbojpeg import TurboJPEG
            self._jpeg = TurboJPEG()

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
        
        if self.config.mask:
            frame = self._apply_mask(frame)
        FRAME_COUNTER.inc()

        self._last_frame_ts = time.time()

        frame = self._resize(frame)
        
        return self._to_proto(frame)

    def close(self):
        self._framegrabber.stop()

    @PROTO_SERIALIZATION_DURATION.time()
    def _to_proto(self, frame):
        msg = SaeMessage()
        msg.frame.source_id = self.config.id
        msg.frame.timestamp_utc_ms = time.time_ns() // 1_000_000
        msg.frame.shape.height = frame.shape[0]
        msg.frame.shape.width = frame.shape[1]
        msg.frame.shape.channels = frame.shape[2]
        if self.config.thread_frame_count:
            msg.frame.frame_id = self._framegrabber.frame_counter.get_counter()

        if self.config.jpeg_encode:
            msg.frame.frame_data_jpeg = self._jpeg.encode(frame, quality=self.config.jpeg_quality)
        else:
            msg.frame.frame_data = frame.tobytes()

        return msg.SerializeToString()
    
    @WAIT_NEXT_FRAME_DURATION.time()
    def _wait_next_frame(self):
        if self.config.max_fps > 0:
            current_time = time.time()

            wait_target = self._last_frame_ts + 1/self.config.max_fps
            time_to_sleep = wait_target - current_time
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    def _resize(self, frame):
        if self.config.scale_width > 0:
            original_width = frame.shape[1]
            scale_factor = self.config.scale_width / original_width
            return cv2.resize(frame, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
        else:
            return frame
        
    def _load_mask(self, mask_polygon_location: str):
        try:
            points = []
            with open(mask_polygon_location, "r") as f:
                for line in f:
                    x, y = map(int, line.strip().split())
                    points.append((x, y))

            mask_img = np.zeros((1440, 2560, 3), dtype=np.uint8)
            if points:
                cv2.fillPoly(mask_img, [np.array(points)], (255, 255, 255))
            return mask_img
        except Exception as e:
            self._logger.error(f"Failed to load mask: {e}")
            return None
        
    def _apply_mask(self, frame):
        return cv2.bitwise_and(frame, self.mask_img)
