#
# Copyright 2019 Christoph Walcher
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
from uuid import UUID
import logging

from homekit.model import get_id
from homekit.model.characteristics.rtp_stream import SetupEndpointsCharacteristicMixin, \
    StreamingStatusCharacteristicMixin, SelectedRTPStreamConfigurationCharacteristicMixin, \
    SupportedVideoStreamConfigurationCharacteristic, SupportedAudioStreamConfigurationCharacteristic, \
    SupportedRTPConfigurationCharacteristic
from homekit.model.characteristics.rtp_stream.selected_rtp_stream_configuration import SelectedRTPStreamConfiguration, \
    Command
from homekit.model.characteristics.rtp_stream.setup_endpoints import SetupEndpointsRequest, EndpointStatus, \
    SetupEndpointsResponse
from homekit.model.characteristics.rtp_stream.streaming_status import StreamingStatus, StreamingStatusEnum
from homekit.model.services import ServicesTypes, AbstractService


class RTPStreamService(AbstractService, StreamingStatusCharacteristicMixin,
                       SetupEndpointsCharacteristicMixin,
                       SelectedRTPStreamConfigurationCharacteristicMixin):
    """
    Defined on page 137; RTP stream management service used to negotiate (camera) live streaming
    """

    def __init__(self, supported_rtp_configuration, supported_video_stream_config, supported_audio_stream_config):
        AbstractService.__init__(self, ServicesTypes.get_uuid('public.hap.service.camera-rtp-stream-management'),
                                 get_id())
        StreamingStatusCharacteristicMixin.__init__(self, get_id())
        SetupEndpointsCharacteristicMixin.__init__(self, get_id())
        SelectedRTPStreamConfigurationCharacteristicMixin.__init__(self, get_id())

        self.append_characteristic(
            SupportedRTPConfigurationCharacteristic(get_id(), supported_rtp_configuration))
        self.append_characteristic(
            SupportedVideoStreamConfigurationCharacteristic(get_id(), supported_video_stream_config))
        self.append_characteristic(
            SupportedAudioStreamConfigurationCharacteristic(get_id(), supported_audio_stream_config))


class Stream:
    def __init__(self, uuid, status, srtp_params_video, srtp_params_audio, handler, address):
        self.uuid = uuid
        self.status = status
        self.srtp_params_video = srtp_params_video
        self.srtp_params_audio = srtp_params_audio
        self.handler = handler
        self.address = address


class ManagedRTPStreamService(RTPStreamService):
    def __init__(self, stream_handler_factory, supported_rtp_configuration, supported_video_stream_config,
                 supported_audio_stream_config):
        super().__init__(supported_rtp_configuration, supported_video_stream_config,
                         supported_audio_stream_config)
        self.set_selected_rtp_stream_configuration_set_callback(self.select_rtp_stream_configuration)
        self.set_selected_rtp_stream_configuration_get_callback(self.get_rtp_stream_configuration)
        self.set_setup_endpoints_set_callback(self.setup_endpoints_req)
        self.set_setup_endpoints_get_callback(self.setup_endpoints_res)
        self.set_streaming_status_get_callback(lambda: StreamingStatus(self.get_status()))
        self.stream_handler_factory = stream_handler_factory
        self.streams = {}
        self.last_added = None
        self.last_rtp_stream_config = None

    def setup_endpoints_req(self, val: SetupEndpointsRequest):
        logging.error('setup_endpoints_req: %s', val)
        uuid = UUID(bytes=bytes(val.id))
        stream_handler = self.stream_handler_factory(uuid=uuid,
                                                     controller_address=val.controller_address,
                                                     srtp_params_video=val.srtp_params_video,
                                                     srtp_params_audio=val.srtp_params_audio)
        stream = Stream(uuid, EndpointStatus.SUCCESS, srtp_params_video=val.srtp_params_video,
                        srtp_params_audio=val.srtp_params_audio, handler=stream_handler, address=val.controller_address)
        self.streams[uuid] = stream
        self.last_added = stream

    def setup_endpoints_res(self):
        logging.error('setup_endpoints_res')
        if self.last_added is not None:
            ssrc = self.last_added.handler.get_ssrc()
            address = self.last_added.handler.get_address()
            result = SetupEndpointsResponse(id=self.last_added.uuid.bytes,
                                            status=EndpointStatus.SUCCESS,
                                            accessory_address=address,
                                            srtp_params_video=self.last_added.srtp_params_video,
                                            srtp_params_audio=self.last_added.srtp_params_audio,
                                            ssrc_video=ssrc[0],
                                            ssrc_audio=ssrc[1])
        else:
            result = SetupEndpointsResponse(id=self.last_added.uuid.bytes, status=EndpointStatus.ERROR)
        logging.error('setup_endpoints_res: %s', result)
        return result

    def select_rtp_stream_configuration(self, rtp_stream_config: SelectedRTPStreamConfiguration):
        logging.error('select_rtp_stream_configuration: %s', rtp_stream_config)
        if rtp_stream_config is not None:
            uuid = UUID(bytes=bytes(rtp_stream_config.session_control.id))
            stream = self.streams[uuid]
            self.last_rtp_stream_config = rtp_stream_config
            cmd = rtp_stream_config.session_control.command
            if cmd == Command.START:
                stream.handler.on_start(rtp_stream_config.selected_video_parameters)
            elif cmd == Command.END:
                stream.handler.on_end()

    def get_rtp_stream_configuration(self):
        logging.error('get_rtp_stream_configuration')
        return self.last_rtp_stream_config

    def get_status(self):
        return StreamingStatusEnum.AVAILABLE
