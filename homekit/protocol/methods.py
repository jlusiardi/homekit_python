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


class Methods(IntEnum):
    # Methods (see table 4-4 page 60)
    PairSetup = 1
    PairVerify = 2
    AddPairing = 3
    RemovePairing = 4
    ListPairings = 5

    # Table 6-27 page 116
    kTLVMethod_Resume = 7
