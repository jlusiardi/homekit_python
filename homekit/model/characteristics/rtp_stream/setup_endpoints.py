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
import tlv8

from homekit.model.characteristics import CharacteristicsTypes, CharacteristicFormats, CharacteristicPermissions, \
    AbstractCharacteristic
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import CameraSRTPCryptoSuite


class SetupEndpointsKeys(IntEnum):
    """
    Page 208 / Table 9-13
    """
    SESSION_ID = 1
    CONTROLLER_ADDRESS = 3
    SRTP_PARAMETERS_FOR_VIDEO = 4
    SRTP_PARAMETERS_FOR_AUDIO = 5


class IPVersion(IntEnum):
    """
    Page 208 / Table 9-14 values for key 'IP address version'
    """
    IPV4 = 0
    IPV6 = 1


class Address:
    """
    Page 208 / Table 9-14
    """

    def __init__(self, ip_address, video_rtp_port, audio_rtp_port, ip_version=IPVersion.IPV4):
        self.ip_version = ip_version
        self.ip_address = ip_address
        self.video_rtp_port = video_rtp_port
        self.audio_rtp_port = audio_rtp_port

    def to_entry_list(self):
        el = tlv8.EntryList([
            tlv8.Entry(ControllerAddressKeys.IP_ADDRESS_VERSION, self.ip_version),
            tlv8.Entry(ControllerAddressKeys.IP_ADDRESS, self.ip_address),
            tlv8.Entry(ControllerAddressKeys.VIDEO_RTP_PORT, self.video_rtp_port),
            tlv8.Entry(ControllerAddressKeys.AUDIO_RTP_PORT, self.audio_rtp_port),
        ])
        return el

    @staticmethod
    def parse(source_bytes):
        data_format = {
            ControllerAddressKeys.IP_ADDRESS_VERSION: IPVersion,
            ControllerAddressKeys.IP_ADDRESS: tlv8.DataType.STRING,
            ControllerAddressKeys.VIDEO_RTP_PORT: tlv8.DataType.INTEGER,
            ControllerAddressKeys.AUDIO_RTP_PORT: tlv8.DataType.INTEGER,
        }
        el = tlv8.decode(source_bytes, data_format)
        return el

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):
        ip_version = data.first_by_id(ControllerAddressKeys.IP_ADDRESS_VERSION).data
        ip_address = data.first_by_id(ControllerAddressKeys.IP_ADDRESS).data
        video_rtp_port = data.first_by_id(ControllerAddressKeys.VIDEO_RTP_PORT).data
        audio_rtp_port = data.first_by_id(ControllerAddressKeys.AUDIO_RTP_PORT).data
        return Address(ip_address, video_rtp_port, audio_rtp_port, ip_version)


class ControllerAddressKeys(IntEnum):
    """
    Page 208 / Table 9-14
    """
    IP_ADDRESS_VERSION = 1
    IP_ADDRESS = 2
    VIDEO_RTP_PORT = 3
    AUDIO_RTP_PORT = 4


class SrtpParameterKeys(IntEnum):
    """
    Page 209 / Table 9-15
    """
    SRTP_CRYPTO_SUITE = 1
    SRTP_MASTER_KEY = 2
    SRTP_MASTER_SALT = 3


class SRTPParameters:
    """
    page 209 / table 9-15
    """

    def __init__(self, crypto_suite, master_key=b'', master_salt=b''):
        self.crypto_suite = crypto_suite
        self.master_key = master_key
        self.master_salt = master_salt

    def to_entry_list(self):
        return tlv8.EntryList([
            tlv8.Entry(SrtpParameterKeys.SRTP_CRYPTO_SUITE, self.crypto_suite),
            tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_KEY, self.master_key),
            tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_SALT, self.master_salt)
        ])

    @staticmethod
    def parse(source_bytes):
        data_format = {
            SrtpParameterKeys.SRTP_CRYPTO_SUITE: CameraSRTPCryptoSuite,
            SrtpParameterKeys.SRTP_MASTER_KEY: tlv8.DataType.BYTES,
            SrtpParameterKeys.SRTP_MASTER_SALT: tlv8.DataType.BYTES,
        }
        el = tlv8.decode(source_bytes, data_format)
        return el

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):
        return SRTPParameters(
            data.first_by_id(SrtpParameterKeys.SRTP_CRYPTO_SUITE).data,
            data.first_by_id(SrtpParameterKeys.SRTP_MASTER_KEY).data,
            data.first_by_id(SrtpParameterKeys.SRTP_MASTER_SALT).data,
        )


