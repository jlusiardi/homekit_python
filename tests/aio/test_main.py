"""Test the AIO CLI variant."""

import json
from unittest import mock

import pytest

from homekit.aio.__main__ import main


# Without this line you would have to mark your async tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


async def test_help():
    with mock.patch("sys.stdout") as stdout:
        with pytest.raises(SystemExit):
            await main(["-h"])
    printed = stdout.write.call_args[0][0]

    assert printed.startswith("usage: ")
    assert "discover_ip" in printed


async def test_get_accessories(pairing):
    with mock.patch("sys.stdout") as stdout:
        await main(["get_accessories", "-f", "pairing.json", "-a", "alias"])
    printed = stdout.write.call_args_list[0][0][0]
    assert printed.startswith("1.2: >accessory-information")

    with mock.patch("sys.stdout") as stdout:
        await main(["get_accessories", "-f", "pairing.json", "-a", "alias", "-o", "json"])
    printed = stdout.write.call_args_list[0][0][0]
    accessories = json.loads(printed)
    assert accessories[0]["aid"] == 1
    assert accessories[0]["services"][0]["iid"] == 2
    assert accessories[0]["services"][0]["characteristics"][0]["iid"] == 3


async def test_get_characteristic(pairing):
    with mock.patch("sys.stdout") as stdout:
        await main(["get_characteristics", "-f", "pairing.json", "-a", "alias", "-c", "1.10"])
    printed = stdout.write.call_args_list[0][0][0]
    assert json.loads(printed) == {"1.10": {"value": False}}


async def test_put_characteristic(pairing):
    with mock.patch("sys.stdout"):
        await main(["put_characteristics", "-f", "pairing.json", "-a", "alias", "-c", "1.10", "true"])

    characteristics = await pairing.get_characteristics([
        (1, 10),
    ])
    assert characteristics[(1, 10)] == {'value': True}


async def test_list_pairings(pairing):
    with mock.patch("sys.stdout") as stdout:
        await main(["list_pairings", "-f", "pairing.json", "-a", "alias"])
    printed = "".join(write[0][0] for write in stdout.write.call_args_list)
    assert printed == (
        "Pairing Id: decc6fa3-de3e-41c9-adba-ef7409821bfc\n"
        "\tPublic Key: 0xd708df2fbf4a8779669f0ccd43f4962d6d49e4274f88b1292f822edc3bcf8ed8\n"
        "\tPermissions: 1 (admin)\n"
    )
