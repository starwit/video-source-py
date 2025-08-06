import logging
import signal
import threading

from prometheus_client import Histogram, start_http_server
from visionlib.pipeline.publisher import RedisPublisher

from .config import VideoSourceConfig
from .videosource import VideoSource

logger = logging.getLogger(__name__)

REDIS_PUBLISH_DURATION = Histogram('video_source_redis_publish_duration', 'The time it takes to push a message onto the Redis stream',
                                   buckets=(0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25))

def run_stage():

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

    logger.info(f'Starting prometheus metrics endpoint on port {CONFIG.prometheus_port}')

    start_http_server(CONFIG.prometheus_port)

    logger.info(f'Starting video source. Config: {CONFIG.model_dump_json(indent=2)}')

    # Init Videosource
    video_source = VideoSource(CONFIG)

    try:
        video_source.start()

        with RedisPublisher(CONFIG.redis.host, CONFIG.redis.port) as publish:
            # Start processing images
            while not stop_event.is_set():
                image_proto = video_source.get()
                if image_proto is not None:
                    with REDIS_PUBLISH_DURATION.time():
                        publish(stream_key=f'{CONFIG.redis.output_stream_prefix}:{CONFIG.id}', proto_data=image_proto)
    except Exception as e:
        logger.error('Exception in main loop', exc_info=True)
    finally:
        video_source.close()

