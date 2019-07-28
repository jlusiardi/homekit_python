import asyncio
import tempfile
import threading
import time

import pytest

from homekit import AccessoryServer
from homekit.model import Accessory
from homekit.model.services import LightBulbService
from homekit.model import mixin as model_mixin
from homekit.protocol.tlv import TLV
from homekit.aio.controller import Controller
from homekit.aio.controller.ip import IpDiscovery, IpPairing


# Without this line you would have to mark your async tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


async def test_pair(controller_and_unpaired_accessory):
    discovery = IpDiscovery(controller_and_unpaired_accessory, {
        'address': '127.0.0.1',
        'port': 51842,
        'id': '00:01:02:03:04:05',
    })

    pairing = await discovery.perform_pairing('alias', '031-45-154')

    assert isinstance(pairing, IpPairing)

    assert await pairing.get_characteristics([(1, 10)]) == {
        (1, 10): {'value': False},
    }

async def test_identify(controller_and_unpaired_accessory):
    discovery = IpDiscovery(controller_and_unpaired_accessory, {
        'address': '127.0.0.1',
        'port': 51842,
        'id': '00:01:02:03:04:05',
    })

    identified = await discovery.identify()
    assert identified == True
