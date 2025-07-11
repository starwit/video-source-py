import pytest

def test_video_source_import():
    try:
        from video_source_py.videosource import VideoSource
    except ImportError:
        pytest.fail("VideoSource module could not be imported")
    