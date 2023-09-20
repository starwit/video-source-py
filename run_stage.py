import logging
import signal
import threading

from visionlib.pipeline.publisher import RedisPublisher

from video_source_py.config import VideoSourceConfig
from video_source_py.videosource import VideoSource

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    stop_event = threading.Event()

    # Register signal handlers
    def sig_handler(signum, _):
        signame = signal.Signals(signum).name
        print(f'Caught signal {signame} ({signum}). Exiting...')
        stop_event.set()

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Load config from settings.yaml / env vars
    CONFIG = VideoSourceConfig()
    logger.setLevel(CONFIG.log_level.value)

    logger.info(f'Starting video source (id={CONFIG.id},use_source_fps={CONFIG.use_source_fps},redis={CONFIG.redis.host}:{CONFIG.redis.port})')

    # Init Videosource
    video_source = VideoSource(CONFIG)

    with RedisPublisher(CONFIG.redis.host, CONFIG.redis.port) as publish:
        # Start processing images
        while not stop_event.is_set():
            image_proto = video_source.get()
            if image_proto is not None:
                publish(stream_key=f'{CONFIG.redis.output_stream_prefix}:{CONFIG.id}', proto_data=image_proto)

    video_source.close()

