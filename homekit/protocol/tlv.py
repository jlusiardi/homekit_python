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
    DEBUG = False

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
    kTLVType_Separator_Pair = [255, bytearray(b'')]

    # Errors (see table 4-5 page 60)
    kTLVError_Unknown = bytearray(b'\x01')
    kTLVError_Authentication = bytearray(b'\x02')
    kTLVError_Backoff = bytearray(b'\x03')
    kTLVError_MaxPeers = bytearray(b'\x04')
    kTLVError_MaxTries = bytearray(b'\x05')
    kTLVError_Unavailable = bytearray(b'\x06')
    kTLVError_Busy = bytearray(b'\x07')

    @staticmethod
    def decode_bytes(bs) -> list:
        return TLV.decode_bytearray(bytearray(bs))

    @staticmethod
    def decode_bytearray(ba: bytearray) -> list:
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

            if len(result) > 0 and result[-1][0] == key:
                result[-1][1] += value
            else:
                result.append([key, value])
        if TLV.DEBUG:
            print('receiving ' + TLV.to_string(result))
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
    def encode_list(d: list) -> bytearray:
        if TLV.DEBUG:
            print('sending ' + TLV.to_string(d))
        result = bytearray()
        for p in d:
            (key, value) = p
            if not TLV.validate_key(key):
                raise ValueError('Invalid key')

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
    def to_string(d) -> str:
        if isinstance(d, dict):
            res = '{\n'
            for k in d.keys():
                res += '  {k}: ({l} bytes) {v}\n'.format(k=k, v=d[k], l=len(d[k]))
            res += '}\n'
        else:
            res = '[\n'
            for k in d:
                res += '  {k}: ({l} bytes) {v}\n'.format(k=k[0], v=k[1], l=len(k[1]))
            res += ']\n'
        return res


    @staticmethod
    def reorder(tlv_array, preferred_order):
        """
        This function is used to reorder the key value pairs of a TLV list according to a preferred order. If key from
        the preferred_order list is not found, it is ignored. If a pair's key is not in the preferred order list it is
        ignored as well.

        It is mostly used, if some accessory does not respect the order mentioned in the specification.

        :param tlv_array: a list of tupels containing key and value of the TLV
        :param preferred_order: a list of keys describing how the key value pairs should be sorted.
        :return: a TLV list containing only pairs whose key was in the preferred order list sorted by that order.
        """
        tmp = []
        for key in preferred_order:
            for item in tlv_array:
                if item[0] == key:
                    tmp.append(item)
        return tmp


class TlvParseException(Exception):
    """Raised upon parse error with some TLV"""
    pass

