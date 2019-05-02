# Device Name: Eve Light Strip

[Product Page](https://www.evehome.com/en/eve-light-strip) 

Python Homekit Library Version: 0.13.0

# Step 1 Discovery

In this step we test whether or not the device can be discovered properly using the 
homekit_python library.

Command - 
```
(venv) Christophers-MacBook-Air:HomekitPythonPlaying christopheryoung$ python -m homekit.discover >  pairingtest.txt
```

## Output

This is the output from the above command. In a network with multiple device, it is expected that
 we filter so that only the device of interest is included in the test file.

```
Name: Eve Light Strip 8606._hap._tcp.local.
Url: http_impl://10.101.0.175:80
Configuration number (c#): 1
Feature Flags (ff): Supports HAP Pairing (Flag: 1)
Device ID (id): 1A:EA:89:9D:04:AF
Model Name (md): Eve Light Strip 20EAS9901
Protocol Version (pv): 1.1
State Number (s#): 1
Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Lightbulb (Id: 5)
```

# Step 2. unpaired identify

In this step we will run the unpaired identify function using the Device ID (id) returned in step 1.

```
(venv) Christophers-MacBook-Air:HomekitPythonPlaying christopheryoung$ python3 -m homekit.identify -d 1A:EA:89:9D:04:AF
```

## Result:

Please record the results of the identify function here. Specific device results will vary 
between accessories. 

Eve Light strip flashes: True

# Step 3. Initialize Controller Storage

We must initialize the Controller Storage before attempting to pair any devices.

Created the file test_report.json
Note: Must contain {} in the file to be a valid JSON syntax.


# Step 4. Pairing

In this step, we will verify that the Homekit Accessory is able to be successfully paired to the 
Homekit Python controller. 

*Note ${Device Setup Code} is the Homekit pairing code in format XXX-XX-XXX where X is a digit
between 0 and 9.*

```
(venv) Christophers-MacBook-Air:HomekitPythonPlaying christopheryoung$ python3 -m homekit.pair -d
 1A:EA:89:9D:04:AF -p 555-55-555 -a Eve -f test_report.json
Pairing for "Eve" was established.
```



## Contents of test_report.json

This is the output from the above command. In the event that there are multiple devices in the 
network, please only include the JSON body for the specific device which we have paired above. 

```
{
  "Eve": {
    "AccessoryPairingID": "1A:EA:89:9D:04:AF",
    "AccessoryLTPK": "4abc5178fb710785ea00241cb85e0875e7ec21e3ec0149f6d24469c077c4b329",
    "iOSPairingId": "2d1feb16-1f94-4048-92f3-bae4c3fedd31",
    "iOSDeviceLTSK": "8748696d41490110155fd0f9807ac925f6947d441226581d30b1363b12c9ad76",
    "iOSDeviceLTPK": "9999a484a03687cc3bd1d03d95e940ac9036a891c016f4d17abfcdde558ce91b",
    "AccessoryIP": "10.101.0.175",
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
                "value": "Eve Light Strip 20EAS9901",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000023-0000-1000-8000-0026BB765291",
                "iid": 5,
                "value": "Eve Light Strip 8606",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000030-0000-1000-8000-0026BB765291",
                "iid": 6,
                "value": "HV40H1A00544",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000052-0000-1000-8000-0026BB765291",
                "iid": 7,
                "value": "1.0.5",
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
            "type": "00000043-0000-1000-8000-0026BB765291",
            "iid": 11,
            "primary": true,
            "characteristics": [
              {
                "type": "00000025-0000-1000-8000-0026BB765291",
                "iid": 12,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "bool",
                "value": true
              },
              {
                "type": "00000023-0000-1000-8000-0026BB765291",
                "iid": 13,
                "perms": [
                  "pr"
                ],
                "format": "string",
                "value": "Eve Light Strip"
              },
              {
                "type": "00000008-0000-1000-8000-0026BB765291",
                "iid": 14,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "int",
                "value": 100,
                "unit": "percentage",
                "minValue": 0,
                "maxValue": 100,
                "minStep": 1
              },
              {
                "type": "00000013-0000-1000-8000-0026BB765291",
                "iid": 15,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "float",
                "value": 3,
                "unit": "arcdegrees",
                "minValue": 0,
                "maxValue": 360,
                "minStep": 1
              },
              {
                "type": "0000002F-0000-1000-8000-0026BB765291",
                "iid": 16,
                "perms": [
                  "pw",
                  "pr",
                  "ev"
                ],
                "format": "float",
                "value": 6,
                "unit": "percentage",
                "minValue": 0,
                "maxValue": 100,
                "minStep": 1
              },
              {
                "type": "E863F11A-079E-48FF-8F27-9C2605A29F52",
                "iid": 17,
                "perms": [
                  "pr"
                ],
                "format": "uint32",
                "value": 0,
                "minValue": 0,
                "maxValue": 4294967295,
                "minStep": 1
              }
            ]
          },
          {
            "type": "E863F007-079E-48FF-8F27-9C2605A29F52",
            "iid": 18,
            "hidden": true,
            "characteristics": [
              {
                "type": "E863F131-079E-48FF-8F27-9C2605A29F52",
                "iid": 19,
                "perms": [
                  "pr"
                ],
                "format": "tlv8",
                "value": ""
              },
              {
                "type": "E863F11D-079E-48FF-8F27-9C2605A29F52",
                "iid": 20,
                "perms": [
                  "pw"
                ],
                "format": "tlv8"
              },
              {
                "type": "E863F11C-079E-48FF-8F27-9C2605A29F52",
                "iid": 21,
                "perms": [
                  "pw"
                ],
                "format": "data"
              },
              {
                "type": "E863F116-079E-48FF-8F27-9C2605A29F52",
                "iid": 22,
                "perms": [
                  "pr"
                ],
                "format": "data",
                "value": ""
              },
              {
                "type": "E863F117-079E-48FF-8F27-9C2605A29F52",
                "iid": 23,
                "perms": [
                  "pr"
                ],
                "format": "data",
                "value": ""
              },
              {
                "type": "E863F121-079E-48FF-8F27-9C2605A29F52",
                "iid": 24,
                "perms": [
                  "pw"
                ],
                "format": "data"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

# Step 5. Paired Identity

Run the following command to verify the paired identity.

```
(venv) Christophers-MacBook-Air:HomekitPythonPlaying christopheryoung$ python3 -m homekit.identify -f test_report.json -a Eve
```

## Results

Please record the results of the identify function here. Specific device results will vary 
between accessories. 

Eve Light Strip flashes: True


# Step 6. Get Accessories

In this step we wil perform the get_accessories function and record the results. 
```
(venv) Christophers-MacBook-Air:HomekitPythonPlaying christopheryoung$ python3 -m homekit.get_accessories -f test_report.json -a Eve
1.1: >accessory-information<
  1.2:  () >identify< [pw]
  1.3: Eve Systems () >manufacturer< [pr]
  1.4: Eve Light Strip 20EAS9901 () >model< [pr]
  1.5: Eve Light Strip 8606 () >name< [pr]
  1.6: HV40H1A00544 () >serial-number< [pr]
  1.7: 1.0.5 () >firmware.revision< [pr]
  1.8: 1 () >hardware.revision< [pr]
1.9: >service<
  1.10: 1.1.0 () >version< [pr]
1.11: >lightbulb<
  1.12: True () >on< [pw,pr,ev]
  1.13: Eve Light Strip () >name< [pr]
  1.14: 100 () >brightness< [pw,pr,ev]
  1.15: 3 () >hue< [pw,pr,ev]
  1.16: 6 () >saturation< [pw,pr,ev]
  1.17: 0 () >Unknown Characteristic E863F11A-079E-48FF-8F27-9C2605A29F52< [pr]
1.18: >Unknown Service: E863F007-079E-48FF-8F27-9C2605A29F52<
  1.19:  () >Unknown Characteristic E863F131-079E-48FF-8F27-9C2605A29F52< [pr]
  1.20:  () >Unknown Characteristic E863F11D-079E-48FF-8F27-9C2605A29F52< [pw]
  1.21:  () >Unknown Characteristic E863F11C-079E-48FF-8F27-9C2605A29F52< [pw]
  1.22:  () >Unknown Characteristic E863F116-079E-48FF-8F27-9C2605A29F52< [pr]
  1.23:  () >Unknown Characteristic E863F117-079E-48FF-8F27-9C2605A29F52< [pr]
  1.24:  () >Unknown Characteristic E863F121-079E-48FF-8F27-9C2605A29F52< [pw]
(venv) Christophers-MacBook-Air:HomekitPythonPlaying christopheryoung$
```
