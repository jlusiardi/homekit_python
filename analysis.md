# iPhone to democameraserver

## read from status

    reply: b'\x01\x01\x00'
            010100

## write to setup endpoint

    request: b'\x01\x10r\x18P\xa9\xc7vE"\xb8\x1e\x8d>\x05\\4-\x03\x1c\x01\x01\x00\x02\x0f192.168.178.237\x03\x02\xec\xd6\x04\x02\x9b\xd4\x04%\x02\x10\xa3\xc6\xa9N\x02Gii\x1a<V]%\xaa\x0e"\x03\x0e\x87T\xee|\xecD; \\\xf9\x02\xfc\xd1M\x01\x01\x00\x05%\x02\x10\xd4\xfd\xc9X\xa5\xf1\x87`-\xfd@\xb2XI\xb7\x8b\x03\x0e\xbf\xfb\xc7\xb9\xdc\x0fUU\xb1\xa4y!\x80~\x01\x01\x00'
            0110721850a9c7764522b81e8d3e055c342d031c010100020f3139322e3136382e3137382e3233370302ecd604029bd404250210a3c6a94e024769691a3c565d25aa0e22030e8754ee7cec443b205cf902fcd14d01010005250210d4fdc958a5f187602dfd40b25849b78b030ebffbc7b9dc0f5555b1a47921807e010100

## read from setup endpoint

    response: b'\x01\x10r\x18P\xa9\xc7vE"\xb8\x1e\x8d>\x05\\4-\x02\x01\x00\x03\x1b\x01\x01\x00\x02\x0e192.168.178.32\x03\x02\xec\xd6\x04\x02\x9b\xd4\x04%\x01\x01\x00\x02\x10\xa3\xc6\xa9N\x02Gii\x1a<V]%\xaa\x0e"\x03\x0e\x87T\xee|\xecD; \\\xf9\x02\xfc\xd1M\x05%\x01\x01\x00\x02\x10\xd4\xfd\xc9X\xa5\xf1\x87`-\xfd@\xb2XI\xb7\x8b\x03\x0e\xbf\xfb\xc7\xb9\xdc\x0fUU\xb1\xa4y!\x80~\x06\x01 \x07\x01 '
            0110721850a9c7764522b81e8d3e055c342d020100031b010100020e3139322e3136382e3137382e33320302ecd604029bd404250101000210a3c6a94e024769691a3c565d25aa0e22030e8754ee7cec443b205cf902fcd14d05250101000210d4fdc958a5f187602dfd40b25849b78b030ebffbc7b9dc0f5555b1a47921807e060120070120

## write to selected stream configuration (start of stream)

    request: b'\x01\x15\x02\x01\x01\x01\x10r\x18P\xa9\xc7vE"\xb8\x1e\x8d>\x05\\4-\x024\x01\x01\x00\x02\t\x01\x01\x02\x02\x01\x02\x03\x01\x00\x03\x0b\x01\x02\x00\x05\x02\x02\xd0\x02\x03\x01\x1e\x04\x17\x01\x01c\x02\x04\xbe\xfc\xd9\xc4\x03\x02+\x01\x04\x04\x00\x00\x00?\x05\x02b\x05\x03,\x01\x01\x02\x02\x0c\x01\x01\x01\x02\x01\x00\x03\x01\x01\x04\x01\x1e\x03\x16\x01\x01n\x02\x04\xa5\xac\xcab\x03\x02\x18\x00\x04\x04\x00\x00\xa0@\x06\x01\r\x04\x01\x00'
            01 15           Session Control
                02 01           Command
                    01              Start streaming session
                01 10           Session identifier
                    721850a9c7764522b81e8d3e055c342d
            02 34           Selected Video Params
                01 01           Type of codec
                    00              H.264
                02 09           Video Codec Params
                    010102020102030100
                03 0b           Video Attributes
                    010200050202d00203011e
                04 17           Selected Video RTP Params
                    01 01
                        63
                    02 04 
                        befcd9c4
                    03 02
                        2b01
                    04 04
                        0000003f
                    05 02
                        6205
            03  2c          Selected Audio Params 
                01 01           Selected Audio Codec type
                    02              AAC-ELD
                02 0c           Selected Audio Codec parameters
                    01010102010003010104011e
                03 16           Selected Audio RTP parameters
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
            01 15           Session Control
                02 01           Command
                    00              End streaming session
                01 10           Session Identifier
                    cbd433ce2ef348669c71438aa1b3b0d0