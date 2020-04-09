# Information about `debug_proxy`

The `debug_proxy` command can be used to sit between an IP Accessory and a 
controller (e.g. iPhone). The accessory must be paired already so we cannot 
debug issues with pairing at the moment.

## cli parameter

```text
usage: debug_proxy.py [-h] -c CLIENT_DATA -a ALIAS -s SERVER_DATA [-C CODE]
                      [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

HomeKit debug proxy

optional arguments:
  -h, --help            show this help message and exit
  -c CLIENT_DATA, --client-data CLIENT_DATA
                        JSON file with the pairing data for the accessory
  -a ALIAS, --alias ALIAS
                        alias for the pairing
  -s SERVER_DATA, --server-data SERVER_DATA
                        JSON file with the accessory data to the controller
  -C CODE, --code CODE  Reference to a python module with filter functions
  --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the log level of the script
```

## basic functionality

For basic usage of the `debug_proxy`, proceed as follows:
  1) create a pairing with the accessory under test and store it in `pairingdata.json` 
     under alias `target` (The names are free to choose)
  2) create `server.json` as described under creating [HomeKit Accessory](#homekit-accessory). 
     **Important**: the `category` here must match the category of the proxied accessory
  3) run the `debug_proxy` like `python3 -m homekit.debug_proxy --client-data pairingdata.json --alias target --server-data server.json`
  4) inspect the log and analyse the data. Right to the beginning, the list of proxied 
     characteristics is logged and the get and set value calls come later:
