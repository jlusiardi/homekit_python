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

from homekit.model.characteristics import CharacteristicsTypes, CharacteristicPermissions, \
    AbstractTlv8Characteristic, AbstractTlv8CharacteristicValue
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import CameraSRTPCryptoSuite


class SetupEndpointsKeys(IntEnum):
    """
    Page 208 / Table 9-13
    Page 210 / Table 9-16
    """
    SESSION_ID = 1
    STATUS = 2
    ADDRESS = 3
    SRTP_PARAMETERS_FOR_VIDEO = 4
    SRTP_PARAMETERS_FOR_AUDIO = 5
    VIDEO_RTP_SSRC = 6
    AUDIO_RTP_SSRC = 7


class IPVersion(IntEnum):
    """
    Page 208 / Table 9-14 values for key 'IP address version'
    """
    IPV4 = 0
    IPV6 = 1


class ControllerAddressKeys(IntEnum):
    """
    Page 208 / Table 9-14
    """
    IP_ADDRESS_VERSION = 1
    IP_ADDRESS = 2
    VIDEO_RTP_PORT = 3
    AUDIO_RTP_PORT = 4


class Address(AbstractTlv8CharacteristicValue):
    """
    Page 208 / Table 9-14
    """

    def __init__(self,
                 ip_address: str,
                 video_rtp_port: int,
                 audio_rtp_port: int,
                 ip_version: IPVersion = IPVersion.IPV4):
        self.ip_version = ip_version
        self.ip_address = ip_address
        self.video_rtp_port = video_rtp_port
        self.audio_rtp_port = audio_rtp_port

    def to_bytes(self) -> bytes:
        el = tlv8.EntryList([
            tlv8.Entry(ControllerAddressKeys.IP_ADDRESS_VERSION, self.ip_version),
            tlv8.Entry(ControllerAddressKeys.IP_ADDRESS, self.ip_address),
            tlv8.Entry(ControllerAddressKeys.VIDEO_RTP_PORT, self.video_rtp_port),
            tlv8.Entry(ControllerAddressKeys.AUDIO_RTP_PORT, self.audio_rtp_port),
        ])
        return el.encode()

    @staticmethod
    def from_bytes(data: bytes):
        data_format = {
            ControllerAddressKeys.IP_ADDRESS_VERSION: IPVersion,
            ControllerAddressKeys.IP_ADDRESS: tlv8.DataType.STRING,
            ControllerAddressKeys.VIDEO_RTP_PORT: tlv8.DataType.INTEGER,
            ControllerAddressKeys.AUDIO_RTP_PORT: tlv8.DataType.INTEGER,
        }
        el = tlv8.decode(data, data_format)
        ip_version = el.first_by_id(ControllerAddressKeys.IP_ADDRESS_VERSION).data
        ip_address = el.first_by_id(ControllerAddressKeys.IP_ADDRESS).data
        video_rtp_port = el.first_by_id(ControllerAddressKeys.VIDEO_RTP_PORT).data
        audio_rtp_port = el.first_by_id(ControllerAddressKeys.AUDIO_RTP_PORT).data
        return Address(ip_address, video_rtp_port, audio_rtp_port, ip_version)


class SrtpParameterKeys(IntEnum):
    """
    Page 209 / Table 9-15
    """
    SRTP_CRYPTO_SUITE = 1
    SRTP_MASTER_KEY = 2
    SRTP_MASTER_SALT = 3


class SRTPParameters(AbstractTlv8CharacteristicValue):
    """
    page 209 / table 9-15
    """

    def __init__(self,
                 crypto_suite: CameraSRTPCryptoSuite,
                 master_key: bytes = b'',
                 master_salt: bytes = b''):
        self.crypto_suite = crypto_suite
        self.master_key = master_key
        self.master_salt = master_salt

    def to_bytes(self) -> bytes:
        return tlv8.EntryList([
            tlv8.Entry(SrtpParameterKeys.SRTP_CRYPTO_SUITE, self.crypto_suite),
            tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_KEY, self.master_key),
            tlv8.Entry(SrtpParameterKeys.SRTP_MASTER_SALT, self.master_salt)
        ]).encode()

    @staticmethod
    def from_bytes(data: bytes):
        data_format = {
            SrtpParameterKeys.SRTP_CRYPTO_SUITE: CameraSRTPCryptoSuite,
            SrtpParameterKeys.SRTP_MASTER_KEY: tlv8.DataType.BYTES,
            SrtpParameterKeys.SRTP_MASTER_SALT: tlv8.DataType.BYTES,
        }
        el = tlv8.decode(data, data_format)
        return SRTPParameters(
            el.first_by_id(SrtpParameterKeys.SRTP_CRYPTO_SUITE).data,
            el.first_by_id(SrtpParameterKeys.SRTP_MASTER_KEY).data,
            el.first_by_id(SrtpParameterKeys.SRTP_MASTER_SALT).data,
        )


