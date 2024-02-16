#!/bin/bash

docker build -t starwitorg/sae-video-source-py:$(poetry version --short) .