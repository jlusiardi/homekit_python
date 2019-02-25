#!/bin/bash

echo "OS: $TRAVIS_OS_NAME"
if [ "$TRAVIS_OS_NAME" == "linux" ]; then
    sudo apt-get update;
    sudo apt-get install -y build-essential python3-dev libdbus-1-dev libdbus-glib-1-dev libgirepository1.0-dev;
    pip install coveralls;
    pip install flake8;
fi
