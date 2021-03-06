#!/bin/bash
set -e

# Verified on Mac OSX Yosemite and El Capitan

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CRYPTOGRAPHY_VERSION='1.2.1'

# Go to parent project
cd ${DIR}
cd ..

# Get secrets2git submodule
git submodule update --init

cd ${DIR}

# Clarify sudo password prompt
sudo -p "System password for sudo commands: " echo 1 >/dev/null 2>&1;

# Make sure pip is installed
command -v pip >/dev/null 2>&1 || {
    echo "I require pip but it's not installed. Installing..." >&2;
    sudo -H easy_install pip;
}

PIP_INSTALL='pip install --trusted-host pypi.python.org'

# Install cryptography package
if ! hash openssl 2>/dev/null && [[ "$OSTYPE" == "darwin"* ]]; then
    # Make sure openssl is installed (for El Capitan)
    read -p "OpenSSL needs to be installed via homebrew, proceed? " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install openssl 2> /dev/null || true;
        sudo -H env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" ${PIP_INSTALL} -I cryptography==${CRYPTOGRAPHY_VERSION}
    else
        exit 1
    fi
else
  sudo -H ${PIP_INSTALL} -I cryptography==${CRYPTOGRAPHY_VERSION} pycparser==2.13
fi

sudo -H ${PIP_INSTALL} --ignore-installed six -r requirements.txt

if [ -f ${DIR}/../Secrets2GitConf.py ]; then
  # If existing project, do initial decryption
  python secrets2git.py decrypt
fi
