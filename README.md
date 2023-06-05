# Video Source (Python)

## How to setup
- Make sure you have Poetry installed (otherwise head over to https://python-poetry.org/docs/#installing-with-the-official-installer)
- Source the script `set_local_git_creds.sh` (and use a read-only token with minimal permissions)
- Run `poetry install`
- Run the below script with `poetry run <scriptfile>`

## Sample script to play around with
Look at `demo.py`. Enter your `VIDEO_URI` (can also be any URI OpenCV understands, e.g. RTSP URI or `0` for your first webcam) and run the script.