class SetupEndpointsRequest:
    """
    Page 208 / Table 9-13
    """

    def __init__(self,
                 session_id,
                 controller_address: Address,
                 srtp_params_video: SRTPParameters,
                 srtp_params_audio: SRTPParameters):
        self.session_id = session_id
        self.controller_address = controller_address
        self.srtp_params_video = srtp_params_video
        self.srtp_params_audio = srtp_params_audio

    @staticmethod
    def from_entry_list(data: tlv8.EntryList):
        session_id = data.first_by_id(SetupEndpointsKeys.SESSION_ID).data

        el = Address.parse(data.first_by_id(SetupEndpointsKeys.CONTROLLER_ADDRESS).data)
        controller_address = Address.from_entry_list(el)

        el = SRTPParameters.parse(data.first_by_id(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO).data)
        srtp_params_video = SRTPParameters.from_entry_list(el)

        el = SRTPParameters.parse(data.first_by_id(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO).data)
        srtp_params_audio = SRTPParameters.from_entry_list(el)

        return SetupEndpointsRequest(session_id, controller_address, srtp_params_video, srtp_params_audio)


class EndpointStatus(IntEnum):
    """
    Page 210 / Table 9-16 Values for key status
    """
    SUCCESS = 0
    BUSY = 1
    ERROR = 2


class SetupEndpointsResponseKeys(IntEnum):
    """
    Page 208 / Table 9-13
    """
    SESSION_ID = 1
    STATUS = 2
    ACCESSORY_ADDRESS = 3
    SRTP_PARAMETERS_FOR_VIDEO = 4
    SRTP_PARAMETERS_FOR_AUDIO = 5
    VIDEO_RTP_SSRC = 6
    AUDIO_RTP_SSRC = 7


class SetupEndpointsResponse:
    """
    Page 210 / Table 9-16
    """

    def __init__(self,
                 id,
                 status,
                 accessory_address: Address = None,
                 srtp_params_video=None,
                 srtp_params_audio=None,
                 ssrc_video=None,
                 ssrc_audio=None):
        self.id = id
        self.status = status
        self.accessory_address = accessory_address
        self.srtp_params_video = srtp_params_video
        self.srtp_params_audio = srtp_params_audio
        self.ssrc_video = ssrc_video
        self.ssrc_audio = ssrc_audio

    def to_entry_list(self):
        el = tlv8.EntryList([
            tlv8.Entry(SetupEndpointsResponseKeys.SESSION_ID, self.id),
            tlv8.Entry(SetupEndpointsResponseKeys.STATUS, self.status),
        ])
        if self.accessory_address:
            el.append(tlv8.Entry(SetupEndpointsResponseKeys.ACCESSORY_ADDRESS, self.accessory_address.to_entry_list()))
        if self.srtp_params_video:
            el.append(tlv8.Entry(SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_VIDEO,
                                 self.srtp_params_video.to_entry_list()))
        if self.srtp_params_audio:
            el.append(tlv8.Entry(SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_VIDEO,
                                 self.srtp_params_audio.to_entry_list()))
        if self.ssrc_video:
            el.append(tlv8.Entry(SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_VIDEO, self.ssrc_video))
        if self.ssrc_audio:
            el.append(tlv8.Entry(SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_VIDEO, self.ssrc_audio))
        return el

    @staticmethod
    def parse(source_bytes):
        data_format = {
            SetupEndpointsResponseKeys.SESSION_ID: tlv8.DataType.BYTES,
            SetupEndpointsResponseKeys.STATUS: EndpointStatus,
            SetupEndpointsResponseKeys.ACCESSORY_ADDRESS: tlv8.DataType.BYTES,
            SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_VIDEO: tlv8.DataType.BYTES,
            SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_AUDIO: tlv8.DataType.BYTES,
            SetupEndpointsResponseKeys.VIDEO_RTP_SSRC: tlv8.DataType.BYTES,
            SetupEndpointsResponseKeys.AUDIO_RTP_SSRC: tlv8.DataType.BYTES,
        }
        el = tlv8.decode(source_bytes, data_format)
        entry = el.first_by_id(SetupEndpointsResponseKeys.ACCESSORY_ADDRESS)
        entry.data = Address.parse(entry.data)
        entry = el.first_by_id(SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_VIDEO)
        entry.data = SRTPParameters.parse(entry.data)
        entry = el.first_by_id(SetupEndpointsResponseKeys.SRTP_PARAMETERS_FOR_AUDIO)
        entry.data = SRTPParameters.parse(entry.data)
        return el


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
