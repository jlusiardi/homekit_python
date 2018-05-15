FROM debian:9

RUN apt update -y; apt upgrade -y

RUN apt -y install libgmp-dev libmpfr-dev libmpc-dev libffi-dev build-essential python3-pip python3-dev git

RUN pip3 install --user homekit; rm -rf /root/.local/lib/python3.5/site-packages/homekit*

RUN git clone https://github.com/jlusiardi/homekit_python.git

WORKDIR /homekit_python

RUN mkdir /root/.homekit/

ADD docker_supplementals/demoserver.json /root/.homekit/

ADD demoserver.py /homekit_python/
