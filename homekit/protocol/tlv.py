#
# Copyright 2018-2020 Joachim Lusiardi
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
import logging
import enum

logger = logging.getLogger('homekit.protocol.tlv')


class Steps(enum.IntEnum):
    # Steps (see Table 5-6 TLV Values under kTLVType_State in Spec R2 page 51)
    M1 = 1
    M2 = 2
    M3 = 3
    M4 = 4
    M5 = 5
    M6 = 6


class Methods(enum.IntEnum):
    """
    TLV id for methods.
    See:
     - table 4-4 page 60 in spec R1 or
     - table 5-3 page 49 in spec R2
    """
    PairSetup = 1
    PairVerify = 2
    AddPairing = 3
    RemovePairing = 4
    ListPairings = 5
    # table 6-27 page 116 spec R1 / table 7-38 page 111 spec R2
    kTLVMethod_Resume = 0x06


class Errors(enum.IntEnum):
    """
    TLV id for errors.
    See:
     - table 4-5 page 60 in spec R1 or
     - table 5-5 page 50 in spec R2
    """
    kTLVError_Unknown = 1
    kTLVError_Authentication = 2
    kTLVError_Backoff = 3
    kTLVError_MaxPeers = 4
    kTLVError_MaxTries = 5
    kTLVError_Unavailable = 6
    kTLVError_Busy = 7


class Types(enum.IntEnum):
    """
    TLV id for values.
    See:
     - table 4-6 page 61 in spec R1 or
     - table 5-6 page 51 in spec R2

    Additional types (SessionId) can be found in
     - table 6-27 page 116 spec R1
     - table 7-38 page 111 spec R2
    and (for BLE):
     - table 6-9 page 98 spec R1
     - table 7-10 page 92 spec R2
    """
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
    kTLVType_Signature = 0x0a
    kTLVType_Permissions = 0x0b  # 0x00 => reg. user, 0x01 => admin
    kTLVType_Permission_RegularUser = 0  # bytearray(b'\x00')
    kTLVType_Permission_AdminUser = 1  # bytearray(b'\x01')
    kTLVType_FragmentData = 0x0c
    kTLVType_FragmentLast = 0x0d
    kTLVType_Flags = 0x13
    kTLVType_Separator = 255
    # kTLVType_Separator_Pair = [255, bytearray(b'')]
    # table 6-27 page 116 spec R1 / table 7-38 page 111 spec R2
    kTLVType_SessionID = 0x0e

    kTLVHAPParamValue = 0x01
    kTLVHAPParamAdditionalAuthorizationData = 0x02
    kTLVHAPParamOrigin = 0x03
    kTLVHAPParamCharacteristicType = 0x04
    kTLVHAPParamCharacteristicInstanceId = 0x05
    kTLVHAPParamServiceType = 0x06
    kTLVHAPParamServiceInstanceId = 0x07
    kTLVHAPParamTTL = 0x08
    kTLVHAPParamParamReturnResponse = 0x09
    kTLVHAPParamHAPCharacteristicPropertiesDescriptor = 0x0a
    kTLVHAPParamGATTUserDescriptionDescriptor = 0x0b
    kTLVHAPParamGATTPresentationFormatDescriptor = 0x0c
    kTLVHAPParamGATTValidRange = 0x0d
    kTLVHAPParamHAPStepValueDescriptor = 0x0e
    kTLVHAPParamHAPServiceProperties = 0x0f
    kTLVHAPParamHAPLinkedServices = 0x10
    kTLVHAPParamHAPValidValuesDescriptor = 0x11
    kTLVHAPParamHAPValidValuesRangeDescriptor = 0x12


class TLV:
    """
    as described in Appendix 12 (page 251)
    """

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
                if item.type_id == key:
                    tmp.append(item)
        return tmp
