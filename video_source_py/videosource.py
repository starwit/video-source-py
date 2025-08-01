import logging

logging.basicConfig(format='%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s')
root_logger = logging.getLogger(__name__)

import time
from pathlib import Path
from typing import Any

import redis
import pybase64
import cv2
import numpy as np
from prometheus_client import Counter, Histogram, Summary
from visionapi.sae_pb2 import SaeMessage, Shape, VideoFrame, PositionMessage
from visionapi.common_pb2 import GeoCoordinate

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
        self._source_fps = None
        self._last_frame_ts = 0
        self._mask = None
        if self.config.mask_path is not None:
            self._mask = self._load_mask(self.config.mask_path)

        if config.jpeg_encode:
            from turbojpeg import TurboJPEG
            self._jpeg = TurboJPEG()
        
        self._redis_client = redis.Redis(config.redis.host, config.redis.port)

    def _load_mask(self, path: Path) -> np.ndarray:
        if not path.is_file():
            raise IOError(f'Could not open mask file at {path}')
        mask_original = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        mask = self._resize(mask_original, interpolation=cv2.INTER_NEAREST)
        # Mask needs to be inverted, b/c of how cv2.subtract-based masking works
        return 255 - mask
    
    def start(self):
        self._framegrabber = FrameGrabber(self.config.uri)

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

        frame = self._resize(frame)

        self._apply_mask(frame)
        
        frame = self._to_proto(frame)
        
        if frame is None:
            return None # skip frame       
        
        return frame

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
        if self.config.jpeg_encode:
            msg.frame.frame_data_jpeg = self._jpeg.encode(frame, quality=self.config.jpeg_quality)
        else:
            msg.frame.frame_data = frame.tobytes()
        
        position = self._get_location(msg.frame)
        if position is not None:
            msg.frame.camera_location.CopyFrom(position)
        else:
            if self.config.skip_frames_if_no_position:
                root_logger.debug('no position data - forwarding detections without position')
            else:
                root_logger.error('no position data - not processing Detections')
                return None

        return msg.SerializeToString()
    
    @WAIT_NEXT_FRAME_DURATION.time()
    def _wait_next_frame(self):
        if self.config.max_fps > 0:
            current_time = time.time()

            wait_target = self._last_frame_ts + 1/self.config.max_fps
            time_to_sleep = wait_target - current_time
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

    def _resize(self, frame, interpolation=cv2.INTER_AREA):
        if self.config.scale_width > 0:
            original_width = frame.shape[1]
            scale_factor = self.config.scale_width / original_width
            return cv2.resize(frame, None, fx=scale_factor, fy=scale_factor, interpolation=interpolation)
        else:
            return frame
        
    def _apply_mask(self, frame):
        if self._mask is not None:
            # This works by subtracting the pixel value from itself (i.e. setting it to 0) wherever the mask is not 0
            cv2.subtract(src1=frame, src2=frame, dst=frame, mask=self._mask)
            
    def _get_location(self, frame) -> VideoFrame:
        # read position data and parse it into PositionMessage
        streamPositionMessage = self._redis_client.xrevrange('positionsource:self', count=1)
        decodedPositionMessage = pybase64.b64decode(streamPositionMessage[0][1][b'proto_data_b64'])
        positionMessage = PositionMessage()
        positionMessage.ParseFromString(decodedPositionMessage)
        if positionMessage.fix == False:
            root_logger.debug('no position fix')
            return None
        if abs(positionMessage.timestamp_utc_ms - frame.timestamp_utc_ms) > self.config.max_position_delay:
            root_logger.debug('position data and frame timestamp differ more than ' + str(self.config.max_position_delay))
            return None
        result = GeoCoordinate()
        result.latitude = positionMessage.geo_coordinate.latitude
        result.longitude = positionMessage.geo_coordinate.longitude
        return result