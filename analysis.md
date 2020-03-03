# iPhone to democameraserver

## read from status

    reply: b'\x01\x01\x00'
            01 01           Status
                00              Available

## write to setup endpoint

    request: b'\x01\x10r\x18P\xa9\xc7vE"\xb8\x1e\x8d>\x05\\4-\x03\x1c\x01\x01\x00\x02\x0f192.168.178.237\x03\x02\xec\xd6\x04\x02\x9b\xd4\x04%\x02\x10\xa3\xc6\xa9N\x02Gii\x1a<V]%\xaa\x0e"\x03\x0e\x87T\xee|\xecD; \\\xf9\x02\xfc\xd1M\x01\x01\x00\x05%\x02\x10\xd4\xfd\xc9X\xa5\xf1\x87`-\xfd@\xb2XI\xb7\x8b\x03\x0e\xbf\xfb\xc7\xb9\xdc\x0fUU\xb1\xa4y!\x80~\x01\x01\x00'
            01 1a           Session ID
                721850a9c7764522b81e8d3e055c342d
            03 1c           Controller Address  (Page 208 / Table 9-14)
                01 01           IP address version
                    00              IPv4
                02 0f           IP Address
                   3139322e3136382e3137382e323337
                03 02           Video RTP port
                    ecd6
                04 02           Audio RTP port
                    9bd4
            04 25           SRTP Parameters for Video (Page 209 / Table 9-15)
                02 10           SRTP Master Key
                   a3c6a94e024769691a3c565d25aa0e22
                03 0e           SRTP Master Salt
                    8754ee7cec443b205cf902fcd14d
                01 01           SRTP Crypto Suite
                    00              AES_CM_128_HMAC_SHA1_80
            05 25           SRTP Parameters for Audio (Page 209 / Table 9-15)
                02 10           SRTP Master Key
                    d4fdc958a5f187602dfd40b25849b78b
                03 0e           SRTP Master Salt
                    bffbc7b9dc0f5555b1a47921807e
                01 01           SRTP Crypto Suite
                    00              AES_CM_128_HMAC_SHA1_80

## read from setup endpoint

    response: b'\x01\x10r\x18P\xa9\xc7vE"\xb8\x1e\x8d>\x05\\4-\x02\x01\x00\x03\x1b\x01\x01\x00\x02\x0e192.168.178.32\x03\x02\xec\xd6\x04\x02\x9b\xd4\x04%\x01\x01\x00\x02\x10\xa3\xc6\xa9N\x02Gii\x1a<V]%\xaa\x0e"\x03\x0e\x87T\xee|\xecD; \\\xf9\x02\xfc\xd1M\x05%\x01\x01\x00\x02\x10\xd4\xfd\xc9X\xa5\xf1\x87`-\xfd@\xb2XI\xb7\x8b\x03\x0e\xbf\xfb\xc7\xb9\xdc\x0fUU\xb1\xa4y!\x80~\x06\x01 \x07\x01 '
            01 10           Session Identifier
                721850a9c7764522b81e8d3e055c342d
            02 01           Status
                00              Success
            03 1b           Accessory Address (Page 208 / Table 9-14)
                01 01           IP address version
                    00              IPv4
                02 0e           IP Address
                    3139322e3136382e3137382e3332
                03 02           Video RTP port
                    ecd6
                04 02           Audio RTP port
                    9bd4
            04 25           SRTP Parameters for Video (Page 209 / Table 9-15)
                01 01           SRTP Crypto Suite
                    00              AES_CM_128_HMAC_SHA1_80
                02 10           SRTP Master Key
                    a3c6a94e024769691a3c565d25aa0e22
                03 0e           SRTP Master Salt
                    8754ee7cec443b205cf902fcd14d
            05 25           SRTP Parameters for Audio (Page 209 / Table 9-15)
                01 01           SRTP Crypto Suite
                    00              AES_CM_128_HMAC_SHA1_80
                02 10           SRTP Master Key
                    d4fdc958a5f187602dfd40b25849b78b
                03 0e           SRTP Master Salt
                    bffbc7b9dc0f5555b1a47921807e
            06 01           SynchronizationSource for Video
                20      
            07 01           SynchronizationSource for Audio
                20          

