import pytest

from homekit.exceptions import AuthenticationError


# Without this line you would have to mark your async tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


async def test_remove_pairing(controller_and_paired_accessory):
    pairing = controller_and_paired_accessory.pairings['alias']

    # Verify that there is a pairing connected and working
    await pairing.get_characteristics([(1, 10)])

    # Remove pairing from controller
    await controller_and_paired_accessory.remove_pairing('alias')

    # Verify now gives an appropriate error
    with pytest.raises(AuthenticationError):
        await pairing.get_characteristics([(1, 10)])
