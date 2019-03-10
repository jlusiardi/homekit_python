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

# flake8 is suppressed here because in this file it should just be checked if the packages can be imported.
try:
    import gatt  # noqa: F401
    import dbus  # noqa: F401
    BLE_TRANSPORT_SUPPORTED = True
except ImportError:
    BLE_TRANSPORT_SUPPORTED = False

try:
    import zeroconf  # noqa: F401
    IP_TRANSPORT_SUPPORTED = True
except ImportError:
    IP_TRANSPORT_SUPPORTED = False
