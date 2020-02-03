"""
Provide a non-blocking wrapper around the zeroconf library.

There is aiozercoonf but it doesn't work on Windows - there isn't a
version of asyncio with UDP support on Windows that also supports subprocess.
This is fixed in Python 3.8, but until then it's probably best to stick
with zeroconf.

This also means we don't need to add any extra dependencies.
"""

import asyncio
from functools import partial

from homekit.zeroconf_impl import discover_homekit_devices


async def async_discover_homekit_devices(max_seconds=10):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        partial(discover_homekit_devices, max_seconds=max_seconds)
    )
