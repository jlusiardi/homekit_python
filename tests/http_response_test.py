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
import unittest
import json

from homekit.http_impl.response import *


class TestHttpResponse(unittest.TestCase):

    def parse(data):
        response = HttpResponse()
        for i in range(0, len(data)):
            response.parse(data[i])
            if response.is_read_completely():
                break
        return response

    def test_example1(self):
        parts = [bytearray(
            b'HTTP/1.1 200 OK\r\nContent-Type: application/hap+json\r\n'
            b'Transfer-Encoding: chunked\r\nConnection: keep-alive\r\n\r\n'),
            bytearray(
                b'5f\r\n{"characteristics":[{"aid":1,"iid":10,"value":35},'
                b'{"aid":1,"iid":13,"value":36.0999984741211}]}\r\n'),
            bytearray(b'0\r\n\r\n')
        ]
        res = TestHttpResponse.parse(parts)
        self.assertEqual(res.code, 200)
        self.assertEqual(res.get_http_name(), 'HTTP')
        self.assertEqual(
            res.body,
            b'{"characteristics":[{"aid":1,"iid":10,"value":35},{"aid":1,"iid":13,"value":36.0999984741211}]}')
        j = json.loads(res.body.decode())

    def test_example2(self):
        parts = [
            bytearray(b'EVENT/1.0 200 OK\r\nContent-Type: application/hap+json\r\nTransfer-Encoding: chunked\r\n\r\n'),
            bytearray(
                b'5f\r\n{"characteristics":[{"aid":1,"iid":10,"value":35},{"aid":1,"iid":13,"value":33.2000007629395}]}\r\n'),
            bytearray(b'0\r\n\r\n')
            ]
        res = TestHttpResponse.parse(parts)
        self.assertEqual(res.code, 200)
        self.assertEqual(res.get_http_name(), 'EVENT')
        self.assertEqual(
            res.body,
            b'{"characteristics":[{"aid":1,"iid":10,"value":35},{"aid":1,"iid":13,"value":33.2000007629395}]}')
        j = json.loads(res.body.decode())
        self.assertEqual(j['characteristics'][1]['value'], 33.2000007629395)

    def test_example3(self):
        parts = [bytearray(
            b'HTTP/1.1 200 OK\r\nServer: BaseHTTP/0.6 Python/3.5.3\r\nDate: Mon, 04 Jun 2018 20:06:06 GMT\r\nContent-Type: application/hap+json\r\nContent-Length: 3740\r\n\r\n{"accessories": [{"services": [{"characteristics": [{"maxLen": 64, "type": "00000014-0000-1000-8000-0026BB765291", "format": "bool", "description": "Identify", "perms": ["pw"], "maxDataLen": 2097152, "iid": 3}, {"maxLen": 64, "type": "00000020-0000-1000-8000-0026BB765291", "format": "string", "description": "Manufacturer", "perms": ["pr"], "maxDataLen": 2097152, "value": "lusiardi.de", "iid": 4}, {"maxLen": 64, "type": "00000021-0000-1000-8000-0026BB765291", "format": "string", "description": "Model", "perms": ["pr"], "maxDataLen": 2097152, "value": "Demoserver", "iid": 5}, {"maxLen": 64, "type": "00000023-0000-1000-8000-0026BB765291", "format": "string", "description": "Name", "perms": ["pr"], "maxDataLen": 2097152, "value": "Notifier", "iid": 6}, {"maxLen": 64, "type": "00000030-0000-1000-8000-0026BB765291", "format": "string", "description": "Serial Number", "'),
            bytearray(
                b'perms": ["pr"], "maxDataLen": 2097152, "value": "0001", "iid": 7}, {"maxLen": 64, "type": "00000052-0000-1000-8000-0026BB765291", "format": "string", "description": "Firmware Revision", "perms": ["pr"], "maxDataLen": 2097152, "value": "0.1", "iid": 8}], "type": "0000003E-0000-1000-8000-0026BB765291", "iid": 2}, {"characteristics": [{"maxLen": 64, "type": "00000025-0000-1000-8000-0026BB765291", "format": "bool", "description": "Switch state (on/off)", "perms": ["pw", "pr", "ev"], "maxDataLen": 2097152, "value": false, "iid": 10}, {"maxDataLen": 2097152, "minStep": 1, "description": "Brightness in percent", "unit": "percentage", "minValue": 0, "perms": ["pr", "pw", "ev"], "maxValue": 100, "maxLen": 64, "type": "00000008-0000-1000-8000-0026BB765291", "format": "int", "value": 0, "iid": 11}, {"maxDataLen": 2097152, "minStep": 1, "description": "Hue in arc degrees", "unit": "arcdegrees", "minValue": 0, "perms": ["pr", "pw", "ev"], "maxValue": 360, "maxLen": 64, "type": "00000013-0000-1000-8000-0026BB765291", "form'),
            bytearray(
                b'at": "float", "value": 0, "iid": 12}, {"maxDataLen": 2097152, "minStep": 1, "description": "Saturation in percent", "unit": "percentage", "minValue": 0, "perms": ["pr", "pw", "ev"], "maxValue": 100, "maxLen": 64, "type": "0000002F-0000-1000-8000-0026BB765291", "format": "float", "value": 0, "iid": 13}], "type": "00000043-0000-1000-8000-0026BB765291", "iid": 9}], "aid": 1}, {"services": [{"characteristics": [{"maxLen": 64, "type": "00000014-0000-1000-8000-0026BB765291", "format": "bool", "description": "Identify", "perms": ["pw"], "maxDataLen": 2097152, "iid": 16}, {"maxLen": 64, "type": "00000020-0000-1000-8000-0026BB765291", "format": "string", "description": "Manufacturer", "perms": ["pr"], "maxDataLen": 2097152, "value": "lusiardi.de", "iid": 17}, {"maxLen": 64, "type": "00000021-0000-1000-8000-0026BB765291", "format": "string", "description": "Model", "perms": ["pr"], "maxDataLen": 2097152, "value": "Demoserver", "iid": 18}, {"maxLen": 64, "type": "00000023-0000-1000-8000-0026BB765291", "format": "string"'),
            bytearray(
                b', "description": "Name", "perms": ["pr"], "maxDataLen": 2097152, "value": "Dummy", "iid": 19}, {"maxLen": 64, "type": "00000030-0000-1000-8000-0026BB765291", "format": "string", "description": "Serial Number", "perms": ["pr"], "maxDataLen": 2097152, "value": "0001", "iid": 20}, {"maxLen": 64, "type": "00000052-0000-1000-8000-0026BB765291", "format": "string", "description": "Firmware Revision", "perms": ["pr"], "maxDataLen": 2097152, "value": "0.1", "iid": 21}], "type": "0000003E-0000-1000-8000-0026BB765291", "iid": 15}, {"characteristics": [{"perms": ["pw", "pr"], "maxLen": 64, "minValue": 2, "type": "00000023-0000-1000-8000-0026BB765291", "format": "float", "description": "Test", "minStep": 0.25, "maxDataLen": 2097152, "iid": 23}], "type": "00000040-0000-1000-8000-0026BB765291", "iid": 22}], "aid": 14}]}')
        ]
        res = TestHttpResponse.parse(parts)
        self.assertEqual(res.code, 200)
        self.assertEqual(res.get_http_name(), 'HTTP')
        j = json.loads(res.body.decode())


    def test_example4(self):
        parts = [bytearray(
            b'HTTP/1.1 200 OK\r\nServer: BaseHTTP/0.6 Python/3.5.3\r\nDate: Mon, 04 Jun 2018 21:38:07 GMT\r\nContent-Type: application/hap+json\r\nContent-Length: 3740\r\n\r\n{"accessories": [{"aid": 1, "services": [{"type": "0000003E-0000-1000-8000-0026BB765291", "characteristics": [{"format": "bool", "maxLen": 64, "iid": 3, "description": "Identify", "perms": ["pw"], "type": "00000014-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "lusiardi.de", "format": "string", "maxLen": 64, "iid": 4, "description": "Manufacturer", "perms": ["pr"], "type": "00000020-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Demoserver", "format": "string", "maxLen": 64, "iid": 5, "description": "Model", "perms": ["pr"], "type": "00000021-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Notifier", "format": "string", "maxLen": 64, "iid": 6, "description": "Name", "perms": ["pr"], "type": "00000023-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0001", "format": "string", "maxLen": 64, "iid":'),
        bytearray(
            b' 7, "description": "Serial Number", "perms": ["pr"], "type": "00000030-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0.1", "format": "string", "maxLen": 64, "iid": 8, "description": "Firmware Revision", "perms": ["pr"], "type": "00000052-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}], "iid": 2}, {"type": "00000043-0000-1000-8000-0026BB765291", "characteristics": [{"value": false, "format": "bool", "maxLen": 64, "iid": 10, "description": "Switch state (on/off)", "perms": ["pw", "pr", "ev"], "type": "00000025-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"maxValue": 100, "format": "int", "minStep": 1, "description": "Brightness in percent", "perms": ["pr", "pw", "ev"], "maxDataLen": 2097152, "type": "00000008-0000-1000-8000-0026BB765291", "maxLen": 64, "iid": 11, "value": 0, "unit": "percentage", "minValue": 0}, {"maxValue": 360, "format": "float", "minStep": 1, "description": "Hue in arc degrees", "perms": ["pr", "pw", "ev"], "maxDataLen": 2097152, "type": "00000013-0000-1000'),
        bytearray(
            b'-8000-0026BB765291", "maxLen": 64, "iid": 12, "value": 0, "unit": "arcdegrees", "minValue": 0}, {"maxValue": 100, "format": "float", "minStep": 1, "description": "Saturation in percent", "perms": ["pr", "pw", "ev"], "maxDataLen": 2097152, "type": "0000002F-0000-1000-8000-0026BB765291", "maxLen": 64, "iid": 13, "value": 0, "unit": "percentage", "minValue": 0}], "iid": 9}]}, {"aid": 14, "services": [{"type": "0000003E-0000-1000-8000-0026BB765291", "characteristics": [{"format": "bool", "maxLen": 64, "iid": 16, "description": "Identify", "perms": ["pw"], "type": "00000014-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "lusiardi.de", "format": "string", "maxLen": 64, "iid": 17, "description": "Manufacturer", "perms": ["pr"], "type": "00000020-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Demoserver", "format": "string", "maxLen": 64, "iid": 18, "description": "Model", "perms": ["pr"], "type": "00000021-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Dummy", "fo'),
        bytearray(
            b'rmat": "string", "maxLen": 64, "iid": 19, "description": "Name", "perms": ["pr"], "type": "00000023-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0001", "format": "string", "maxLen": 64, "iid": 20, "description": "Serial Number", "perms": ["pr"], "type": "00000030-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0.1", "format": "string", "maxLen": 64, "iid": 21, "description": "Firmware Revision", "perms": ["pr"], "type": "00000052-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}], "iid": 15}, {"type": "00000040-0000-1000-8000-0026BB765291", "characteristics": [{"minStep": 0.25, "format": "float", "maxLen": 64, "iid": 23, "description": "Test", "perms": ["pw", "pr"], "minValue": 2, "type": "00000023-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}], "iid": 22}]}]}')
        ]
        res = TestHttpResponse.parse(parts)
        self.assertEqual(res.code, 200)
        self.assertEqual(res.get_http_name(), 'HTTP')
        j = json.loads(res.body.decode())
