# Copyright 2020 Joachim Lusiardi
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
from enum import IntEnum


class TlvTypes(IntEnum):
    # TLV Values (see table 4-6 page 61)
    Method = 0
    Identifier = 1
    Salt = 2
    PublicKey = 3
    Proof = 4
    EncryptedData = 5
    State = 6
    Error = 7
    RetryDelay = 8
    Certificate = 9
    Signature = 10
    Permissions = 11  # 0x00 => reg. user, 0x01 => admin
    Permission_RegularUser = 0  # bytearray(b'\x00')
    Permission_AdminUser = 1  # bytearray(b'\x01')
    FragmentData = 12
    FragmentLast = 13
    SessionID = 0x0e  # Table 6-27 page 116
