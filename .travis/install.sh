#!/bin/bash

echo "OS: $TRAVIS_OS_NAME"

if [ "$TRAVIS_OS_NAME" == "linux" ]; then
    sudo apt-get update;
    sudo apt-get install -y build-essential python3-dev libdbus-1-dev libdbus-glib-1-dev libgirepository1.0-dev;
    pip install coveralls;
    pip install flake8;
fi

if [ "$TRAVIS_OS_NAME" == "osx" ]; then
    brew update
    # see https://github.com/pyenv/pyenv/wiki#suggested-build-environment for Mac OS X
    brew install openssl readline sqlite3 xz zlib
    brew install pyenv
    pyenv install $PYTHON
fi
