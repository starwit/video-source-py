# Video Source (Python)

## How to setup
- Make sure you have Poetry installed (otherwise head over to https://python-poetry.org/docs/#installing-with-the-official-installer)
- Run `poetry install`
- Run the below script with `poetry run <scriptfile>`

## Sample script to play around with
```python
from video_source_py.videosource import VideoSource, VideoSourceConfig
import numpy as np
from visionapi.videosource_pb2 import VideoFrame
import cv2
from time import perf_counter

VIDEO_URI = 'path/to/video/file'
RTSP_URI = 'rtsp://uri'

config = VideoSourceConfig(id='a', name='test', uri=VIDEO_URI)

source = VideoSource(config)
source.start()

while True:
    frame_raw = source.get_frame()

    start = perf_counter()
    vf = VideoFrame()
    vf.ParseFromString(frame_raw)

    frame = np.frombuffer(vf.frame, dtype=np.uint8).reshape(vf.shape)
    stop = perf_counter()
    print(f'Time to unpack frame {stop - start}s')
        
    cv2.imshow('default', frame)
    if cv2.waitKey(1) == ord('q'):
        source.stop()
        break

cv2.destroyAllWindows()

```