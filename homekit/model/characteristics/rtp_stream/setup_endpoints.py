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

from enum import IntEnum
from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import CameraSRTPCryptoSuite
from homekit.protocol.tlv import TLVItem


class IPVersion(IntEnum):
    IPV4 = 0
    IPV6 = 1


class Address:
    ip_version = TLVItem(1, IPVersion)
    ip_address = TLVItem(2, str)
    video_rtp_port = TLVItem(3, int)
    audio_rtp_port = TLVItem(4, int)

    def __init__(self, ip_version, ip_address, video_rtp_port, audio_rtp_port):
        self.ip_version = ip_version
        self.ip_address = ip_address
        self.video_rtp_port = video_rtp_port
        self.audio_rtp_port = audio_rtp_port


class SRTPParameters:
    crypto_suite = TLVItem(1, CameraSRTPCryptoSuite)
    master_key = TLVItem(2, bytes)
    master_salt = TLVItem(3, bytes)


class SetupEndpointsRequest:
    id = TLVItem(1, bytes)
    controller_address = TLVItem(3, Address)
    srtp_params_video = TLVItem(4, SRTPParameters)
    srtp_params_audio = TLVItem(5, SRTPParameters)


class EndpointStatus:
    SUCCESS = 0
    BUSY = 1
    ERROR = 2


class SetupEndpointsResponse:
    id = TLVItem(1, bytes)
    status = TLVItem(2, EndpointStatus)
    accessory_address = TLVItem(3, Address)
    srtp_params_video = TLVItem(4, SRTPParameters)
    srtp_params_audio = TLVItem(5, SRTPParameters)
    ssrc_video = TLVItem(6, int)
    ssrc_audio = TLVItem(7, int)

    def __init__(self, id, status, accessory_address=None, srtp_params_video=None, srtp_params_audio=None,
                 ssrc_video=None, ssrc_audio=None):
        self.id = id
        self.status = status
        self.accessory_address = accessory_address
        self.srtp_params_video = srtp_params_video
        self.srtp_params_audio = srtp_params_audio
        self.ssrc_video = ssrc_video
        self.ssrc_audio = ssrc_audio


class SetupEndpointsCharacteristic(AbstractCharacteristic):
    """
    Defined on page 219
    """

    def __init__(self, iid):
        AbstractCharacteristic.__init__(self, iid, CharacteristicsTypes.SETUP_ENDPOINTS,
                                        CharacteristicFormats.tlv8, SetupEndpointsRequest)
        self.perms = [CharacteristicPermissions.paired_read, CharacteristicPermissions.paired_write]
        self.description = 'setup camera endpoint'


class SetupEndpointsCharacteristicMixin(object):

    def __init__(self, iid):
        self._setupEndpointsCharacteristic = SetupEndpointsCharacteristic(iid)
        self.characteristics.append(self._setupEndpointsCharacteristic)

    def set_setup_endpoints_set_callback(self, callback):
        self._setupEndpointsCharacteristic.set_set_value_callback(callback)

    def set_setup_endpoints_get_callback(self, callback):
        self._setupEndpointsCharacteristic.set_get_value_callback(callback)
