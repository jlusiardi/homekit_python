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


class _HapStatusCodes(object):
    """
    This data is taken from Table 5-12 HAP Satus Codes on page 80.
    """
    SUCCESS = 0
    INSUFFICIENT_PRIVILEGES = -70401
    UNABLE_TO_COMMUNICATE = -70402
    RESOURCE_BUSY = -70403
    CANT_WRITE_READ_ONLY = -70404
    CANT_READ_WRITE_ONLY = -70405
    NOTIFICATION_NOT_SUPPORTED = -70406
    OUT_OF_RESOURCES = -70407
    TIMED_OUT = -70408
    RESOURCE_NOT_EXIST = -70409
    INVALID_VALUE = -70410
    INSUFFICIENT_AUTH = -70411

    def __init__(self):
        self._codes = {
            _HapStatusCodes.SUCCESS: 'This specifies a success for the request.',
            _HapStatusCodes.INSUFFICIENT_PRIVILEGES: 'Request denied due to insufficient privileges.',
            _HapStatusCodes.UNABLE_TO_COMMUNICATE:
                'Unable to communicate with requested service, e.g. the power to the accessory was turned off.',
            _HapStatusCodes.RESOURCE_BUSY: 'Resource is busy, try again.',
            _HapStatusCodes.CANT_WRITE_READ_ONLY: 'Cannot write to read only characteristic.',
            _HapStatusCodes.CANT_READ_WRITE_ONLY: 'Cannot read from a write only characteristic.',
            _HapStatusCodes.NOTIFICATION_NOT_SUPPORTED: 'Notification is not supported for characteristic.',
            _HapStatusCodes.OUT_OF_RESOURCES: 'Out of resources to process request.',
            _HapStatusCodes.TIMED_OUT: 'Operation timed out.',
            _HapStatusCodes.RESOURCE_NOT_EXIST: 'Resource does not exist.',
            _HapStatusCodes.INVALID_VALUE: 'Accessory received an invalid value in a write request.',
            _HapStatusCodes.INSUFFICIENT_AUTH: 'Insufficient Authorization.'
        }

        self._categories_rev = {self._codes[k]: k for k in self._codes.keys()}

    def __getitem__(self, item):
        if item in self._codes:
            return self._codes[item]

        raise KeyError('Item {item} not found'.format(item=item))


class _HttpContentTypes:
    JSON = 'application/hap+json'
    TLV = 'application/pairing+tlv8'


class _HttpStatusCodes:
    """
    See Table 4-2 Chapter 4.15 Page 59
    """
    OK = 200
    NO_CONTENT = 204
    MULTI_STATUS = 207
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    TOO_MANY_REQUESTS = 429
    CONNECTION_AUTHORIZATION_REQUIRED = 470
    INTERNAL_SERVER_ERROR = 500

    def __init__(self):
        self._codes = {
            _HttpStatusCodes.OK: 'OK',
            _HttpStatusCodes.NO_CONTENT: 'No Content',
            _HttpStatusCodes.MULTI_STATUS: 'Multi-Status',
            _HttpStatusCodes.BAD_REQUEST: 'Bad Request',
            _HttpStatusCodes.METHOD_NOT_ALLOWED: 'Method Not Allowed',
            _HttpStatusCodes.TOO_MANY_REQUESTS: 'Too Many Requests',
            _HttpStatusCodes.CONNECTION_AUTHORIZATION_REQUIRED: 'Connection Authorization Required',
            _HttpStatusCodes.INTERNAL_SERVER_ERROR: 'Internal Server Error'
        }
        self._categories_rev = {self._codes[k]: k for k in self._codes.keys()}

    def __getitem__(self, item):
        if item in self._codes:
            return self._codes[item]

        raise KeyError('Item {item} not found'.format(item=item))


HapStatusCodes = _HapStatusCodes()
HttpStatusCodes = _HttpStatusCodes()
HttpContentTypes = _HttpContentTypes
