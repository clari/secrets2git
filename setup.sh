#!/bin/bash
set -e

# Verified on Mac OSX Yosemite and El Capitan

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to parent project
cd ${DIR}
cd ..

# Get secrets2git submodule
git submodule update --init

# Clarify sudo password prompt
sudo -p "System password for sudo commands: " echo 1 >/dev/null 2>&1;

# Make sure pip is installed
command -v pip >/dev/null 2>&1 || {
    echo "I require pip but it's not installed. Installing..." >&2;
    sudo -H easy_install pip;
}

# Install cryptography package
if ! hash openssl1 2>/dev/null && [[ "$OSTYPE" == "darwin"* ]]; then
  # Make sure openssl is installed (for El Capitan)
    brew install openssl 2> /dev/null || true;
    sudo -H env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip install -I cryptography
else
  sudo -H pip install -I cryptography
fi

sudo -H pip install --ignore-installed six -r requirements.txt

# Do initial decryption
python secrets2git/secrets2git.py decrypt
