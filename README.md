# Video Source (Python)
**Do not use this component with a local video file! (see below)**

This component is part of the Starwit Awareness Engine (SAE). See umbrella repo here: https://github.com/starwit/vision-pipeline-k8s

## How-To Setup
- Make sure you have Poetry installed (otherwise head over to https://python-poetry.org/docs/#installing-with-the-official-installer)
- Source the script `set_local_git_creds.sh` (and use a read-only token with minimal permissions)
- Run `poetry install`
- Run either `demo.py` or `run_stage.py`

## Run Pipeline Stage
- Make sure that you have a Redis instance available
- Create a `settings.yaml` (you can find some hints in `settings.template.yaml`)
- Run `run_stage.py`

## Run Demo
- Run `demo.py`
- Press `q` (on display window) to exit

## How to Build

See [dev readme](DEV_README.md) for build instructions.

## Caveats
### Camera Simulation
In earlier versions there used to be a `use_source_fps` config option that would limit the read (and thereby output) frame rate to the native frame rate of the source (which only made sense with a local video file). This could be used to simulate a camera.

However, as this implementation had a major bug of not getting frames fast enough, therefore provoking packet loss on the TCP stack level, I had to rework and decouple the frame grabbing mechanism. I decided to remove this feature, as it would have unnecessarily complicated the code. Camera simulation is most probably not going to be a major use case.
If necessary, you can always use a streaming server (like mediamtx) to serve a local file as a RTSP stream.

The current implementation retrieves frames from the incoming stream as fast as possible (the loop is very simple) in order to clear the TCP receive buffer as quickly as possible. **Consequentially, you should not use this component directly on a video file anymore, it will just hog one core of your CPU and you will probably lose a lot of frames!**
