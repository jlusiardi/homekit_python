import asyncio
import tempfile
import threading
import time

import pytest

from homekit import AccessoryServer
from homekit.exceptions import AccessoryDisconnectedError
from homekit.model import Accessory
from homekit.model.services import LightBulbService
from homekit.model import mixin as model_mixin
from homekit.protocol.tlv import TLV
from homekit.aio.controller import Controller
from homekit.aio.controller.ip import IpPairing


# Without this line you would have to mark your async tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


async def test_list_accessories(pairing):
    accessories = await pairing.list_accessories_and_characteristics()
    assert accessories[0]['aid'] == 1
    assert accessories[0]['services'][0]['iid'] == 2

    char = accessories[0]['services'][0]['characteristics'][0]
    assert char['iid'] == 3
    assert char['format'] == 'bool'
    assert char['perms'] == ['pw']
    assert char['description'] == 'Identify'
    assert char['type'] == '00000014-0000-1000-8000-0026BB765291'


async def test_get_characteristics(pairing):
    characteristics = await pairing.get_characteristics([
        (1, 10),
    ])

    assert characteristics[(1, 10)] == {'value': False}


async def test_get_characteristics_after_failure(pairing):
    characteristics = await pairing.get_characteristics([
        (1, 10),
    ])

    assert characteristics[(1, 10)] == {'value': False}

    pairing.connection.transport.close()

    # The connection is closed but the reconnection mechanism hasn't kicked in yet.
    # Attempts to use the connection should fail.
    with pytest.raises(AccessoryDisconnectedError):
        characteristics = await pairing.get_characteristics([
            (1, 10),
        ])

    # We can't await a close - this lets the coroutine fall into the 'reactor'
    # and process queued work which will include the real transport.close work.
    await asyncio.sleep(0)

    characteristics = await pairing.get_characteristics([
        (1, 10),
    ])

    assert characteristics[(1, 10)] == {'value': False}


async def test_put_characteristics(pairing):
    characteristics = await pairing.put_characteristics([
        (1, 10, True),
    ])

    assert characteristics == {}

    characteristics = await pairing.get_characteristics([
        (1, 10),
    ])

    assert characteristics[(1, 10)] == {'value': True}


async def test_subscribe(pairing):
    assert pairing.subscriptions == set()

    await pairing.subscribe([(1, 10)])

    assert pairing.subscriptions == set(((1, 10), ))

    characteristics = await pairing.get_characteristics([
        (1, 10),
    ], include_events=True)

    assert characteristics == {
        (1, 10): {
            'ev': True,
            'value': False,
        }
    }


async def test_unsubscribe(pairing):
    await pairing.subscribe([(1, 10)])

    assert pairing.subscriptions == set(((1, 10), ))

    characteristics = await pairing.get_characteristics([
        (1, 10),
    ], include_events=True)

    assert characteristics == {
        (1, 10): {
            'ev': True,
            'value': False,
        }
    }

    await pairing.unsubscribe([(1, 10)])

    assert pairing.subscriptions == set()

    characteristics = await pairing.get_characteristics([
        (1, 10),
    ], include_events=True)

    assert characteristics == {
        (1, 10): {
            'ev': False,
            'value': False,
        }
    }


async def test_dispatcher_connect(pairing):
    assert pairing.listeners == set()

    callback = lambda x: x
    cancel = pairing.dispatcher_connect(callback)
    assert pairing.listeners == set((callback, ))

    cancel()
    assert pairing.listeners == set()


async def test_receiving_events(pairings):
    """
    Test that can receive events when change happens in another session.

    We set up 2 controllers both with active secure sessions. One
    subscribes and then other does put() calls.

    This test is currently skipped because accessory server doesnt
    support events.
    """
    left, right = pairings

    event_value = None
    ev = asyncio.Event()

    def handler(data):
        print(data)
        nonlocal event_value
        event_value = data
        ev.set()

    # Set where to send events
    right.dispatcher_connect(handler)

    # Set what events to get
    await right.subscribe([(1, 10)])

    # Trigger an event by writing a change on the other connection
    await left.put_characteristics([(1, 10, True)])

    # Wait for event to be received for up to 5s
    await asyncio.wait_for(ev.wait(), 5)

    assert event_value == {
        (1, 10): {
            'value': True,
        }
    }


async def test_list_pairings(pairing):
    pairings = await pairing.list_pairings()
    assert pairings == [{
        'controllerType': 'admin',
        'pairingId': 'decc6fa3-de3e-41c9-adba-ef7409821bfc',
        'permissions': 1,
        'publicKey': 'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8',
    }]


async def test_add_pairings(pairing):
    await pairing.add_pairing(
        'decc6fa3-de3e-41c9-adba-ef7409821bfe',
        'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed7',
        'User',
    )

    pairings = await pairing.list_pairings()
    assert pairings == [
        {
            'controllerType': 'admin',
            'pairingId': 'decc6fa3-de3e-41c9-adba-ef7409821bfc',
            'permissions': 1,
            'publicKey': 'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8',
        },
        {
            'controllerType': 'regular',
            'pairingId': 'decc6fa3-de3e-41c9-adba-ef7409821bfe',
            'permissions': 0,
            'publicKey': 'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed7',
        },

    ]

async def test_add_and_remove_pairings(pairing):
    await pairing.add_pairing(
        'decc6fa3-de3e-41c9-adba-ef7409821bfe',
        'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed7',
        'User',
    )

    pairings = await pairing.list_pairings()
    assert pairings == [
        {
            'controllerType': 'admin',
            'pairingId': 'decc6fa3-de3e-41c9-adba-ef7409821bfc',
            'permissions': 1,
            'publicKey': 'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8',
        },
        {
            'controllerType': 'regular',
            'pairingId': 'decc6fa3-de3e-41c9-adba-ef7409821bfe',
            'permissions': 0,
            'publicKey': 'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed7',
        },

    ]

    await pairing.remove_pairing('decc6fa3-de3e-41c9-adba-ef7409821bfe')

    pairings = await pairing.list_pairings()
    assert pairings == [{
        'controllerType': 'admin',
        'pairingId': 'decc6fa3-de3e-41c9-adba-ef7409821bfc',
        'permissions': 1,
        'publicKey': 'd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8',
    }]


async def test_identify(pairing):
    identified = await pairing.identify()
    assert identified == True
