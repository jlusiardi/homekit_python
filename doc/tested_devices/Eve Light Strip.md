
# Device Name: **Eve Home Light Strip**

Important Information:
 * device manufacturer : **Eve Home**
 * device model : **Eve Light Strip**
 * device firmware version : **1.04**
 * device hardware version : **Eve Light Strip 20EAS9901**
 * communication channel : **IP**
 * version of *homekit* library: **0.13.0.**

# Step 1 - discovery

## used command


```python
python3 -m homekit.discover
``` 
    Name: Eve Light Strip BC58._hap._tcp.local.
    Url: http_impl://10.101.0.181:80
    Configuration number (c#): 1
    Feature Flags (ff): Supports HAP Pairing (Flag: 1)
    Device ID (id): 19:9A:41:EA:25:CF
    Model Name (md): Eve Light Strip 20EAS9901
    Protocol Version (pv): 1.1
    State Number (s#): 1
    Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
    Category Identifier (ci): Lightbulb (Id: 5)
    

## result **✔**

# Step 2 - unpaired identify
## used command


```python
python3 -m homekit.identify -d 19:9A:41:EA:25:CF
```

## result **✔ **

Eve Light Strip Flashes

# Step 3 - initialize controller storage

## used command


```python
python3 -m homekit.init_controller_storage -f eve_light_strip
```

## result **✔**

# Step 4 - pairing

## used command


```python
python3 -m homekit.pair -d 19:9A:41:EA:25:CF -p 555-55-555 -a Eve -f eve_light_strip
```

    Pairing for "Eve" was established.


## result **✔**

~~~
{
  "Eve": {
    "AccessoryPairingID": "19:9A:41:EA:25:CF",
    "AccessoryLTPK": "9a4cd3f11d9e54fbf4aba2e3b21bb9f5953b509532b344c8808f8834da05b819",
    "iOSPairingId": "b72b4703-896d-451f-89fd-e487a872591e",
    "iOSDeviceLTSK": "3b44e492d2037e0e322330bec120de0ba4942e287f0caabcb165fdff46c11eb0",
    "iOSDeviceLTPK": "07062ab39736c379b58c8ae11f468e25df54b81e0c35e475a838f2b805fb950b",
    "AccessoryIP": "10.101.0.181",
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
                "value": "Eve Light Strip BC58",
                "perms": [
                  "pr"
                ],
                "format": "string"
              },
              {
                "type": "00000030-0000-1000-8000-0026BB765291",
                "iid": 6,
                "value": "HV40H1A00642",
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
                "value": 1
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
                "value": 3,
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
~~~

# Step 5 - paired identify

## used command


```python
python3 -m homekit.identify -f eve_light_strip -a Eve
```

## result  **✔**

Eve Light Strip Flashes

# Step 6 - get accessories

## used command


```python
python3 -m homekit.get_accessories -f eve_light_strip -a Eve
```

    1.1: >accessory-information<
      1.2:  () >identify< [pw]
      1.3: Eve Systems () >manufacturer< [pr]
      1.4: Eve Light Strip 20EAS9901 () >model< [pr]
      1.5: Eve Light Strip BC58 () >name< [pr]
      1.6: HV40H1A00642 () >serial-number< [pr]
      1.7: 1.0.4 () >firmware.revision< [pr]
      1.8: 1 () >hardware.revision< [pr]
    1.9: >service<
      1.10: 1.1.0 () >version< [pr]
    1.11: >lightbulb<
      1.12: 1 () >on< [pw,pr,ev]
      1.13: Eve Light Strip () >name< [pr]
      1.14: 100 () >brightness< [pw,pr,ev]
      1.15: 3 () >hue< [pw,pr,ev]
      1.16: 3 () >saturation< [pw,pr,ev]
      1.17: 0 () >Unknown Characteristic E863F11A-079E-48FF-8F27-9C2605A29F52< [pr]
    1.18: >Unknown Service: E863F007-079E-48FF-8F27-9C2605A29F52<
      1.19:  () >Unknown Characteristic E863F131-079E-48FF-8F27-9C2605A29F52< [pr]
      1.20:  () >Unknown Characteristic E863F11D-079E-48FF-8F27-9C2605A29F52< [pw]
      1.21:  () >Unknown Characteristic E863F11C-079E-48FF-8F27-9C2605A29F52< [pw]
      1.22:  () >Unknown Characteristic E863F116-079E-48FF-8F27-9C2605A29F52< [pr]
      1.23:  () >Unknown Characteristic E863F117-079E-48FF-8F27-9C2605A29F52< [pr]
      1.24:  () >Unknown Characteristic E863F121-079E-48FF-8F27-9C2605A29F52< [pw]


# Step 7 - get characteristics

## used command


```python
python3 -m homekit.get_characteristic -f eve_light_strip -a Eve -c 1.4
```

    {
        "1.4": {
            "value": "Eve Light Strip 20EAS9901"
        }
    }


## result  **✔**

# Step 8 - put characteristics

## used command


```python
python3 -m homekit.put_characteristic -f eve_light_strip -a Eve -c 1.14 50
```

## result  **✔**

Light lowered to 50% brightness

# Step 9 - get events

## used command

Note: Ran *python3 -m homekit.put_characteristic -f eve_light_strip -a Eve -c 1.14 100* from a seperate terminal window to get output. 


```python
python3 -m homekit.get_events -f eve_light_strip -a Eve -c 1.14
```

    event for 1.14: 100
    ^C


## result  **✔**

# Step 10 - remove pairing

## used command


```python
python -m homekit.unpair -f eve_light_strip -a Eve
```

    Pairing for "Eve" was removed.


## result  **✔**


