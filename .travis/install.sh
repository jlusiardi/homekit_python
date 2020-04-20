#!/bin/bash

echo "OS: $TRAVIS_OS_NAME"

if [ "$TRAVIS_OS_NAME" == "linux" ]; then
    # update openssl to a version that is sufficient for cryptography 2.6 (openssl 1.1 is required since)
    wget http://launchpadlibrarian.net/400343104/libssl1.1_1.1.0g-2ubuntu4.3_amd64.deb
    sudo dpkg -i libssl1.1_1.1.0g-2ubuntu4.3_amd64.deb
    wget http://launchpadlibrarian.net/367327834/openssl_1.1.0g-2ubuntu4_amd64.deb
    sudo dpkg -i openssl_1.1.0g-2ubuntu4_amd64.deb
    openssl version
    sudo apt-get update;
    sudo apt-get install -y build-essential python3-dev libdbus-1-dev libdbus-glib-1-dev libgirepository1.0-dev;
    pip install -r requirements.txt
    pip install coveralls
fi

if [ "$TRAVIS_OS_NAME" == "osx" ]; then
    brew update
    # see https://github.com/pyenv/pyenv/wiki#suggested-build-environment for Mac OS X
    brew install openssl readline sqlite3 xz zlib
    openssl version
    # pyenv is already installed on a test node
    brew outdated pyenv || brew upgrade pyenv
    pyenv install --list
    pyenv install $PYTHON
    pyenv shell $PYTHON
    python --version
    python3 --version
    pip --version
    pip3 --version
    pip3 install -r requirements_osx.txt
    pip3 install coveralls
fi

if [ "$TRAVIS_OS_NAME" == "windows" ]; then
    choco install python3 --params "/Python38:C:\Python38"
    export PATH="/c/Python38:/c/Python38/Scripts:$PATH"
    py --version
    pip3 --version
    pip3 install -r requirements_windows.txt
    pip3 install coveralls flake8
    echo $PATH
    pwd
    ls -hal
    ls -hal /c/Python38/Scripts
fi
