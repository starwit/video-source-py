from video_source_py.videosource import VideoSource, VideoSourceConfig
import numpy as np
from visionapi.messages_pb2 import VideoFrame
import cv2
from time import perf_counter

# VIDEO_URI = '/home/florian/workspaces/carmel/videos/RangelineSMedicalDr.mp4'
VIDEO_URI = '/home/florian/workspaces/carmel/videos/MISOGuilfordCityCenterDr.mp4'

config = VideoSourceConfig(id='video1', uri=VIDEO_URI, use_source_fps=True, log_level='DEBUG')

source = VideoSource(config)

cv2.namedWindow('default', cv2.WINDOW_NORMAL)
cv2.resizeWindow('default', 1920, 1080)

while True:
    start = perf_counter()
    frame_raw = source.get()
    if frame_raw is None:
        break

    frame_retrieval = perf_counter()
    vf = VideoFrame()
    vf.ParseFromString(frame_raw)

    frame = np.frombuffer(vf.frame_data, dtype=np.uint8).reshape((vf.shape.height, vf.shape.width, vf.shape.channels))
    frame_decoding = perf_counter()
        
    cv2.imshow('default', frame)
    if cv2.waitKey(1) == ord('q'):
        break
    frame_display = perf_counter()
    print(f'Retrieve {frame_retrieval-start:.4f}, Decode {frame_decoding-frame_retrieval:.4f}, Display {frame_display-frame_decoding:.4f}, Total {perf_counter()-start:.4f}')

source.close()
cv2.destroyAllWindows()
