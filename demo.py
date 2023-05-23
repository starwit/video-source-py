from video_source_py.videosource import VideoSource, VideoSourceConfig
import numpy as np
from visionapi.videosource_pb2 import VideoFrame
import cv2
from time import perf_counter

VIDEO_URI = 'path/to/your/video'

config = VideoSourceConfig(id='a', name='test', uri=VIDEO_URI, use_source_fps=True)

source = VideoSource(config)
source.start()

while True:
    frame_raw = source.get_frame()

    start = perf_counter()
    vf = VideoFrame()
    vf.ParseFromString(frame_raw)

    frame = np.frombuffer(vf.frame_data, dtype=np.uint8).reshape((vf.shape.height, vf.shape.width, vf.shape.channels))
    stop = perf_counter()
    print(f'{stop - start}')
        
    cv2.imshow('default', frame)
    if cv2.waitKey(1) == ord('q'):
        source.stop()
        break

cv2.destroyAllWindows()
