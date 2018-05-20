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

import homekit.feature_flags
import homekit.model.categories
import homekit.model.services
import homekit.model.characteristics
import homekit.statuscodes
import homekit.zeroconf_
from homekit.chacha20poly1305 import chacha20_aead_encrypt, chacha20_aead_decrypt
from homekit.protocol import perform_pair_setup, get_session_keys
from homekit.secure_http import SecureHttp
from homekit.server import HomeKitServer
from homekit.srp import SrpClient
from homekit.tlv import TLV
from homekit.tools import load_pairing, save_pairing, create_session
from homekit.http_client import HomeKitHTTPConnection

# Init lookup objects
FeatureFlags = homekit.feature_flags.FeatureFlags
Categories = homekit.model.categories.Categories
HapStatusCodes = homekit.statuscodes.HapStatusCodes
HttpStatusCodes = homekit.statuscodes.HttpStatusCodes
HttpContentTypes = homekit.statuscodes._HttpContentTypes
CharacteristicsTypes = homekit.model.characteristics.CharacteristicsTypes
ServicesTypes = homekit.model.services.ServicesTypes

discover_homekit_devices = homekit.zeroconf_.discover_homekit_devices
find_device_ip_and_port = homekit.zeroconf_.find_device_ip_and_port
