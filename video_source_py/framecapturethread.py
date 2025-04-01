import threading
import queue

class FrameCaptureThread:
    def __init__(self, video_source):
        self.video_source = video_source
        self.frame_queue = queue.Queue()
        self.stopped = False
        self.thread = threading.Thread(target=self.capture_frames)
        self.thread.daemon = True

    def start(self):
        self.thread.start()

    def capture_frames(self):
        while not self.stopped:
            # Capture the frame (which will increment the counter internally)
            proto = self.video_source.get()
            # Even if proto is None, record the corresponding frame_id (accessible via video_source)
            self.frame_queue.put((self.video_source.frame_id, proto))
            
    def stop(self):
        self.stopped = True
        self.thread.join()
