FROM debian:9

RUN apt update -y; \
    apt upgrade -y; \
    apt install -y python3-pip git libgirepository1.0-dev gcc libcairo2-dev pkg-config \
                   python3-dev gir1.2-gtk-3.0 libdbus-1-dev locales; \
    locale-gen en_US.UTF-8; \
    useradd -m test;

#RUN chmod 0755 /etc/default/locale

ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

USER test

RUN pip3 install virtualenv; echo "export PATH=/home/test/.local/bin:$PATH" >> /home/test/.bashrc

RUN cd; git clone https://github.com/jlusiardi/homekit_python.git; cd homekit_python; git pull --all; git checkout fix_106_install_and_runtime_dependencies

WORKDIR /home/test/homekit_python
