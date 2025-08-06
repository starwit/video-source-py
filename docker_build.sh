#!/bin/bash

docker build -t starwitorg/sae-video-source-py:$(git rev-parse --short HEAD) .