```text
2020-03-15 18:34:09,725 debug_proxy.py:0199 INFO %<------ creating proxy ------
2020-03-15 18:34:09,725 debug_proxy.py:0204 INFO accessory with aid=1
2020-03-15 18:34:09,725 debug_proxy.py:0212 INFO   1.1: >accessory-information< (0000003E-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,725 debug_proxy.py:0225 INFO     1.5: Logi Circle >name< (00000023-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,725 debug_proxy.py:0225 INFO     1.2: None >identify< (00000014-0000-1000-8000-0026BB765291) [pw] bool
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.3: Logitech >manufacturer< (00000020-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.4: V-R0008 >model< (00000021-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.6: 1933CDC04478 >serial-number< (00000030-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.7: 5.6.49 >firmware.revision< (00000052-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.9: >camera-rtp-stream-management< (00000110-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.10: AQEC >streaming-status< (00000120-0000-1000-8000-0026BB765291) [pr,ev] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.11: AREBAQACDAEBAQIBAgMBAAQBAA== >supported-video-stream-configuration< (00000114-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.12: AQ8BAgMAAgkBAQECAQADAQECAQA= >supported-audio-configuration< (00000115-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.13: AgEA >supported-rtp-configuration< (00000116-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.14:  >setup-endpoints< (00000118-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.15:  >selected-rtp-stream-configuration< (00000117-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.16: >camera-rtp-stream-management< (00000110-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.17: AQEA >streaming-status< (00000120-0000-1000-8000-0026BB765291) [pr,ev] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.18: AVoBAQACDAEBAQIBAgMBAAQBAAMLAQIABQIC0AIDAR7/AAMLAQKAAgICaAEDAR7/AAMLAQIABAICAAMDAR7/AAMLAQKAAgIC4AEDAR7/AAMLAQJAAQIC8AADAR4= >supported-video-stream-configuration< (00000114-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.19: AQ8BAgMAAgkBAQECAQADAQECAQA= >supported-audio-configuration< (00000115-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.20: AgEA >supported-rtp-configuration< (00000116-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.21: ARA+sNO7kUtMIYyHgEWPvo4KAgEAAxwBAQACDzE5Mi4xNjguMTc4LjIxMgMCKfcEAq7iBCUBAQACEB1niC5AAAcwwBb7IO4e7oYDDmQylh7GJdhOjZ5Yrq67BSUBAQACEBcDMU3e6vrRmHl0Ze2NrrADDuPZEzuug4WjLKreG4PUBgQEV+ZuBwQzoa0p >setup-endpoints< (00000118-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.22:  >selected-rtp-stream-configuration< (00000117-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.34: >microphone< (00000112-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.35: False >mute< (0000011A-0000-1000-8000-0026BB765291) [pr,pw,ev] bool
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.37: >speaker< (00000113-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.38: False >mute< (0000011A-0000-1000-8000-0026BB765291) [pr,pw,ev] bool
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.40: >motion< (00000085-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.41: False >motion-detected< (00000022-0000-1000-8000-0026BB765291) [pr,ev] bool
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.42: Logi Circle Motion Detector >name< (00000023-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.400: >Unknown Service: 5C20E6E7-0B8B-43C4-9C5F-CA0DE8A7BCD2< (5C20E6E7-0B8B-43C4-9C5F-CA0DE8A7BCD2)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.401: AQECAgEA >Unknown Characteristic 30B32518-5C01-4470-9C9F-7AEB89E93419< (30B32518-5C01-4470-9C9F-7AEB89E93419) [pr,ev] tlv8
2020-03-15 18:34:09,727 debug_proxy.py:0225 INFO     1.402: EQYAAAAAAAA= >Unknown Characteristic F1E5CE1A-2185-4798-BDF4-86A6557CBA54< (F1E5CE1A-2185-4798-BDF4-86A6557CBA54) [pr] tlv8
2020-03-15 18:34:09,727 debug_proxy.py:0225 INFO     1.403: None >Unknown Characteristic B45787D2-EE61-471B-9213-AEDBFC67186D< (B45787D2-EE61-471B-9213-AEDBFC67186D) [pw] tlv8
2020-03-15 18:34:09,727 debug_proxy.py:0238 INFO %<------ finished creating proxy ------

...

020-03-15 18:37:04,292 accessoryserver.py:1227 INFO "GET /characteristics?id=1.20,1.18,1.19 HTTP/1.1" 207 -
2020-03-15 18:37:04,437 debug_proxy.py:0088 INFO loading module setup_endpoints for type 00000118-0000-1000-8000-0026BB765291
2020-03-15 18:37:04,440 debug_proxy.py:0117 INFO write value to 1.21 (type 00000118-0000-1000-8000-0026BB765291 / setup-endpoints): 
[
  <SetupEndpointsKeys.SESSION_ID, b'n\x17\x8dh\xed\x90M8\x9d\xb7\\\x9b\x19`\x0bt'>,
  <SetupEndpointsKeys.ADDRESS, [
    <ControllerAddressKeys.IP_ADDRESS_VERSION, IPVersionValues.IPV4>,
    <ControllerAddressKeys.IP_ADDRESS, 192.168.178.222>,
    <ControllerAddressKeys.VIDEO_RTP_PORT, 58833>,
    <ControllerAddressKeys.AUDIO_RTP_PORT, 54612>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, [
    <SrtpParameterKeys.SRTP_MASTER_KEY, b'\x88\x81\xa6\xdd=\xe0\xd4,\x11\x89\x96\x89\xd06\xd1\xf7'>,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b's\xd4\x17\xbeJ\xee\xcf\xde\x170\xcd\x98qk'>,
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, [
    <SrtpParameterKeys.SRTP_MASTER_KEY, b"I\x8c\xb5\xf5up'w\xa8\x0b\x9b\xe8\th|8">,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b'Yg\x85z\xaa&\x809\xc2\x9d\x05`\xe6\xaf'>,
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
  ]>,
]
2020-03-15 18:37:04,441 accessoryserver.py:1227 INFO "PUT /characteristics HTTP/1.1" 204 -
2020-03-15 18:37:04,485 debug_proxy.py:0097 INFO got decoder for 00000118-0000-1000-8000-0026BB765291 from cache
2020-03-15 18:37:04,485 debug_proxy.py:0117 INFO get value from 1.21 (type 00000118-0000-1000-8000-0026BB765291 / setup-endpoints): 
[
  <SetupEndpointsKeys.SESSION_ID, b'n\x17\x8dh\xed\x90M8\x9d\xb7\\\x9b\x19`\x0bt'>,
  <SetupEndpointsKeys.STATUS, EndpointStatusValues.SUCCESS>,
  <SetupEndpointsKeys.ADDRESS, [
    <ControllerAddressKeys.IP_ADDRESS_VERSION, IPVersionValues.IPV4>,
    <ControllerAddressKeys.IP_ADDRESS, 192.168.178.212>,
    <ControllerAddressKeys.VIDEO_RTP_PORT, 58833>,
    <ControllerAddressKeys.AUDIO_RTP_PORT, 54612>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, [
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
    <SrtpParameterKeys.SRTP_MASTER_KEY, b'\x14\xfc\xa9\x12\x03\x89\x19\xfdcMC\xd4hI\xd6T'>,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b'\x97\x95\xd9\xc2#\x84\xfd\xa6\x83\xba\xf2I\xcf\xed'>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, [
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
    <SrtpParameterKeys.SRTP_MASTER_KEY, b'h\xc7\xf6\x8f\x8d\xb9\xc1[~\xdc\x88\x18X\xd78]'>,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b'\xb0\x8f\xbd\x95)\x9b\xdd\x97\xc0\xe1\x14JX4'>,
  ]>,
  <SetupEndpointsKeys.VIDEO_RTP_SSRC, b'&M\xd0w'>,
  <SetupEndpointsKeys.AUDIO_RTP_SSRC, b'\xa7ik\x07'>,
]
2020-03-15 18:37:04,485 accessoryserver.py:1227 INFO "GET /characteristics?id=1.21 HTTP/1.1" 200 -
2020-03-15 18:37:06,118 debug_proxy.py:0088 INFO loading module selected_rtp_stream_configuration for type 00000117-0000-1000-8000-0026BB765291
```

## filter functions

The `debug_proxy` can be started with the parameter `--code`. This offers the ability to change
the value that are to be written do the accessory behind the proxy or the value that was read and
is to be returned to the controller.

Sequence diagram for a `set_filter`:
![Set filter functions](./set_filter_functions.png)

Sequence diagram for a `get_filter`:
![Get filter functions](./get_filter_functions.png)

### How to define a filter function

First of all, important the 2 decorators and data structures and clean them:
```python
from homekit.debug_proxy import set_filters, set_filter, get_filters, get_filter

set_filters.clear()
get_filters.clear()
```

Consider this as a header for every module defining a filter. Now, define filter functions by
using the decorators `@set_filter(accessory_id, characteristic_id)` and
`@get_filter(accessory_id, characteristic_id)`. After that, each write/read operation to a
filtered characteristic will trigger the filter function.

### Example for a file defining filter functions:

 * `rename`: a get filter function to rename the camera from the example above to `mitm`
 * `mic_mute`: prevents the microphone from being unmuted
 
```python
from homekit.debug_proxy import set_filters, set_filter, get_filters, get_filter

set_filters.clear()
get_filters.clear()


@get_filter(1, 5)
def rename(val):
    return 'mitm'


@set_filter(1, 35)
def mic_mute(val):
    return True
```

