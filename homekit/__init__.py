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

__all__ = [
    'Controller', 'BluetoothAdapterError', 'AccessoryDisconnectedError', 'AccessoryNotFoundError',
    'AlreadyPairedError', 'AuthenticationError', 'BackoffError', 'BusyError', 'CharacteristicPermissionError',
    'ConfigLoadingError', 'ConfigSavingError', 'ConfigurationError', 'FormatError', 'HomeKitException',
    'HttpException', 'IncorrectPairingIdError', 'InvalidAuthTagError', 'InvalidError', 'InvalidSignatureError',
    'MaxPeersError', 'MaxTriesError', 'ProtocolError', 'RequestRejected', 'UnavailableError', 'UnknownError',
    'UnpairedError'
]

from homekit.controller import Controller
from homekit.exceptions import BluetoothAdapterError, AccessoryDisconnectedError, AccessoryNotFoundError, \
    AlreadyPairedError, AuthenticationError, BackoffError, BusyError, CharacteristicPermissionError, \
    ConfigLoadingError, ConfigSavingError, ConfigurationError, FormatError, HomeKitException, HttpException, \
    IncorrectPairingIdError, InvalidAuthTagError, InvalidError, InvalidSignatureError, MaxPeersError, MaxTriesError, \
    ProtocolError, RequestRejected, UnavailableError, UnknownError, UnpairedError

from homekit.tools import IP_TRANSPORT_SUPPORTED

if IP_TRANSPORT_SUPPORTED:
    # TODO: change import and let it be imported from its specific file
    from homekit.accessoryserver import AccessoryServer  # noqa: F401

    __all__ += 'AccessoryServer'
