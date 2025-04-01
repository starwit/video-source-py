import logging
import time
from collections import deque
from threading import Event, RLock, Thread
from prometheus_client import Counter, Summary
from .framecounterthread import FrameCounterThread

import cv2

FRAME_COUNTER = Counter('frame_grabber_frame_counter', 'The number of frames that were retrieved from the video stream')
FRAME_LOOP_DURATION = Summary('frame_grabber_loop_duration', 'The time between calls to VideoCapture.read()')

class FrameGrabber(Thread):
    def __init__(self, uri: str, reconnect_backoff_time: float = 1.0) -> None:
        super().__init__(name=__name__, target=self._main_loop)
        self._frame_deque = deque(maxlen=1)
        self._stop_event = Event()

        self._uri = uri
        self._reconnect_backoff_time = reconnect_backoff_time

        self._logger = logging.getLogger(__name__)

        self._cap = None
        self._source_fps = None
        self._last_frame_ts = None
        self._last_frame_ok = True
        self.frame_counter = FrameCounterThread()
        self.start()
        self.frame_counter.start()

    # Always remember: This method is called from within the thread and must not be called outside
    def _main_loop(self):
        last_read_call_ts = time.time()
        
        while not self._stop_event.is_set():
            if not self._ensure_connection():
                time.sleep(self._reconnect_backoff_time)
                continue

            FRAME_LOOP_DURATION.observe(time.time() - last_read_call_ts)
            last_read_call_ts = time.time()
            
            self._last_frame_ok, frame = self._cap.read()
            if not self._last_frame_ok:
                continue

            FRAME_COUNTER.inc()

            self._frame_deque.append(frame)
        
        if self._cap is not None:
            self._cap.release()

    def _ensure_connection(self):
        if self._cap is None:
            self._cap = cv2.VideoCapture(self._uri)
            if self._cap.isOpened():
                self._source_fps = self._cap.get(cv2.CAP_PROP_FPS)
                self._logger.info(f'Successfully established connection to {self._uri}')
                self._logger.info(f'Detected source framerate: {self._source_fps:.3f} fps')
                self._logger.info(f'Detected source frame size: {int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}')
                return True
            else:
                self._logger.warn(f'Could not open source at {self._uri}')
                return False

        if not self._cap.isOpened():
            self._cap.release()
            self._cap = None
            self._logger.warn(f'Source not available anymore at {self._uri}')
            return False
        
        if not self._last_frame_ok:
            self._cap.release()
            self._cap = None
            self._logger.warn(f'Last frame was not okay. Discarding active connection.')
            return False
        
        return True
    
    @property
    def source_fps(self):
        return self._source_fps

    def get_frame(self):
        if self._stop_event.is_set():
            return None
        try:
            return self._frame_deque.popleft()
        except IndexError:
            return None
        
    def stop(self):
        self._stop_event.set()
        self.join(10)
        self.frame_counter.stop()
