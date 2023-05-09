import cv2

from .config import VideoSourceConfig


class VideoSource:
    def __init__(self, config: VideoSourceConfig) -> None:
        if config.__class__.__name__ != 'VideoSourceConfig':
            raise TypeError('Config must be of type VideoSourceConfig')
        self.config = config

    def frame_iter(self):
        try:
            cap = cv2.VideoCapture(self.config.uri)
            if not cap.isOpened():
                raise IOError(f'Cannot open video source at {self.config.uri}')

            while True:
                frame_ok, frame = cap.read()
                if not frame_ok:
                    raise IOError('Could not read frame')

                yield frame
        finally:
            cap.release()
