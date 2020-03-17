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
import logging

logger = logging.getLogger('homekit.protocol.tlv')


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
    kTLVType_Separator_Pair = [255, bytearray(b'')]
    kTLVType_SessionID = 0x0e   # Table 6-27 page 116

    # Errors (see table 4-5 page 60)
    kTLVError_Unknown = bytearray(b'\x01')
    kTLVError_Authentication = bytearray(b'\x02')
    kTLVError_Backoff = bytearray(b'\x03')
    kTLVError_MaxPeers = bytearray(b'\x04')
    kTLVError_MaxTries = bytearray(b'\x05')
    kTLVError_Unavailable = bytearray(b'\x06')
    kTLVError_Busy = bytearray(b'\x07')

    # Table 6-27 page 116
    kTLVMethod_Resume = 0x07

    # Additional Parameter Types for BLE (Table 6-9 page 98)
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
