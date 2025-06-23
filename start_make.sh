#!/bin/bash

#export GPG_TTY=$(tty)

echo $0
export PATH=/root/.local/bin/:$PATH
cd /code
echo "export GPG_KEY=${GPG_KEY}" > env.sh
echo "export PASSPHRASE=${GPG_KEY}" >> env.sh
cat env.sh
source ./env.sh
make