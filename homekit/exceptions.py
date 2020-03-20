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


class BluetoothAdapterError(HomeKitException):
    pass


class MalformedPinError(HomeKitException):
    """
    Class to represent a malformed pin (not following the form DDD-DD-DDD)
    """
    pass


class ProtocolError(HomeKitException):
    """
    Class to represent an abstraction layer for all errors that are defined in the Error Codes table 4-5 page 60 of the
    specification.
    """
    pass


class UnknownError(ProtocolError):
    """
    Raised upon receipt of an unknown error (transmission of Errors.Unknown). The spec says that this can happen
    during "Add Pairing" (chapter 4.11 page 51) and "Remove Pairing" (chapter 4.12 page 53).
    """
    pass


class AuthenticationError(ProtocolError):
    """
    Raised upon receipt of an authentication error. This can happen on:
     * multiple occasions through out setup pairing (M4 / page 42, M5 page 45): if the pairing could not be established
     * during pair verify (M4 / page 50): if the session key could not be generated
     * during add pair (M2 / page 52): if the controller is not admin
     * during remove pairing (M2 / page 54): if the controller is not admin
     * during list pairing (M2 / page 56): if the controller is not admin
    """
    pass


class BackoffError(ProtocolError):
    """
    Raised upon receipt of a back off error. It seems unclear when this is raised, must be related to
    TlvType.RetryDelay which is defined on page 61 of the spec.
    """
    pass


class MaxPeersError(ProtocolError):
    """
    Raised upon receipt of a max peers error. This can happen:
     * during executing a "pair setup" command
     * during an "add pairing" command
    """
    pass


class MaxTriesError(ProtocolError):
    """
    Raised upon receipt of a max tries error during a pair setup procedure. This happens if more than 100 unsuccessful
    authentication attempts were performed.
    """
    pass


class UnavailableError(ProtocolError):
    """Raised upon receipt of an unavailable error"""
    pass


class BusyError(ProtocolError):
    """
    Raised upon receipt of a busy error during a pair setup procedure. This happens only if a parallel pairing process
    is ongoing.
    """
    pass


class InvalidError(ProtocolError):
    """
    Raised upon receipt of an error not defined in the HomeKit spec. This should basically never be raised since it is
    the default error in the protocol's error handler.
    """
    pass


class HttpException(Exception):
    """
    Used within the HTTP Parser.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class InvalidAuthTagError(ProtocolError):
    """
    Raised upon receipt of an invalid auth tag in Pair Verify Step 3.3 (Page 49).
    """
    pass


class IncorrectPairingIdError(ProtocolError):
    """
    Raised in Pair Verify Step 3.5 (Page 49) if the accessory responds with an unexpected pairing id.
    """
    pass


class InvalidSignatureError(ProtocolError):
    """
    Raised upon receipt of an invalid signature either from an accessory or from the controller.
    """
    pass


class ConfigurationError(HomeKitException):
    """
    Used if any configuration in the HomeKit AccessoryServer's context was wrong.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class FormatError(HomeKitException):
    """
    Used if any format conversion fails or is impossible.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class CharacteristicPermissionError(HomeKitException):
    """
    Used if the characteristic's permissions do not allow the action. This includes reads on write only characteristics
    and writes on read only characteristics.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class AccessoryNotFoundError(HomeKitException):
    """
    Used if a HomeKit Accessory's IP and port could not be received via Bonjour / Zeroconf. This might be a temporary
    issue due to the way Bonjour / Zeroconf works.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class EncryptionError(HomeKitException):
    """
    Used if during a transmission some errors occurred.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class AccessoryDisconnectedError(HomeKitException):
    """
    Used if a HomeKit disconnects part way through an operation or series of operations.

    It may be possible to reconnect and retry the request.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class ConfigLoadingError(HomeKitException):
    """
    Used on problems loading some config. This includes but may not be limited to:
     * problems with file permissions (file not readable)
     * the file could not be found
     * the file does not contain parseable JSON
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class ConfigSavingError(HomeKitException):
    """
    Used on problems saving some config. This includes but may not be limited to:
     * problems with file permissions (file not writable)
     * the file could not be found (occurs if the path does not exist)
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class UnpairedError(HomeKitException):
    """
    This should be raised if a paired accessory is expected but the accessory is still unpaired.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class AlreadyPairedError(HomeKitException):
    """
    This should be raised if an unpaired accessory is expected but the accessory is already paired.
    """

    def __init__(self, message):
        Exception.__init__(self, message)


class RequestRejected(HomeKitException):
    """
    Raised when a request fails with a HAP error code
    """

    def __init__(self, message, error_code):
        self.error_code = error_code
        self.message = message
        Exception.__init__(message)


class TransportNotSupportedError(HomeKitException):
    def __init__(self, transport):
        Exception.__init__(self,
                           'Transport {t} not supported. See setup.py for required dependencies.'.format(t=transport))


class DisconnectedControllerError(HomeKitException):
    def __init__(self):
        Exception.__init__(self, 'Controller has passed away')
