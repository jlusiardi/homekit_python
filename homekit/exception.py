#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


class HomeKitException(Exception):
    """Generic HomeKit exception.
    Attributes:
        stage: the stage that the exception occurred at
    """

    def __init__(self, stage):
        self.stage = stage

    pass


class UnknownError(HomeKitException):
    """Raised upon receipt of an unknown error"""
    pass


class AuthenticationError(HomeKitException):
    """Raised upon receipt of an authentication error"""
    pass


class BackoffError(HomeKitException):
    """Raised upon receipt of a backoff error"""
    pass


class MaxPeersError(HomeKitException):
    """Raised upon receipt of a maxpeers error"""
    pass


class MaxTriesError(HomeKitException):
    """Raised upon receipt of a maxtries error"""
    pass


class UnavailableError(HomeKitException):
    """Raised upon receipt of an unavailable error"""
    pass


class BusyError(HomeKitException):
    """Raised upon receipt of a busy error"""
    pass


class InvalidError(HomeKitException):
    """Raised upon receipt of an error not defined in the HomeKit spec"""
    pass


class IllegalData(HomeKitException):
    """Raised upon receipt of invalid encrypted data"""
    pass


class InvalidAuth(HomeKitException):
    """Raised upon receipt of an invalid authtag"""
    pass


class IncorrectPairingID(HomeKitException):
    """Raised upon a pairing response that doesn't match pairing data"""
    pass


class InvalidSignature(HomeKitException):
    """Raised upon receipt of an invalid signature from an accessory"""
    pass


class HomeKitStatusException(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