class SetupEndpointsRequest(AbstractTlv8CharacteristicValue):
    """
    Page 208 / Table 9-13
    """

    def __init__(self,
                 session_id: bytes,
                 controller_address: Address,
                 srtp_params_video: SRTPParameters,
                 srtp_params_audio: SRTPParameters):
        self.session_id = session_id
        self.controller_address = controller_address
        self.srtp_params_video = srtp_params_video
        self.srtp_params_audio = srtp_params_audio

    def to_bytes(self) -> bytes:
        return tlv8.EntryList([
            tlv8.Entry(SetupEndpointsKeys.SESSION_ID, self.session_id),
            tlv8.Entry(SetupEndpointsKeys.ADDRESS, self.controller_address.to_bytes()),
            tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, self.srtp_params_video.to_bytes()),
            tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, self.srtp_params_audio.to_bytes()),
        ]).encode()

    @staticmethod
    def from_bytes(data: bytes):
        el = tlv8.decode(data, {
            SetupEndpointsKeys.SESSION_ID: tlv8.DataType.BYTES,
            SetupEndpointsKeys.ADDRESS: tlv8.DataType.BYTES,
            SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO: tlv8.DataType.BYTES,
            SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO: tlv8.DataType.BYTES,
        })
        session_id = el.first_by_id(SetupEndpointsKeys.SESSION_ID).data

        controller_address = Address.from_bytes(el.first_by_id(SetupEndpointsKeys.ADDRESS).data)

        srtp_params_video = SRTPParameters.from_bytes(el.first_by_id(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO).data)

        srtp_params_audio = SRTPParameters.from_bytes(el.first_by_id(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO).data)

        return SetupEndpointsRequest(session_id, controller_address, srtp_params_video, srtp_params_audio)


class EndpointStatus(IntEnum):
    """
    Page 210 / Table 9-16 Values for key status
    """
    SUCCESS = 0
    BUSY = 1
    ERROR = 2


class SetupEndpointsResponse(AbstractTlv8CharacteristicValue):
    """
    Page 210 / Table 9-16
    """

    def __init__(self,
                 id,
                 status: EndpointStatus,
                 accessory_address: Address = None,
                 srtp_params_video: SRTPParameters = None,
                 srtp_params_audio: SRTPParameters = None,
                 ssrc_video: bytes = None,
                 ssrc_audio: bytes = None):
        self.id = id
        self.status = status
        self.accessory_address = accessory_address
        self.srtp_params_video = srtp_params_video
        self.srtp_params_audio = srtp_params_audio
        self.ssrc_video = ssrc_video
        self.ssrc_audio = ssrc_audio

    def to_bytes(self) -> bytes:
        el = tlv8.EntryList([
            tlv8.Entry(SetupEndpointsKeys.SESSION_ID, self.id),
            tlv8.Entry(SetupEndpointsKeys.STATUS, self.status),
        ])
        if self.accessory_address:
            el.append(tlv8.Entry(SetupEndpointsKeys.ADDRESS, self.accessory_address.to_bytes()))
        if self.srtp_params_video:
            el.append(tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO,
                                 self.srtp_params_video.to_bytes()))
        if self.srtp_params_audio:
            el.append(tlv8.Entry(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO,
                                 self.srtp_params_audio.to_bytes()))
        if self.ssrc_video:
            el.append(tlv8.Entry(SetupEndpointsKeys.VIDEO_RTP_SSRC, self.ssrc_video))
        if self.ssrc_audio:
            el.append(tlv8.Entry(SetupEndpointsKeys.AUDIO_RTP_SSRC, self.ssrc_audio))
        return el.encode()

    @staticmethod
    def from_bytes(data: bytes):
        data_format = {
            SetupEndpointsKeys.SESSION_ID: tlv8.DataType.BYTES,
            SetupEndpointsKeys.STATUS: EndpointStatus,
            SetupEndpointsKeys.ADDRESS: tlv8.DataType.BYTES,
            SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO: tlv8.DataType.BYTES,
            SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO: tlv8.DataType.BYTES,
            SetupEndpointsKeys.VIDEO_RTP_SSRC: tlv8.DataType.BYTES,
            SetupEndpointsKeys.AUDIO_RTP_SSRC: tlv8.DataType.BYTES,
        }
        el = tlv8.decode(data, data_format)
        session_id = el.first_by_id(SetupEndpointsKeys.SESSION_ID).data
        status = el.first_by_id(SetupEndpointsKeys.STATUS).data
        address = Address.from_bytes(el.first_by_id(SetupEndpointsKeys.ADDRESS).data)
        srtp_params_video = SRTPParameters.from_bytes(
            el.first_by_id(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO).data)
        srtp_params_audio = SRTPParameters.from_bytes(
            el.first_by_id(SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO).data)
        ssrc_video = el.first_by_id(SetupEndpointsKeys.VIDEO_RTP_SSRC).data
        ssrc_audio = el.first_by_id(SetupEndpointsKeys.AUDIO_RTP_SSRC).data
        return SetupEndpointsResponse(session_id, status, address, srtp_params_video, srtp_params_audio, ssrc_video,
                                      ssrc_audio)


class SetupEndpointsCharacteristic(AbstractTlv8Characteristic):
    """
    Defined on page 219
    """

    def __init__(self, iid, value):
        AbstractTlv8Characteristic.__init__(self, iid, value, CharacteristicsTypes.SETUP_ENDPOINTS)
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
