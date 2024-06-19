import os
PARALLELSIM = int(os.environ.get("VIDEO_SOURCE_PARALLELISM", 1))
print(f'Parallelism set to {PARALLELSIM}')

# Prevent numpy from using multiple threads, because we do not need to parallelize the computation and it created a lot of overhead
# This needs to be done before any app module is imported!
os.environ["OMP_NUM_THREADS"] = f'{PARALLELSIM}'
os.environ["OPENBLAS_NUM_THREADS"] = f'{PARALLELSIM}'
os.environ["MKL_NUM_THREADS"] = f'{PARALLELSIM}'
os.environ["VECLIB_MAXIMUM_THREADS"] = f'{PARALLELSIM}'
os.environ["NUMEXPR_NUM_THREADS"] = f'{PARALLELSIM}'

# Limit OpenCV and subcomponents to one thread (again, order is important)
os.environ["OPENCV_FFMPEG_THREADS"] = f'{PARALLELSIM}'
import cv2
cv2.setNumThreads(PARALLELSIM)

from video_source_py import run_stage

if __name__ == '__main__':
    run_stage()