#!/bin/bash

export PACKAGE_NAME=video-source-py

export PATH=/root/.local/bin/:$PATH
cd /code
echo "export GPG_KEY=${GPG_KEY}" > env.sh
echo "export PASSPHRASE=${GPG_KEY}" >> env.sh
cat env.sh
source ./env.sh

# Setting up PGP
mkdir ~/.gnupg
echo "allow-loopback-pinentry" > ~/.gnupg/gpg-agent.conf
echo "pinentry-mode loopback" > ~/.gnupg/gpg.conf

gpgconf --launch gpg-agent
export GPG_TTY=$(tty)
export GPG_PASS=$PASSPHRASE

echo ${GPG_KEY} | base64 --decode | gpg --batch --import

export DEBSIGN_KEYID=$(gpg --list-keys --with-colons | grep pub | cut -d: -f5)

cat > gpg-loopback.sh  <<EOF
#!/bin/bash
exec gpg \
  --batch \
  --yes \
  --pinentry-mode loopback \
  --passphrase "$GPG_PASS" \
  "$@"

EOF

chmod u+x gpg-loopback.sh
export GPG="gpg-loopback.sh"

#poetry lock
#poetry build

./check_settings.sh
dpkg-buildpackage -k$DEBSIGN_KEYID -S
mkdir -p target
mv ../${PACKAGE_NAME}_* target/


