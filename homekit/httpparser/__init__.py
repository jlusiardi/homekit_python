class HttpResponse(object):
    STATE_PRE_STATUS = 0
    STATE_HEADERS = 1
    STATE_BODY = 2
    STATE_DONE = 3

    def __init__(self):
        self._state = HttpResponse.STATE_PRE_STATUS
        self._raw_response = bytearray()
        self._is_ready = False
        self._is_chunked = False
        self._had_empty_chunk = False
        self._content_length = -1
        self.version = None
        self.code = None
        self.reason = None
        self.headers = []
        self.body = bytearray()

    def parse(self, part):
        self._raw_response += part
        pos = self._raw_response.find(b'\r\n')
        while pos != -1:
            line = self._raw_response[:pos]
            self._raw_response = self._raw_response[pos + 2:]
            if self._state == HttpResponse.STATE_PRE_STATUS:
                # parse status line
                line = line.split(b' ', 2)
                if len(line) != 3:
                    raise HttpException()
                self.version = line[0].decode()
                self.code = int(line[1])
                self.reason = line[2].decode()
                self._state = HttpResponse.STATE_HEADERS

            elif self._state == HttpResponse.STATE_HEADERS and line == b'':
                # this is the empty line after the headers
                self._state = HttpResponse.STATE_BODY

            elif self._state == HttpResponse.STATE_HEADERS:
                # parse a header line
                line = line.split(b':', 1)
                name = line[0].decode()
                value = line[1].decode().strip()
                if name == 'Transfer-Encoding':
                    if value == 'chunked':
                        self._is_chunked = True
                elif name == 'Content-Length':
                    self._content_length = int(value)
                self.headers.append((name, value))

            elif self._state == HttpResponse.STATE_BODY:
                # print('raw', self._raw_response)
                if self._is_chunked:
                    length = int(line, 16)
                    if length > len(self._raw_response):
                        self._raw_response = line + b'\r\n' + self._raw_response
                        # the remaining bytes in raw response are not sufficient. bail out and wait for an other call.
                        break
                    if length == 0:
                        self._had_empty_chunk = True
                        self._state = HttpResponse.STATE_DONE
                        self._raw_response = self._raw_response[length + 2:]
                    else:
                        line = self._raw_response[:length]
                        self.body += line
                        self._raw_response = self._raw_response[length + 2:]
                if self._content_length > -1:
                    self.body += self._raw_response
                    self._raw_response = bytearray()

            elif self._state == HttpResponse.STATE_BODY:
                raise HttpException

            else:
                print('unknown state')

            pos = self._raw_response.find(b'\r\n')

        if self._state == HttpResponse.STATE_BODY and self._content_length > 0:
            self.body = self._raw_response

    def read(self):
        return self.body

    def is_read_completly(self):
        if self._is_chunked:
            return self._had_empty_chunk
        if self.code == 204:
            return True
        if self._content_length != -1:
            return len(self.body) == self._content_length
        if self._state == HttpResponse.STATE_PRE_STATUS or self._state == HttpResponse.STATE_HEADERS:
            return False
        raise HttpException()


class HttpException(Exception):
    def __init__(self):
        pass


