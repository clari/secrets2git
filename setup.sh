#!/bin/bash
set -e

# Clarify sudo password prompt
sudo -p "System password for sudo commands: " echo 1 >/dev/null 2>&1;

# Make sure pip is installed
command -v pip >/dev/null 2>&1 || {
    echo "I require pip but it's not installed. Installing..." >&2;
    sudo -H easy_install pip;
}

if hash openssl 2>/dev/null; then
    sudo -H pip install -I cryptography
else
    # Make sure openssl is installed (for El capitan)
    brew install openssl 2> /dev/null || true;
    sudo -H env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip install -I cryptography
fi

sudo -H pip install --ignore-installed six -r requirements.txt
