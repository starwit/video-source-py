import signal
import redis
import threading
from video_source_py.config import VideoSourceConfig
from video_source_py.videosource import VideoSource

if __name__ == '__main__':

    stop_event = threading.Event()
    last_retrieved_id = None

    # Register signal handlers
    def sig_handler(signum, _):
        signame = signal.Signals(signum).name
        print(f'Caught signal {signame} ({signum}). Exiting...')
        stop_event.set()

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Load config from settings.yaml / env vars
    CONFIG = VideoSourceConfig()

    # Init Videosource
    video_source = VideoSource(CONFIG)

    # Init output
    redis_conn = redis.Redis(
        host=CONFIG.output.host,
        port=CONFIG.output.port,
    )

    # Start processing images
    while not stop_event.is_set():
        image_proto = video_source.get()
        if image_proto is not None:
            redis_conn.xadd(name=f'video_source_{CONFIG.id}', fields={'proto_data': image_proto}, maxlen=10)
