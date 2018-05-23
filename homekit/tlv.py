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


class TLV:
    """
    as described in Appendix 12 (page 251)
    """

    # Steps
    M1 = bytearray(b'\x01')
    M2 = bytearray(b'\x02')
    M3 = bytearray(b'\x03')
    M4 = bytearray(b'\x04')
    M5 = bytearray(b'\x05')
    M6 = bytearray(b'\x06')

    # Methods (see table 4-4 page 60)
    PairSetup = bytearray(b'\x01')
    PairVerify = bytearray(b'\x02')
    AddPairing = bytearray(b'\x03')
    RemovePairing = bytearray(b'\x04')
    ListPairings = bytearray(b'\x05')

    # TLV Values (see table 4-6 page 61)
    kTLVType_Method = 0
    kTLVType_Identifier = 1
    kTLVType_Salt = 2
    kTLVType_PublicKey = 3
    kTLVType_Proof = 4
    kTLVType_EncryptedData = 5
    kTLVType_State = 6
    kTLVType_Error = 7
    kTLVType_RetryDelay = 8
    kTLVType_Certificate = 9
    kTLVType_Signature = 10
    kTLVType_Permissions = 11  # 0x00 => reg. user, 0x01 => admin
    kTLVType_Permission_RegularUser = bytearray(b'\x00')
    kTLVType_Permission_AdminUser = bytearray(b'\x01')
    kTLVType_FragmentData = 12
    kTLVType_FragmentLast = 13
    kTLVType_Separator = 255

    # Errors (see table 4-5 page 60)
    kTLVError_Unknown = bytearray(b'\x01')
    kTLVError_Authentication = bytearray(b'\x02')
    kTLVError_Backoff = bytearray(b'\x03')
    kTLVError_MaxPeers = bytearray(b'\x04')
    kTLVError_MaxTries = bytearray(b'\x05')
    kTLVError_Unavailable = bytearray(b'\x06')
    kTLVError_Busy = bytearray(b'\x07')

    def __init__(self):
        pass

    @staticmethod
    def decode_bytes(bs) -> dict:
        return TLV.decode_bytearray(bytearray(bs))

    @staticmethod
    def decode_bytearray(ba: bytearray) -> dict:
        result = {}
        # do not influence caller!
        tail = ba.copy()
        while len(tail) > 0:
            key = tail.pop(0)
            length = tail.pop(0)
            value = tail[:length]
            if length != len(value):
                raise TlvParseException('Not enough data for length {}'.format(length))
            tail = tail[length:]

            if key not in result:
                result[key] = value
            else:
                for b in value:
                    result[key].append(b)
        return result

    @staticmethod
    def decode_bytes_to_list(bs) -> dict:
        return TLV.decode_bytearray_to_list(bytearray(bs))

    @staticmethod
    def decode_bytearray_to_list(ba: bytearray) -> list:
        result = []
        # do not influence caller!
        tail = ba.copy()
        while len(tail) > 0:
            key = tail.pop(0)
            length = tail.pop(0)
            value = tail[:length]
            if length != len(value):
                raise TlvParseException('Not enough data for length {}'.format(length))
            tail = tail[length:]

            result.append((key, value))
        return result

    @staticmethod
    def validate_key(k: int) -> bool:
        try:
            val = int(k)
            if val < 0 or val > 255:
                valid = False
            else:
                valid = True
        except ValueError:
            valid = False
        return valid

    @staticmethod
    def encode_dict(d: dict) -> bytearray:
        result = bytearray()
        for key in d:
            if not TLV.validate_key(key):
                raise ValueError('Invalid key')

            value = d[key]

            # handle separators properly
            if key == TLV.kTLVType_Separator:
                if len(value) == 0:
                    result.append(key)
                    result.append(0)
                else:
                    raise ValueError('Separator must not have data')

            while len(value) > 0:
                result.append(key)
                if len(value) > 255:
                    length = 255
                    result.append(length)
                    for b in value[:length]:
                        result.append(b)
                    value = value[length:]
                else:
                    length = len(value)
                    result.append(length)
                    for b in value[:length]:
                        result.append(b)
                    value = value[length:]
        return result

    @staticmethod
    def encode_list(d: list) -> bytearray:
        result = bytearray()
        for p in d:
            (key, value) = p
            if not TLV.validate_key(key):
                raise ValueError('Invalid key')

            #value = d[key]

            # handle separators properly
            if key == TLV.kTLVType_Separator:
                if len(value) == 0:
                    result.append(key)
                    result.append(0)
                else:
                    raise ValueError('Separator must not have data')

            while len(value) > 0:
                result.append(key)
                if len(value) > 255:
                    length = 255
                    result.append(length)
                    for b in value[:length]:
                        result.append(b)
                    value = value[length:]
                else:
                    length = len(value)
                    result.append(length)
                    for b in value[:length]:
                        result.append(b)
                    value = value[length:]
        return result

    @staticmethod
    def to_string(d: dict) -> str:
        res = '{\n'
        for k in sorted(d.keys()):
            res += '  {k}: {v}\n'.format(k=k, v=d[k])
        res += '}\n'
        return res


class TlvParseException(Exception):
    """Raised upon parse error with some TLV"""
    pass



if __name__ == '__main__':
    # TLV Example 1 from Chap 12.1.2 Page 252
    example_1 = bytearray.fromhex('060103010568656c6c6f')
    dict_1_1 = TLV.decode_bytearray(example_1)

    bytearray_1 = TLV.encode_dict(dict_1_1)
    dict_1_2 = TLV.decode_bytearray(bytearray_1)
    assert dict_1_1 == dict_1_2

    # TLV Example 1 from Chap 12.1.2 Page 252
    example_2 = bytearray.fromhex('060103' + ('09FF' + 255 * '61' + '092D' + 45 * '61') + '010568656c6c6f')
    dict_2_1 = TLV.decode_bytearray(example_2)

    bytearray_2 = TLV.encode_dict(dict_2_1)
    dict_2_2 = TLV.decode_bytearray(bytearray_2)
    assert dict_2_1 == dict_2_2

    example_3 = {
        TLV.kTLVType_Separator: bytes()
    }
    print(TLV.encode_dict(example_3))

    print(TLV.to_string(dict_2_1))
