"""
This module is for regression tests.

This is where we have identified something that breaks a HomeKit accessory
certified by Apple because our implementation of the spec is different to
Apple's. If your change trips a test in this module it is likely you will 
break support for a device that currently works.

We strive to comply with the HAP spec wherever possible, and where
possible we aim to do what an iOS device would do.
"""

import unittest
from unittest import mock

from homekit.http_impl.secure_http import SecureHttp


class TestHTTPPairing(unittest.TestCase):

    """
    Communication failures in the pairing stage.

    These types of problem generally involve comparing a working and
    non-working device via WireShark.
    """

    def test_pairing_doesnt_add_extra_headers(self):
        """
        The tado internet bridge will fail if a pairing request has
        extraneous headers like `Accept-Encoding`.

        https://github.com/home-assistant/home-assistant/issues/16971
        https://github.com/jlusiardi/homekit_python/pull/130
        """


class TestSecureSession(unittest.TestCase):

    """
    Communication failures of HTTP secure session layer.

    To debug these its often easiest to modify demoserver.py to dump
    data as it decrypts it, then compare an iOS device to homekit_python.
    """

    def test_requests_have_host_header(self):
        """
        The tado internet bridge will fail if a secure session request
        doesn't have a Host header.

        https://github.com/home-assistant/home-assistant/issues/16971
        https://github.com/jlusiardi/homekit_python/pull/130
        """

        session = mock.Mock()
        session.pairing_data = {
            'AccessoryIP': '192.168.1.2:8000',
            'AccesoryPort': 8080,
        }
        secure_http = SecureHttp(session)

        with mock.patch.object(session, '_handle_request') as handle_req:
            secure_http.get('/characteristics')
            assert b'\nHost: 192.168.1.2:8080\n' in handle_req.call_args[0][0]

            secure_http.post('/characteristics')
            assert b'\nHost: 192.168.1.2:8080\n' in handle_req.call_args[0][0]

            secure_http.put('/characteristics')
            assert b'\nHost: 192.168.1.2:8080\n' in handle_req.call_args[0][0]

    def test_requests_only_send_params_for_true_case(self):
        """
        The tado internet bridge will fail if a GET request has what it
        considers to be unexpected request parameters.

        An iPhone client sends requests like `/characteristics?id=1.10`.
        It doesn't transmit `ev=0` or any other falsies.

        https://github.com/home-assistant/home-assistant/issues/16971
        https://github.com/jlusiardi/homekit_python/pull/132
        """
