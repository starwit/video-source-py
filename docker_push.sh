#!/bin/bash

docker push docker.internal.starwit-infra.de/sae/video-source-py:$(poetry version --short)