## write to selected stream configuration (start of stream)

    request: b'\x01\x15\x02\x01\x01\x01\x10r\x18P\xa9\xc7vE"\xb8\x1e\x8d>\x05\\4-\x024\x01\x01\x00\x02\t\x01\x01\x02\x02\x01\x02\x03\x01\x00\x03\x0b\x01\x02\x00\x05\x02\x02\xd0\x02\x03\x01\x1e\x04\x17\x01\x01c\x02\x04\xbe\xfc\xd9\xc4\x03\x02+\x01\x04\x04\x00\x00\x00?\x05\x02b\x05\x03,\x01\x01\x02\x02\x0c\x01\x01\x01\x02\x01\x00\x03\x01\x01\x04\x01\x1e\x03\x16\x01\x01n\x02\x04\xa5\xac\xcab\x03\x02\x18\x00\x04\x04\x00\x00\xa0@\x06\x01\r\x04\x01\x00'
            01 15           Session Control (Page 205 / Table 9-8)
                02 01           Commanda
                    01              Start streaming session
                01 10           Session identifier
                    721850a9c7764522b81e8d3e055c342d
            02 34           Selected Video Params (Page 205 / Table 9-9)
                01 01           Selected Video Codec type
                    00              H.264 (as of Page 219 / Table 9-26)
                02 09           Selected Video Codec parameters (Page 220 / Table 9-27)
                    01 01           ProfileID
                        02              High Profile
                    02 01           Level
                        02              4
                    03 01           Packetization mode                        
                        00              Non-interleaved mode
                03 0b           Video Attributes (Page 220 / Table 9-28)
                    01 02           Image width
                        0005            1280 px
                    02 02           Image height
                        d002            720 px
                    03 01           Frame rate
                        1e              30
                04 17           Selected Video RTP Params (Page 206 / Table 9-10)
                    01 01           Payload type
                        63              ??
                    02 04           SynchronizationSource for Video
                        befcd9c4
                    03 02           Maximum Bitrate
                        2b01            299 kbps
                    04 04           Min RTCP interval
                        0000003f        0.5 s
                    05 02           Max MTU
                        6205            1378 bytes
            03  2c          Selected Audio Params (Page 207 / Table 9-11)
                01 01           Selected Audio Codec type
                    02              AAC-ELD
                02 0c           Selected Audio Codec parameters (Page 217 / Table 9-21)
                    01 01           Audio channels
                        01              1 Channel
                    02 01           Bit-rate
                        00              Variable bit-rate
                    03 01           Sample rate
                        01              16 kHz
                    04 01           RTP time
                        1e              30 ms
                03 16           Selected Audio RTP parameters (Page 207 / Table 9-12)
                    01 01           Payload type
                        6e              RFC 3551 ??
                    02 04           SynchronizationSource for Audio
                        a5acca62
                    03 02           Maximum Bitrate
                        1800            24 kbps
                    04 04           Min RTCP interval
                        0000a040        5.0s
                    06 01           Comfort Noise Payload Type
                        0d              is not required
                04 01           Comfort Noise
                    00              No Comfort Noise
            
## write to selected stream configuration (end of stream)
Page 204 / UUID 00000117-0000-1000-8000-0026BB765291

    request: b'\x01\x15\x02\x01\x00\x01\x10\xcb\xd43\xce.\xf3Hf\x9cqC\x8a\xa1\xb3\xb0\xd0'
            01 15           Session Control (Page 205 / Table 9-8)
                02 01           Command
                    00              End streaming session
                01 10           Session Identifier
                    cbd433ce2ef348669c71438aa1b3b0d0
