
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


```bash
python3 -m homekit.discover
```

## result **✔**

```
...

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

...
```

# Step 2 - unpaired identify
## used command


```bash
python3 -m homekit.identify -d 31:65:CA:16:E4:78
```

## result **✔**

Eve Energy Strip Third button flashes.

# Step 3 - initialize controller storage

## used command


```bash
python3 -m homekit.init_controller_storage -f eve_energy_strip
```

## result **✔**

# Step 4 - pairing

## used command

note: Homekit Pairing code modified from original used.


```bash
python3 -m homekit.pair -d 31:65:CA:16:E4:78 -p 555-55-555 -a Eve -f eve_energy_strip
```

## result **✔**

```text
Pairing for "Eve" was established.
```

# Step 5 - paired identify

## used command


```bash
python3 -m homekit.identify -f eve_energy_strip -a Eve
```

## result  **✔**

Eve Energy Strip 3rd button light Flashes

# Step 6 - get accessories

## used command


```bash
python3 -m homekit.get_accessories -f eve_energy_strip -a Eve
```

## result  **✔**
```text
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
```

# Step 7 - get characteristics

## used command


```bash
python3 -m homekit.get_characteristic -f eve_energy_strip -a Eve -c 1.4
```

## result  **✔**

```json
{
    "1.4": {
        "value": "Eve Energy Strip 20EBA4101"
    }
}
```


# Step 8 - put characteristics

## used command

```bash
python3 -m homekit.put_characteristic -f eve_energy_strip -a Eve -c 1.14 True
```

## result  **✔**

First Plug turned on.

# Step 9 - get events

## used command

Note: Manually toggled on/off switch for 1st plug button on Eve Energy Switch


```bash
python3 -m homekit.get_events -f eve_energy_strip -a Eve -c 1.14
```

## result  **✔**

```text
event for 1.14: False
event for 1.14: True
^C
```


# Step 10 - remove pairing

## used command


```bash
python -m homekit.unpair -f eve_energy_strip -a Eve
```

## result  **✔**
```text
Pairing for "Eve" was removed.
```
