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

from http.client import HTTPConnection


class HomeKitHTTPConnection(HTTPConnection):

    def _send_output(self, message_body=None, encode_chunked=False):
        """
        Acts like the original HTTPConnection._send_output but makes sure the 
        headers and the body are sent in one packet. This fixes issues with 
        some homekit devices. See for more details:
         * https://github.com/jlusiardi/homekit_python/issues/12
         * https://github.com/jlusiardi/homekit_python/issues/16

        Send the currently buffered request and clear the buffer.

        Appends an extra \\r\\n to the buffer.
        A message_body may be specified, to be appended to the request.
        """
        self._buffer.extend((b"", b""))
        msg = b"\r\n".join(self._buffer)
        del self._buffer[:]

        if message_body is not None:
            msg = msg + message_body

        self.send(msg)
