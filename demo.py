import time
from time import perf_counter

import cv2
import numpy as np
from visionapi.messages_pb2 import VideoFrame
from visionlib.pipeline.tools import get_raw_frame_data

from video_source_py.videosource import VideoSource, VideoSourceConfig

VIDEO_URI = 'rtsp://localhost:8554/ondemand-4k'

config = VideoSourceConfig(id='video1', uri=VIDEO_URI, log_level='DEBUG')

source = VideoSource(config)

cv2.namedWindow('default', cv2.WINDOW_NORMAL)
cv2.resizeWindow('default', 1920, 1080)

while True:
    start = perf_counter()
    frame_raw = source.get()
    if frame_raw is None:
        time.sleep(0.01)
        continue

    frame_retrieval = perf_counter()
    vf = VideoFrame()
    vf.ParseFromString(frame_raw)

    frame = get_raw_frame_data(vf)
    frame_decoding = perf_counter()
        
    cv2.imshow('default', frame)
    if cv2.waitKey(1) == ord('q'):
        break
    frame_display = perf_counter()
    print(f'Retrieve {frame_retrieval-start:.4f}, Decode {frame_decoding-frame_retrieval:.4f}, Display {frame_display-frame_decoding:.4f}, Total {perf_counter()-start:.4f}')

source.close()
cv2.destroyAllWindows()
