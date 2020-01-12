import errno
import socket
import tempfile
import threading
import time
from unittest import mock

import pytest

from homekit import AccessoryServer
from homekit.model import Accessory
from homekit.model.services import LightBulbService
from homekit.model import mixin as model_mixin
from homekit.aio.controller import Controller
from homekit.aio.controller.ip import IpPairing


def port_ready(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return True
    finally:
        s.close()

    return False


@pytest.fixture
def controller_and_unpaired_accessory(request, event_loop):
    config_file = tempfile.NamedTemporaryFile()
    config_file.write("""{
        "accessory_ltpk": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
        "accessory_ltsk": "3d99f3e959a1f93af4056966f858074b2a1fdec1c5fd84a51ea96f9fa004156a",
        "accessory_pairing_id": "12:34:56:00:01:0A",
        "accessory_pin": "031-45-154",
        "c#": 1,
        "category": "Lightbulb",
        "host_ip": "127.0.0.1",
        "host_port": 51842,
        "name": "unittestLight",
        "unsuccessful_tries": 0
    }""".encode())
    config_file.flush()

    # Make sure get_id() numbers are stable between tests
    model_mixin.id_counter = 0

    httpd = AccessoryServer(config_file.name, None)
    accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
    lightBulbService = LightBulbService()
    accessory.services.append(lightBulbService)
    httpd.add_accessory(accessory)

    t = threading.Thread(target=httpd.serve_forever)
    t.start()

    controller = Controller()

    # This syntax is awkward. We can't use the syntax proposed by the pytest-asyncio
    # docs because we have to support python 3.5
    def cleanup():
        async def async_cleanup():
            await controller.shutdown()
        event_loop.run_until_complete(async_cleanup())
    request.addfinalizer(cleanup)

    for i in range(10):
        if port_ready(51842):
            break
        time.sleep(1)

    with mock.patch.object(controller, "load_data", lambda x: None):
        with mock.patch("homekit.aio.__main__.Controller") as c:
            c.return_value = controller
            yield controller

    httpd.shutdown()

    t.join()


@pytest.fixture
def controller_and_paired_accessory(request, event_loop):
    config_file = tempfile.NamedTemporaryFile()
    config_file.write("""{
        "accessory_ltpk": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
        "accessory_ltsk": "3d99f3e959a1f93af4056966f858074b2a1fdec1c5fd84a51ea96f9fa004156a",
        "accessory_pairing_id": "12:34:56:00:01:0A",
        "accessory_pin": "031-45-154",
        "c#": 1,
        "category": "Lightbulb",
        "host_ip": "127.0.0.1",
        "host_port": 51842,
        "name": "unittestLight",
        "peers": {
            "decc6fa3-de3e-41c9-adba-ef7409821bfc": {
                "admin": true,
                "key": "d708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8"
            }
        },
        "unsuccessful_tries": 0
    }""".encode())
    config_file.flush()

    # Make sure get_id() numbers are stable between tests
    model_mixin.id_counter = 0

    httpd = AccessoryServer(config_file.name, None)
    accessory = Accessory('Testlicht', 'lusiardi.de', 'Demoserver', '0001', '0.1')
    lightBulbService = LightBulbService()
    accessory.services.append(lightBulbService)
    httpd.add_accessory(accessory)

    t = threading.Thread(target=httpd.serve_forever)
    t.start()

    controller_file = tempfile.NamedTemporaryFile()
    controller_file.write("""{
        "alias": {
            "Connection": "IP",
            "iOSDeviceLTPK": "d708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8",
            "iOSPairingId": "decc6fa3-de3e-41c9-adba-ef7409821bfc",
            "AccessoryLTPK": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
            "AccessoryPairingID": "12:34:56:00:01:0A",
            "AccessoryPort": 51842,
            "AccessoryIP": "127.0.0.1",
            "iOSDeviceLTSK": "fa45f082ef87efc6c8c8d043d74084a3ea923a2253e323a7eb9917b4090c2fcc"
        }
    }""".encode())
    controller_file.flush()

    controller = Controller()
    controller.load_data(controller_file.name)
    config_file.close()

    # This syntax is awkward. We can't use the syntax proposed by the pytest-asyncio
    # docs because we have to support python 3.5
    def cleanup():
        async def async_cleanup():
            await controller.shutdown()
        event_loop.run_until_complete(async_cleanup())
    request.addfinalizer(cleanup)

    with mock.patch.object(controller, "load_data", lambda x: None):
        with mock.patch("homekit.aio.__main__.Controller") as c:
            c.return_value = controller
            yield controller

    httpd.shutdown()

    t.join()


@pytest.fixture
def pairing(controller_and_paired_accessory):
    return controller_and_paired_accessory.get_pairings()['alias']


@pytest.fixture
def pairings(request, event_loop, controller_and_paired_accessory):
    """ Returns a pairing of pairngs. """
    left = controller_and_paired_accessory.get_pairings()['alias']

    right = IpPairing(left.pairing_data)

    # This syntax is awkward. We can't use the syntax proposed by the pytest-asyncio
    # docs because we have to support python 3.5
    def cleanup():
        async def async_cleanup():
            await right.close()
        event_loop.run_until_complete(async_cleanup())
    request.addfinalizer(cleanup)

    yield (left, right)
