#!/bin/bash
set -e

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
    # Install Python 3.6.5 directly from brew
    brew update
    brew uninstall --ignore-dependencies python
    brew install --ignore-dependencies https://raw.githubusercontent.com/Homebrew/homebrew-core/f2a764ef944b1080be64bd88dca9a1d80130c558/Formula/python.rb

    python3 --version
    pip3 --version
    pip3 install -r requirements_osx.txt
    pip3 install coveralls
fi
