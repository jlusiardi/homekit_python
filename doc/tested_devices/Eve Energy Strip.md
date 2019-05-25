
# Device Name: **Eve Home Light Strip**

Important Information:
 * device manufacturer : **Eve Home**
 * device model : **Eve Energy Strip**
 * device firmware version : **1.0.4**
 * device hardware version : **Eve Energy Strip 20EBA4101**
 * communication channel : **IP**
 * version of *homekit* library: **0.14.0.**

# Step 1 - discovery

## used command


```python
!python3 -m homekit.discover
```

    Name: TRADFRI gateway._hap._tcp.local.
    Url: http_impl://10.101.0.112:80
    Configuration number (c#): 519
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): FA:1B:E3:A7:9E:6E
    Model Name (md): TRADFRI gateway
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Bridge (Id: 2)
    
    Name: Xiaoyan HC - 789b41._hap._tcp.local.
    Url: http_impl://10.101.0.126:46306
    Configuration number (c#): 32
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 09:8b:8c:6a:31:58
    Model Name (md): xiaoyan home center
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Bridge (Id: 2)
    
    Name: Omna 180Cam HD - 790D._hap._tcp.local.
    Url: http_impl://10.101.0.92:5010
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): B8:00:CC:07:9B:0F
    Model Name (md): DSH-C310
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): IP Camera (Id: 17)
    
    Name: Philips hue - 2687A7._hap._tcp.local.
    Url: http_impl://10.101.0.120:8080
    Configuration number (c#): 105
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): D6:A6:AF:B9:45:FC
    Model Name (md): BSB002
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Bridge (Id: 2)
    
    Name: ArloBaby1A._hap._tcp.local.
    Url: http_impl://10.101.0.171:5051
    Configuration number (c#): 22
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): EA:14:B6:A5:EA:47
    Model Name (md): ABC1000
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): IP Camera (Id: 17)
    
    Name: iHome SmartMonitor-A289F4._hap._tcp.local.
    Url: http_impl://10.101.0.102:80
    Configuration number (c#): 2
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 6D:3A:28:5E:56:A6
    Model Name (md): iSS50
    Protocol Version (pv): 1.0
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Sensor (Id: 10)
    
    Name: LaserEgg2-C42ED9._hap._tcp.local.
    Url: http_impl://10.101.0.88:80
    Configuration number (c#): 2
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 7E:14:DE:BE:17:4A
    Model Name (md): LE-200
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Sensor (Id: 10)
    
    Name: iHome SmartPlug-C4CF6A._hap._tcp.local.
    Url: http_impl://10.101.0.83:80
    Configuration number (c#): 5
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 0E:AA:CE:2B:35:71
    Model Name (md): iSP8
    Protocol Version (pv): 1.0
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Outlet (Id: 7)
    
    Name: GLOCO-C152._hap._tcp.local.
    Url: http_impl://10.101.0.84:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 80:A5:89:C0:C1:52
    Model Name (md): GLOCO-500
    Protocol Version (pv): 1.0
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Sensor (Id: 10)
    
    Name: Koogeek-LS1-1FF6B0._hap._tcp.local.
    Url: http_impl://10.101.0.60:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 8C:DB:AC:08:E5:68
    Model Name (md): LS1
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Light Panels 50:d2:b7._hap._tcp.local.
    Url: http_impl://10.101.0.73:6517
    Configuration number (c#): 6
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 82:9C:E8:3B:94:EF
    Model Name (md): NL22
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: iHaper-DL1-208A66._hap._tcp.local.
    Url: http_impl://10.101.0.174:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): AF:12:3B:5B:F9:2F
    Model Name (md): DL1
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Outlet (Id: 7)
    
    Name: Main Floor._hap._tcp.local.
    Url: http_impl://10.101.0.168:1200
    Configuration number (c#): 14
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 99:2C:C7:72:F0:A2
    Model Name (md): ecobee4
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Thermostat (Id: 9)
    
    Name: Aqara Hub-A779._hap._tcp.local.
    Url: http_impl://10.101.0.125:4567
    Configuration number (c#): 16
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 50:E0:B3:76:FD:0F
    Model Name (md): Aqara Hub-1900
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Bridge (Id: 2)
    
    Name: VOCOlinc-Flowerbud-0d19f1._hap._tcp.local.
    Url: http_impl://10.101.0.133:80
    Configuration number (c#): 14
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): C8:93:D2:13:47:7D
    Model Name (md): VOCOlinc-Flowerbud-0d19f1
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Humidifier (Id: 22)
    
    Name: ConnectSense Outlet 2 01786E._hap._tcp.local.
    Url: http_impl://10.101.0.124:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 17:0F:14:F9:C6:5D
    Model Name (md): CS-SO-2
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Outlet (Id: 7)
    
    Name: VOCOlinc-PM2-0bbd7c._hap._tcp.local.
    Url: http_impl://10.101.0.79:80
    Configuration number (c#): 12
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): DF:E1:49:D0:38:86
    Model Name (md): VOCOlinc-PM2-0bbd7c
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Outlet (Id: 7)
    
    Name: LifX Strip Top._hap._tcp.local.
    Url: http_impl://10.101.0.110:80
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): B6:1B:12:3E:43:B2
    Model Name (md): LIFX Z
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Lifx Master Bedroom Strip._hap._tcp.local.
    Url: http_impl://10.101.0.65:80
    Configuration number (c#): 4
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 74:54:0F:8C:F7:9A
    Model Name (md): LIFX Z
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Logi Circle._hap._tcp.local.
    Url: http_impl://10.101.0.156:8080
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): E2:3E:22:29:A8:2A
    Model Name (md): V-R0008
    Protocol Version (pv): 1.0
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): IP Camera (Id: 17)
    
    Name: Flood  Master Bedroom._hap._tcp.local.
    Url: http_impl://10.101.0.64:80
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 43:98:C2:91:83:5F
    Model Name (md): LIFX BR30
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: VOCOlinc-LS1-0c657f._hap._tcp.local.
    Url: http_impl://10.101.0.70:80
    Configuration number (c#): 11
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 84:A0:82:FA:A2:02
    Model Name (md): VOCOlinc-LS1-0c657f
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Eve Light Strip BC58._hap._tcp.local.
    Url: http_impl://10.101.0.181:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 19:9A:41:EA:25:CF
    Model Name (md): Eve Light Strip 20EAS9901
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: CviLux-AirPurifier-A0BC._hap._tcp.local.
    Url: http_impl://10.101.0.137:80
    Configuration number (c#): 2
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 2C:85:91:11:99:96
    Model Name (md): FHH106
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Air Purifier (Id: 19)
    
    Name: VOCOlinc-L1-0c28cc._hap._tcp.local.
    Url: http_impl://10.101.0.138:80
    Configuration number (c#): 5
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 64:15:00:89:E1:2B
    Model Name (md): VOCOlinc-L1-0c28cc
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: VOCOlinc-L1-0c0c35._hap._tcp.local.
    Url: http_impl://10.101.0.97:80
    Configuration number (c#): 5
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 14:AA:01:0B:F1:B8
    Model Name (md): VOCOlinc-L1-0c0c35
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Healthy Home Coach._hap._tcp.local.
    Url: http_impl://10.101.0.66:5001
    Configuration number (c#): 4
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): B4:35:6E:AA:39:5D
    Model Name (md): Healthy Home Coach 
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Sensor (Id: 10)
    
    Name: Games Flood One._hap._tcp.local.
    Url: http_impl://10.101.0.90:80
    Configuration number (c#): 8
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): C9:D2:EE:D2:5A:6D
    Model Name (md): LIFX BR30
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Joshua’s Main Light._hap._tcp.local.
    Url: http_impl://10.101.0.74:80
    Configuration number (c#): 10
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 3C:E0:EE:CC:24:A2
    Model Name (md): LIFX BR30
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Canvas 6A54._hap._tcp.local.
    Url: http_impl://10.101.0.128:6517
    Configuration number (c#): 4
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 57:C8:27:4B:E7:33
    Model Name (md): NL29
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Eve Energy Strip B1E5._hap._tcp.local.
    Url: http_impl://10.101.0.161:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 31:65:CA:16:E4:78
    Model Name (md): Eve Energy Strip 20EBA4101
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
    Category Identifier (ci): Outlet (Id: 7)
    
    Name: Plants._hap._tcp.local.
    Url: http_impl://10.101.0.76:80
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 70:26:C0:BC:31:7F
    Model Name (md): LIFX Pls BR30
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Games Flood Two._hap._tcp.local.
    Url: http_impl://10.101.0.89:80
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 56:E3:17:08:12:94
    Model Name (md): LIFX Pls BR30
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: VOCOlinc-PM3-0be650._hap._tcp.local.
    Url: http_impl://10.101.0.77:80
    Configuration number (c#): 19
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 50:5F:A4:BD:D8:69
    Model Name (md): VOCOlinc-PM3-0be650
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Outlet (Id: 7)
    
    Name: MiBedsideLamp2-17DD._hap._tcp.local.
    Url: http_impl://10.101.0.108:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): F8:4C:F5:1D:A1:B1
    Model Name (md): MJCTD02YL
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Games Flood Four._hap._tcp.local.
    Url: http_impl://10.101.0.63:80
    Configuration number (c#): 9
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 13:5D:2B:A5:84:5E
    Model Name (md): LIFX Pls BR30
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: MiDeskLampPro-1712._hap._tcp.local.
    Url: http_impl://10.101.0.67:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 8B:19:1B:BE:76:B1
    Model Name (md): MJTD02YL
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: Eve Light Strip 8606._hap._tcp.local.
    Url: http_impl://10.101.0.175:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): A7:C2:62:F3:D5:14
    Model Name (md): Eve Light Strip 20EAS9901
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: iHaper-L3-9C5931._hap._tcp.local.
    Url: http_impl://10.101.0.144:80
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): BE:91:7F:F9:32:4E
    Model Name (md): L3
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Lightbulb (Id: 5)
    
    Name: iDevices Outdoor Switch._hap._tcp.local.
    Url: http_impl://169.254.89.133:80
    Configuration number (c#): 3
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): AE:E4:D8:DC:12:2F
    Model Name (md): IDEV0004
    Protocol Version (pv): 1.0
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): Switch (Id: 8)
    
    Name: Netatmo Welcome._hap._tcp.local.
    Url: http_impl://10.101.0.154:5001
    Configuration number (c#): 5
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): EB:30:84:4C:A6:DA
    Model Name (md): Welcome
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has been paired. (Flag: 0)
    Category Identifier (ci): IP Camera (Id: 17)
    


## result **✔**

```
Name: Eve Energy Strip B1E5._hap._tcp.local.
Url: http_impl://10.101.0.161:80
Configuration number (c#): 1
Feature Flags (ff): Supports HAP Pairing (Flag: 1)
Device ID (id): 31:65:CA:16:E4:78
Model Name (md): Eve Energy Strip 20EBA4101
Protocol Version (pv): 1.1
State Number (s#): 1
Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Outlet (Id: 7)
```

# Step 2 - unpaired identify
## used command


```python
!python3 -m homekit.identify -d 31:65:CA:16:E4:78
```

## result **✔**

Eve Energy Strip Third button Flashes

# Step 3 - initialize controller storage

## used command


```python
!python3 -m homekit.init_controller_storage -f eve_energy_strip
```

## result **✔**

# Step 4 - pairing

## used command

note: Homekit Pairing code modified from original used.


```python
!python3 -m homekit.pair -d 31:65:CA:16:E4:78 -p 555-55-555 -a Eve -f eve_energy_strip
```

    Pairing for "Eve" was established.


## result **✔**

~~~
{
  "Eve": {
    "AccessoryPairingID": "31:65:CA:16:E4:78",
    "AccessoryLTPK": "b098de0757d91ea1307eff708c833d7638bb0039fd15fbf367e7edfbe0cf7cd1",
    "iOSPairingId": "2a2c94da-3722-42f7-adc9-81d95adb7b09",
    "iOSDeviceLTSK": "26427a558c011164d9ce79aacc4eb36c034f25b92d3ff4fe352472df24d5b9ef",
    "iOSDeviceLTPK": "c28ca6e9f9f6db141705b2566b1626dca8c1ce69549b95ac353a370d80c4dd39",
    "AccessoryIP": "10.101.0.161",
    "AccessoryPort": 80,
    "Connection": "IP",
    "accessories": [
      {
        "aid": 1,
        "services": [
          {
            "type": "0000003E-0000-1000-8000-0026BB765291",
            "iid": 1,
            "characteristics": [
              {
                "type": "00000014-0000-1000-8000-0026BB765291",
                "iid": 2,
                "perms": [
                  "pw"
                ],
                "format": "bool"
              },
              {
                "type": "00000020-0000-1000-8000-0026BB765291",
                "iid": 3,
                "value": "Eve Systems",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000021-0000-1000-8000-0026BB765291",
                "iid": 4,
                "value": "Eve Energy Strip 20EBA4101",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000023-0000-1000-8000-0026BB765291",
                "iid": 5,
                "value": "Eve Energy Strip B1E5",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000030-0000-1000-8000-0026BB765291",
                "iid": 6,
                "value": "JV09I1A00494",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000052-0000-1000-8000-0026BB765291",
                "iid": 7,
                "value": "1.0.4",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000053-0000-1000-8000-0026BB765291",
                "iid": 8,
                "value": "1",
                "perms": [
                  "pr"
                ],
                "format": "string"
              }
            ]
          },
          {
            "type": "000000A2-0000-1000-8000-0026BB765291",
            "iid": 9,
            "characteristics": [
              {
                "type": "00000037-0000-1000-8000-0026BB765291",
                "iid": 10,
                "value": "1.1.0",
                "perms": [
                  "pr"
                ],
                "format": "string"
              }
            ]
          },
          {
            "type": "000000CC-0000-1000-8000-0026BB765291",
            "iid": 11,
            "characteristics": [
              {
                "type": "000000CD-0000-1000-8000-0026BB765291",
                "iid": 12,
                "perms": [
                  "pr"
                ],
                "format": "uint8",
                "value": 0,
                "minValue": 0,
                "maxValue": 1,
                "minStep": 1
              }
            ]
          },
          {
            "type": "00000047-0000-1000-8000-0026BB765291",
            "iid": 13,
            "primary": true,
            "characteristics": [
              {
                "type": "00000025-0000-1000-8000-0026BB765291",
                "iid": 14,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "00000026-0000-1000-8000-0026BB765291",
                "iid": 15,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": false
              },
              {
                "type": "00000023-0000-1000-8000-0026BB765291",
                "iid": 16,
                "perms": [
                  "pr"
                ],
                "format": "string",
                "value": "Eve Energy Strip 1"
              },
              {
                "type": "000000CB-0000-1000-8000-0026BB765291",
                "iid": 17,
                "perms": [
                  "pr"
                ],
                "format": "uint8",
                "value": 1,
                "minValue": 1,
                "maxValue": 255,
                "minStep": 1
              },
              {
                "type": "00000075-0000-1000-8000-0026BB765291",
                "iid": 18,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "E863F11A-079E-48FF-8F27-9C2605A29F52",
                "iid": 19,
                "perms": [
                  "pr"
                ],
                "format": "uint32",
                "value": 10,
                "minValue": 0,
                "maxValue": 4294967295,
                "minStep": 1
              }
            ]
          },
          {
            "type": "00000047-0000-1000-8000-0026BB765291",
            "iid": 20,
            "characteristics": [
              {
                "type": "00000025-0000-1000-8000-0026BB765291",
                "iid": 21,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "00000026-0000-1000-8000-0026BB765291",
                "iid": 22,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": false
              },
              {
                "type": "00000023-0000-1000-8000-0026BB765291",
                "iid": 23,
                "perms": [
                  "pr"
                ],
                "format": "string",
                "value": "Eve Energy Strip 2"
              },
              {
                "type": "000000CB-0000-1000-8000-0026BB765291",
                "iid": 24,
                "perms": [
                  "pr"
                ],
                "format": "uint8",
                "value": 2,
                "minValue": 1,
                "maxValue": 255,
                "minStep": 1
              },
              {
                "type": "00000075-0000-1000-8000-0026BB765291",
                "iid": 25,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "E863F11A-079E-48FF-8F27-9C2605A29F52",
                "iid": 26,
                "perms": [
                  "pr"
                ],
                "format": "uint32",
                "value": 12,
                "minValue": 0,
                "maxValue": 4294967295,
                "minStep": 1
              }
            ]
          },
          {
            "type": "00000047-0000-1000-8000-0026BB765291",
            "iid": 27,
            "characteristics": [
              {
                "type": "00000025-0000-1000-8000-0026BB765291",
                "iid": 28,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "00000026-0000-1000-8000-0026BB765291",
                "iid": 29,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": false
              },
              {
                "type": "00000023-0000-1000-8000-0026BB765291",
                "iid": 30,
                "perms": [
                  "pr"
                ],
                "format": "string",
                "value": "Eve Energy Strip 3"
              },
              {
                "type": "000000CB-0000-1000-8000-0026BB765291",
                "iid": 31,
                "perms": [
                  "pr"
                ],
                "format": "uint8",
                "value": 3,
                "minValue": 1,
                "maxValue": 255,
                "minStep": 1
              },
              {
                "type": "00000075-0000-1000-8000-0026BB765291",
                "iid": 32,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "E863F11A-079E-48FF-8F27-9C2605A29F52",
                "iid": 33,
                "perms": [
                  "pr"
                ],
                "format": "uint32",
                "value": 15,
                "minValue": 0,
                "maxValue": 4294967295,
                "minStep": 1
              }
            ]
          },
          {
            "type": "E863F007-079E-48FF-8F27-9C2605A29F52",
            "iid": 34,
            "hidden": true,
            "characteristics": [
              {
                "type": "E863F131-079E-48FF-8F27-9C2605A29F52",
                "iid": 35,
                "perms": [
                  "pr"
                ],
                "format": "tlv8",
                "value": ""
              },
              {
                "type": "E863F11D-079E-48FF-8F27-9C2605A29F52",
                "iid": 36,
                "perms": [
                  "pw"
                ],
                "format": "tlv8"
              },
              {
                "type": "E863F11C-079E-48FF-8F27-9C2605A29F52",
                "iid": 37,
                "perms": [
                  "pw"
                ],
                "format": "data"
              },
              {
                "type": "E863F116-079E-48FF-8F27-9C2605A29F52",
                "iid": 38,
                "perms": [
                  "pr"
                ],
                "format": "data",
                "value": ""
              },
              {
                "type": "E863F117-079E-48FF-8F27-9C2605A29F52",
                "iid": 39,
                "perms": [
                  "pr"
                ],
                "format": "data",
                "value": ""
              },
              {
                "type": "E863F121-079E-48FF-8F27-9C2605A29F52",
                "iid": 40,
                "perms": [
                  "pw"
                ],
                "format": "data"
              }
            ]
          },
          {
            "type": "E863F008-079E-48FF-8F27-9C2605A29F52",
            "iid": 41,
            "hidden": true,
            "characteristics": [
              {
                "type": "E863F10A-079E-48FF-8F27-9C2605A29F52",
                "iid": 42,
                "perms": [
                  "pr"
                ],
                "format": "float",
                "value": 0
              },
              {
                "type": "E863F126-079E-48FF-8F27-9C2605A29F52",
                "iid": 43,
                "perms": [
                  "pr"
                ],
                "format": "float",
                "value": 0
              },
              {
                "type": "E863F10D-079E-48FF-8F27-9C2605A29F52",
                "iid": 44,
                "perms": [
                  "pr"
                ],
                "format": "float",
                "value": 0
              },
              {
                "type": "E863F10C-079E-48FF-8F27-9C2605A29F52",
                "iid": 45,
                "perms": [
                  "pr"
                ],
                "format": "float",
                "value": 0
              },
              {
                "type": "00000077-0000-1000-8000-0026BB765291",
                "iid": 46,
                "perms": [
                  "pr",
                  "ev"
                ],
                "format": "uint8",
                "value": 0
              },
              {
                "type": "000000A7-0000-1000-8000-0026BB765291",
                "iid": 47,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "uint8",
                "value": 0,
                "minValue": 0,
                "maxValue": 1,
                "minStep": 1
              }
            ]
          }
        ]
      }
    ]
  }
}
~~~

# Step 5 - paired identify

## used command


```python
!python3 -m homekit.identify -f eve_energy_strip -a Eve
```

## result  **✔**

Eve Energy Strip 3rd button light Flashes

# Step 6 - get accessories

## used command


```python
!python3 -m homekit.get_accessories -f eve_energy_strip -a Eve
```

    1.1: >accessory-information<
      1.2:  () >identify< [pw]
      1.3: Eve Systems () >manufacturer< [pr]
      1.4: Eve Energy Strip 20EBA4101 () >model< [pr]
      1.5: Eve Energy Strip B1E5 () >name< [pr]
      1.6: JV09I1A00494 () >serial-number< [pr]
      1.7: 1.0.4 () >firmware.revision< [pr]
      1.8: 1 () >hardware.revision< [pr]
    1.9: >service<
      1.10: 1.1.0 () >version< [pr]
    1.11: >service-label<
      1.12: 0 () >service-label-namespace< [pr]
    1.13: >outlet<
      1.14: False () >on< [pw,pr,ev]
      1.15: False () >outlet-in-use< [pr,ev]
      1.16: Eve Energy Strip 1 () >name< [pr]
      1.17: 1 () >service-label-index< [pr]
      1.18: True () >status-active< [pr,ev]
      1.19: 10 () >Unknown Characteristic E863F11A-079E-48FF-8F27-9C2605A29F52< [pr]
    1.20: >outlet<
      1.21: True () >on< [pw,pr,ev]
      1.22: False () >outlet-in-use< [pr,ev]
      1.23: Eve Energy Strip 2 () >name< [pr]
      1.24: 2 () >service-label-index< [pr]
      1.25: True () >status-active< [pr,ev]
      1.26: 12 () >Unknown Characteristic E863F11A-079E-48FF-8F27-9C2605A29F52< [pr]
    1.27: >outlet<
      1.28: True () >on< [pw,pr,ev]
      1.29: False () >outlet-in-use< [pr,ev]
      1.30: Eve Energy Strip 3 () >name< [pr]
      1.31: 3 () >service-label-index< [pr]
      1.32: True () >status-active< [pr,ev]
      1.33: 15 () >Unknown Characteristic E863F11A-079E-48FF-8F27-9C2605A29F52< [pr]
    1.34: >Unknown Service: E863F007-079E-48FF-8F27-9C2605A29F52<
      1.35:  () >Unknown Characteristic E863F131-079E-48FF-8F27-9C2605A29F52< [pr]
      1.36:  () >Unknown Characteristic E863F11D-079E-48FF-8F27-9C2605A29F52< [pw]
      1.37:  () >Unknown Characteristic E863F11C-079E-48FF-8F27-9C2605A29F52< [pw]
      1.38:  () >Unknown Characteristic E863F116-079E-48FF-8F27-9C2605A29F52< [pr]
      1.39:  () >Unknown Characteristic E863F117-079E-48FF-8F27-9C2605A29F52< [pr]
      1.40:  () >Unknown Characteristic E863F121-079E-48FF-8F27-9C2605A29F52< [pw]
    1.41: >Unknown Service: E863F008-079E-48FF-8F27-9C2605A29F52<
      1.42: 0 () >Unknown Characteristic E863F10A-079E-48FF-8F27-9C2605A29F52< [pr]
      1.43: 0 () >Unknown Characteristic E863F126-079E-48FF-8F27-9C2605A29F52< [pr]
      1.44: 0 () >Unknown Characteristic E863F10D-079E-48FF-8F27-9C2605A29F52< [pr]
      1.45: 0 () >Unknown Characteristic E863F10C-079E-48FF-8F27-9C2605A29F52< [pr]
      1.46: 0 () >status-fault< [pr,ev]
      1.47: 0 () >lock-physical-controls< [pw,pr,ev]


# Step 7 - get characteristics

## used command


```python
!python3 -m homekit.get_characteristic -f eve_energy_strip -a Eve -c 1.4
```

    {
        "1.4": {
            "value": "Eve Energy Strip 20EBA4101"
        }
    }


## result  **✔**

# Step 8 - put characteristics

## used command


```python
!python3 -m homekit.put_characteristic -f eve_energy_strip -a Eve -c 1.14 True
```

## result  **✔**

First Plug turned on.

# Step 9 - get events

## used command

Note: Manually toggled on/off switch for 1st plug button on Eve Energy Switch


```python
!python3 -m homekit.get_events -f eve_energy_strip -a Eve -c 1.14
```

    event for 1.14: False
    event for 1.14: True
    ^C


## result  **✔**

# Step 10 - remove pairing

## used command


```python
!python -m homekit.unpair -f eve_energy_strip -a Eve
```

    Pairing for "Eve" was removed.


## result  **✔**
