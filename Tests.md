# Testing

# setting up test environment

```bash
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config gir1.2-gtk-3.0 libdbus-1-dev python3-dev python3-pip
pip3 install --user virtualenv
virtualenv tests_env
source tests_env/bin/activate
pip install -r requirements.txt 
```

Use docker to run the tests in a container:
```bash
# build image
docker build -t homekit_tests -f ./Dockerfile_tests  .

# start container
docker run --rm -ti homekit_tests
```

# Running unit tests

```bash
coverage3 run --branch -m unittest -v ; coverage3 html
```

# Style checker

```bash
flake8 homekit tests
```

# Test pair & unpair

# Bluetooth LE
```bash
PYTHONPATH=. python3 homekit/pair_ble.py -f ble.json -a DW1 -m e2:a3:cb:26:77:61 -p 893-01-591;\
PYTHONPATH=. python3 homekit/unpair.py -f ble.json -a DW1
```

# IP
```bash
PYTHONPATH=. python3 homekit/pair.py -f controller.json -a esp -d EC:73:A0:BD:97:22 -p 111-11-111;\
PYTHONPATH=. python3 homekit/unpair.py -f controller.json -a esp
```