from homekit import AccessoryServer
from homekit.model import CameraAccessory, ManagedRTPStreamService, MicrophoneService
from homekit.model.characteristics.rtp_stream.setup_endpoints import Address, IPVersion
from homekit.model.characteristics.rtp_stream.supported_audio_stream_configuration import \
    SupportedAudioStreamConfiguration, AudioCodecConfiguration, AudioCodecType, AudioCodecParameters, BitRate, \
    SampleRate
from homekit.model.characteristics.rtp_stream.supported_rtp_configuration import SupportedRTPConfiguration, \
    CameraSRTPCryptoSuite
from homekit.model.characteristics.rtp_stream.supported_video_stream_configuration import \
    SupportedVideoStreamConfiguration, VideoCodecConfiguration, VideoCodecParameters, H264Profile, H264Level, \
    VideoAttributes

import subprocess
import base64

if __name__ == '__main__':
    try:
        httpd = AccessoryServer('demoserver.json')

        accessory = CameraAccessory('Testkamera', 'wiomoc', 'Demoserver', '0001', '0.1')


        # accessory.set_get_image_snapshot_callback(
        #     lambda f: open('cam-preview.jpg', 'rb').read())

        class StreamHandler:
            def __init__(self, controller_address, srtp_params_video, **_):
                self.srtp_params_video = srtp_params_video
                self.controller_address = controller_address
                self.ffmpeg_process = None

            def on_start(self, attrs):
                self.ffmpeg_process = subprocess.Popen(
                    ['ffmpeg', '-re',
                     '-f', 'avfoundation',
                     '-r', '30.000030', '-i', '0:0', '-threads', '0',
                     '-vcodec', 'libx264', '-an', '-pix_fmt', 'yuv420p',
                     '-r', str(attrs.attributes.frame_rate),
                     '-f', 'rawvideo', '-tune', 'zerolatency', '-vf',
                     f'scale={attrs.attributes.width}:{attrs.attributes.height}',
                     '-b:v', '300k', '-bufsize', '300k',
                     '-payload_type', '99', '-ssrc', '32', '-f', 'rtp',
                     '-srtp_out_suite', 'AES_CM_128_HMAC_SHA1_80',
                     '-srtp_out_params', base64.b64encode(
                        self.srtp_params_video.master_key + self.srtp_params_video.master_salt).decode('ascii'),
                     f'srtp://{self.controller_address.ip_address}:{self.controller_address.video_rtp_port}'
                     f'?rtcpport={self.controller_address.video_rtp_port}&localrtcpport={self.controller_address.video_rtp_port}'
                     '&pkt_size=1378'
                     ])

            def on_end(self):
                if self.ffmpeg_process is not None:
                    self.ffmpeg_process.terminate()

            def get_ssrc(self):
                return (32, 32)

            def get_address(self):
                return Address(IPVersion.IPV4, httpd.data.ip, self.controller_address.video_rtp_port,
                               self.controller_address.audio_rtp_port)


        stream_service = ManagedRTPStreamService(
            StreamHandler,
            SupportedRTPConfiguration(
                [
                    CameraSRTPCryptoSuite.AES_CM_128_HMAC_SHA1_80,
                ]),
            SupportedVideoStreamConfiguration(
                VideoCodecConfiguration(
                    VideoCodecParameters(
                        [H264Profile.CONSTRAINED_BASELINE_PROFILE, H264Profile.MAIN_PROFILE, H264Profile.HIGH_PROFILE],
                        [H264Level.L_3_1, H264Level.L_3_2, H264Level.L_4]
                    ), [
                        VideoAttributes(1920, 1080, 30),
                        VideoAttributes(320, 240, 15),
                        VideoAttributes(1280, 960, 30),
                        VideoAttributes(1280, 720, 30),
                        VideoAttributes(1280, 768, 30),
                        VideoAttributes(640, 480, 30),
                        VideoAttributes(640, 360, 30)
                    ])),
            SupportedAudioStreamConfiguration([
                AudioCodecConfiguration(AudioCodecType.OPUS,
                                        AudioCodecParameters(1, BitRate.VARIABLE, SampleRate.KHZ_24)),
                AudioCodecConfiguration(AudioCodecType.AAC_ELD,
                                        AudioCodecParameters(1, BitRate.VARIABLE, SampleRate.KHZ_16))
            ], 0))
        accessory.services.append(stream_service)
        microphone_service = MicrophoneService()
        accessory.services.append(microphone_service)
        httpd.accessories.add_accessory(accessory)

        httpd.publish_device()
        print('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('unpublish device')
        httpd.unpublish_device()