if __name__ == '__main__':
    import json


    def test(data):
        res = HttpResponse()
        for i in range(0, len(data)):
            print('->', data[i].decode(), '<-')
            res.parse(data[i])
            if res.is_read_completly():
                break
        print('version:', res.version)
        print('body:', res.body.decode())
        # print('json:', json.loads(res.body.decode()))


    parts = [bytearray(
        b'HTTP/1.1 200 OK\r\nContent-Type: application/hap+json\r\nTransfer-Encoding: chunked\r\nConnection: keep-alive\r\n\r\n'),
        bytearray(
            b'5f\r\n{"characteristics":[{"aid":1,"iid":10,"value":35},{"aid":1,"iid":13,"value":36.0999984741211}]}\r\n'),
        bytearray(b'0\r\n\r\n')
    ]
    test(parts)

    parts = [bytearray(b'HTTP/1.1 204 No Content\r\n\r\n')]
    test(parts)

    parts = [bytearray(b'EVENT/1.0 200 OK\r\nContent-Type: application/hap+json\r\nTransfer-Encoding: chunked\r\n\r\n'),
             bytearray(
                 b'5f\r\n{"characteristics":[{"aid":1,"iid":10,"value":35},{"aid":1,"iid":13,"value":33.2000007629395}]}\r\n'),
             bytearray(b'0\r\n\r\n')
             ]
    test(parts)

    parts = [bytearray(
        b'HTTP/1.1 200 OK\r\nServer: BaseHTTP/0.6 Python/3.5.3\r\nDate: Mon, 04 Jun 2018 20:06:06 GMT\r\nContent-Type: application/hap+json\r\nContent-Length: 3740\r\n\r\n{"accessories": [{"services": [{"characteristics": [{"maxLen": 64, "type": "00000014-0000-1000-8000-0026BB765291", "format": "bool", "description": "Identify", "perms": ["pw"], "maxDataLen": 2097152, "iid": 3}, {"maxLen": 64, "type": "00000020-0000-1000-8000-0026BB765291", "format": "string", "description": "Manufacturer", "perms": ["pr"], "maxDataLen": 2097152, "value": "lusiardi.de", "iid": 4}, {"maxLen": 64, "type": "00000021-0000-1000-8000-0026BB765291", "format": "string", "description": "Model", "perms": ["pr"], "maxDataLen": 2097152, "value": "Demoserver", "iid": 5}, {"maxLen": 64, "type": "00000023-0000-1000-8000-0026BB765291", "format": "string", "description": "Name", "perms": ["pr"], "maxDataLen": 2097152, "value": "Notifier", "iid": 6}, {"maxLen": 64, "type": "00000030-0000-1000-8000-0026BB765291", "format": "string", "description": "Serial Number", "'),
             bytearray(
                 b'perms": ["pr"], "maxDataLen": 2097152, "value": "0001", "iid": 7}, {"maxLen": 64, "type": "00000052-0000-1000-8000-0026BB765291", "format": "string", "description": "Firmware Revision", "perms": ["pr"], "maxDataLen": 2097152, "value": "0.1", "iid": 8}], "type": "0000003E-0000-1000-8000-0026BB765291", "iid": 2}, {"characteristics": [{"maxLen": 64, "type": "00000025-0000-1000-8000-0026BB765291", "format": "bool", "description": "Switch state (on/off)", "perms": ["pw", "pr", "ev"], "maxDataLen": 2097152, "value": false, "iid": 10}, {"maxDataLen": 2097152, "minStep": 1, "description": "Brightness in percent", "unit": "percentage", "minValue": 0, "perms": ["pr", "pw", "ev"], "maxValue": 100, "maxLen": 64, "type": "00000008-0000-1000-8000-0026BB765291", "format": "int", "value": 0, "iid": 11}, {"maxDataLen": 2097152, "minStep": 1, "description": "Hue in arc degrees", "unit": "arcdegrees", "minValue": 0, "perms": ["pr", "pw", "ev"], "maxValue": 360, "maxLen": 64, "type": "00000013-0000-1000-8000-0026BB765291", "form'),
             bytearray(
                 b'at": "float", "value": 0, "iid": 12}, {"maxDataLen": 2097152, "minStep": 1, "description": "Saturation in percent", "unit": "percentage", "minValue": 0, "perms": ["pr", "pw", "ev"], "maxValue": 100, "maxLen": 64, "type": "0000002F-0000-1000-8000-0026BB765291", "format": "float", "value": 0, "iid": 13}], "type": "00000043-0000-1000-8000-0026BB765291", "iid": 9}], "aid": 1}, {"services": [{"characteristics": [{"maxLen": 64, "type": "00000014-0000-1000-8000-0026BB765291", "format": "bool", "description": "Identify", "perms": ["pw"], "maxDataLen": 2097152, "iid": 16}, {"maxLen": 64, "type": "00000020-0000-1000-8000-0026BB765291", "format": "string", "description": "Manufacturer", "perms": ["pr"], "maxDataLen": 2097152, "value": "lusiardi.de", "iid": 17}, {"maxLen": 64, "type": "00000021-0000-1000-8000-0026BB765291", "format": "string", "description": "Model", "perms": ["pr"], "maxDataLen": 2097152, "value": "Demoserver", "iid": 18}, {"maxLen": 64, "type": "00000023-0000-1000-8000-0026BB765291", "format": "string"'),
             bytearray(
                 b', "description": "Name", "perms": ["pr"], "maxDataLen": 2097152, "value": "Dummy", "iid": 19}, {"maxLen": 64, "type": "00000030-0000-1000-8000-0026BB765291", "format": "string", "description": "Serial Number", "perms": ["pr"], "maxDataLen": 2097152, "value": "0001", "iid": 20}, {"maxLen": 64, "type": "00000052-0000-1000-8000-0026BB765291", "format": "string", "description": "Firmware Revision", "perms": ["pr"], "maxDataLen": 2097152, "value": "0.1", "iid": 21}], "type": "0000003E-0000-1000-8000-0026BB765291", "iid": 15}, {"characteristics": [{"perms": ["pw", "pr"], "maxLen": 64, "minValue": 2, "type": "00000023-0000-1000-8000-0026BB765291", "format": "float", "description": "Test", "minStep": 0.25, "maxDataLen": 2097152, "iid": 23}], "type": "00000040-0000-1000-8000-0026BB765291", "iid": 22}], "aid": 14}]}')
             ]
    test(parts)

    parts = [
        bytearray(
            b'HTTP/1.1 200 OK\r\nServer: BaseHTTP/0.6 Python/3.5.3\r\nDate: Mon, 04 Jun 2018 21:38:07 GMT\r\nContent-Type: application/hap+json\r\nContent-Length: 3740\r\n\r\n{"accessories": [{"aid": 1, "services": [{"type": "0000003E-0000-1000-8000-0026BB765291", "characteristics": [{"format": "bool", "maxLen": 64, "iid": 3, "description": "Identify", "perms": ["pw"], "type": "00000014-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "lusiardi.de", "format": "string", "maxLen": 64, "iid": 4, "description": "Manufacturer", "perms": ["pr"], "type": "00000020-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Demoserver", "format": "string", "maxLen": 64, "iid": 5, "description": "Model", "perms": ["pr"], "type": "00000021-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Notifier", "format": "string", "maxLen": 64, "iid": 6, "description": "Name", "perms": ["pr"], "type": "00000023-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0001", "format": "string", "maxLen": 64, "iid":'),
        bytearray(
            b' 7, "description": "Serial Number", "perms": ["pr"], "type": "00000030-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0.1", "format": "string", "maxLen": 64, "iid": 8, "description": "Firmware Revision", "perms": ["pr"], "type": "00000052-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}], "iid": 2}, {"type": "00000043-0000-1000-8000-0026BB765291", "characteristics": [{"value": false, "format": "bool", "maxLen": 64, "iid": 10, "description": "Switch state (on/off)", "perms": ["pw", "pr", "ev"], "type": "00000025-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"maxValue": 100, "format": "int", "minStep": 1, "description": "Brightness in percent", "perms": ["pr", "pw", "ev"], "maxDataLen": 2097152, "type": "00000008-0000-1000-8000-0026BB765291", "maxLen": 64, "iid": 11, "value": 0, "unit": "percentage", "minValue": 0}, {"maxValue": 360, "format": "float", "minStep": 1, "description": "Hue in arc degrees", "perms": ["pr", "pw", "ev"], "maxDataLen": 2097152, "type": "00000013-0000-1000'),
        bytearray(
            b'-8000-0026BB765291", "maxLen": 64, "iid": 12, "value": 0, "unit": "arcdegrees", "minValue": 0}, {"maxValue": 100, "format": "float", "minStep": 1, "description": "Saturation in percent", "perms": ["pr", "pw", "ev"], "maxDataLen": 2097152, "type": "0000002F-0000-1000-8000-0026BB765291", "maxLen": 64, "iid": 13, "value": 0, "unit": "percentage", "minValue": 0}], "iid": 9}]}, {"aid": 14, "services": [{"type": "0000003E-0000-1000-8000-0026BB765291", "characteristics": [{"format": "bool", "maxLen": 64, "iid": 16, "description": "Identify", "perms": ["pw"], "type": "00000014-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "lusiardi.de", "format": "string", "maxLen": 64, "iid": 17, "description": "Manufacturer", "perms": ["pr"], "type": "00000020-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Demoserver", "format": "string", "maxLen": 64, "iid": 18, "description": "Model", "perms": ["pr"], "type": "00000021-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "Dummy", "fo'),
        bytearray(
            b'rmat": "string", "maxLen": 64, "iid": 19, "description": "Name", "perms": ["pr"], "type": "00000023-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0001", "format": "string", "maxLen": 64, "iid": 20, "description": "Serial Number", "perms": ["pr"], "type": "00000030-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}, {"value": "0.1", "format": "string", "maxLen": 64, "iid": 21, "description": "Firmware Revision", "perms": ["pr"], "type": "00000052-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}], "iid": 15}, {"type": "00000040-0000-1000-8000-0026BB765291", "characteristics": [{"minStep": 0.25, "format": "float", "maxLen": 64, "iid": 23, "description": "Test", "perms": ["pw", "pr"], "minValue": 2, "type": "00000023-0000-1000-8000-0026BB765291", "maxDataLen": 2097152}], "iid": 22}]}]}')
    ]
    test(parts)

    # koogeek get accessories
    parts = [
        bytearray(
            b'HTTP/1.1 200 OK\r\nConnection: keep-alive\r\nTransfer-Encoding: chunked\r\nContent-Type: application/hap+json\r\n\r\n3c6\r\n{"accessories":[{"aid":1,"services":[{"type":"3E","iid":1,"characteristics":[{"iid":2,"value":"Koogeek-P1-770D90","format":"string","maxLen":64,"type":"23","perms":["pr"]},{"iid":3,"value":"Koogeek","format":"string","maxLen":64,"type":"20","perms":["pr"]},{"iid":4,"value":"P1EU","format":"string","maxLen":64,"type":"21","perms":["pr"]},{"iid":5,"value":"EUCP031715001435","format":"string","maxLen":64,"type":"30","perms":["pr"]},{"iid":6,"format":"bool","type":"14","perms":["pw"]},{"iid":37,"value":"1.2.9","format":"string","type":"52","perms":["pr"]}]},{"type":"47","iid":7,"primary":true,"characteristics":[{"iid":8,"value":false,"format":"bool","type":"25","perms":["pr","pw","ev"],"ev":false},{"iid":9,"value":true,"format":"bool","type":"26","perms":["pr","ev"],"ev":false},{"iid":10,"value":"Outlet","format":"string","maxLen":64,"type":"23","perms":["pr"]}]},{"type":"4aaaf940-0dec-11e5-b939-0800200'),
        bytearray(
            b'c9a66","iid":11,"characteristics":[{"iid":12,"value":"\r\n3fb\r\nAHAAAAABAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA","format":"tlv8","description":"TIMER_SETTINGS","type":"4aaaf942-0dec-11e5-b939-0800200c9a66","perms":["pr","pw"]}]},{"type":"151909D0-3802-11E4-916C-0800200C9A66","iid":13,"hidden":true,"characteristics":[{"iid":14,"value":"url,data","format":"string","description":"FW Upgrade supported types","type":"151909D2-3802-11E4-916C-0800200C9A66","perms":["pr","hd"]},{"iid":15,"format":"string","description":"FW Upgrade URL","maxLen":256,"type":"151909D1-3802-11E4-916C-0800200C9A66","perms":["pw","hd"]},{"iid":16,"value":0,"format":"int","description":"FW Upgrade Status","type":"151909D6-3802-11E4-916C-0800200C9A66","perms":["pr","ev","hd"],"ev":false},{"iid":17,"format":"data","description":"FW Upgrade Data","type":"151909D7-3802-11E4-916C-0800200C9A66","perms":["pw","hd"]}]},{"type":"151909D3-3802-11E4-9')
    ]
    test(parts)
