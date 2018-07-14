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

from homekit.http_impl.response import HttpException, HttpResponse
from homekit.http_impl.secure_http import SecureHttp
from homekit.http_impl.http_client import HomeKitHTTPConnection
from homekit.http_impl.contentTypes import HttpContentTypes


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
            200: 'OK',
            204: 'No Content',
            207: 'Multi-Status',
            400: 'Bad Request',
            405: 'Method Not Allowed',
            429: 'Too Many Requests',
            470: 'Connection Authorization Required',
            500: 'Internal Server Error'
        }
        self._categories_rev = {self._codes[k]: k for k in self._codes.keys()}

    def __getitem__(self, item):
        if item in self._codes:
            return self._codes[item]

        raise KeyError('Item {item} not found'.format_map(item=item))


HttpStatusCodes = _HttpStatusCodes()
