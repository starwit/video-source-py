from video_source_py.videosource import VideoSource, VideoSourceConfig
import numpy as np
from visionapi.messages_pb2 import VideoFrame
import cv2
from time import perf_counter

VIDEO_URI = '/home/florian/Downloads/ArchWestMainStreetEB.mp4'

config = VideoSourceConfig(id='a', name='test', uri=VIDEO_URI, use_source_fps=True)

source = VideoSource(config)

while True:
    frame_raw = source.get()

    start = perf_counter()
    vf = VideoFrame()
    vf.ParseFromString(frame_raw)

    frame = np.frombuffer(vf.frame_data, dtype=np.uint8).reshape((vf.shape.height, vf.shape.width, vf.shape.channels))
    print(f'{perf_counter() - start}')
        
    cv2.imshow('default', frame)
    if cv2.waitKey(1) == ord('q'):
        break

source.close()
cv2.destroyAllWindows()
