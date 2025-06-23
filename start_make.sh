#!/bin/bash

export PACKAGE_NAME=video-source-py

export PATH=/root/.local/bin/:$PATH
cd /code
echo "export GPG_KEY=${GPG_KEY}" > env.sh
echo "export PASSPHRASE=${PASSPHRASE}" >> env.sh
source ./env.sh

make

