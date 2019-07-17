# Device Name: **Onvis Smart Motion Sensor**

Important Information:
 * device manufacturer : **Onvis**
 * device model : **SMS1**
 * device firmware version : **2.3.3**
 * device hardware version : **1.0.1**
 * communication channel : **Bluetooth LE**
 * version of *homekit* library: **0.14.0**

[Product Page](http://www.onvistech.com)

# Step 1 - discovery

## used command

```bash
python3 -m homekit.discover_ble
```

## result ✔

```text
Name: Onvis-SMS1-634d28
MAC: d0:77:11:3f:57:1b
Configuration number (cn): 1
Device ID (id): 42:78:9B:49:27:A1
Compatible Version (cv): 2
Global State Number (s#): 8
Status Flags (sf): The accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Sensor (Id: 10)
```

# Step 2 - unpaired identify

## used command

```bash
python3 -m homekit.identify -m d0:77:11:3f:57:1b
```

## result ✔

```text
Green LED flashes on the front below the sensor panel.
```

# Step 3 - initialize controller storage

## used command

```bash
python3 -m homekit.init_controller_storage -f onvis-sms1.json
```

## result ✔

```text

```

# Step 4 - pairing

## used command

```bash
python3 -m homekit.pair_ble -m d0:77:11:3f:57:1b -p 208-21-757 -f onvis-sms1.json -a Onvis-SMS1
```

## result ✔

```text
Pairing for "Onvis-SMS1" was established.
```

# Step 5 - paired identify

## used command

```bash
python3 -m homekit.identify -f onvis-sms1.json -a Onvis-SMS1
```

## result ✔

```text
Green LED flashes on the front below the sensor panel.
```

# Step 6 - get accessories

## used command

```bash
python3 -m homekit.get_accessories -f onvis-sms1.json -a Onvis-SMS1
```

## result ✔

```text
1.1003: >Unknown Service: 4AAAF961-0DEC-11E5-B939-0800200C9A66<
  1.1005:  (Time_zone) >Unknown Characteristic 4AAAF963-0DEC-11E5-B939-0800200C9A66< [pr,pw]
  1.1004:  (Time_value) >Unknown Characteristic 4AAAF962-0DEC-11E5-B939-0800200C9A66< [pr,pw]
1.900: >Unknown Service: 00001530-1212-EFDE-1523-785FEABCD123<
  1.901:  (DFU Control Point) >Unknown Characteristic 00001531-1212-EFDE-1523-785FEABCD123< [pw,hd]
  1.902:  (Service Signature) >service-signature< [r,pr,hd]
1.255: >temperature<
  1.1012:  (Temperature_History_Data) >Unknown Characteristic 4AAAF958-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1011:  (Temperature_Today_Data) >Unknown Characteristic 4AAAF957-0DEC-11E5-B939-0800200C9A66< [pr]
  1.257:  (Current_temperature) >temperature.current< [pr,evc,evd]
  1.262:  (Name) >name< [pr]
1.143: >humidity<
  1.1010:  (Humidity_History_Data) >Unknown Characteristic 4AAAF95A-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1009:  (Humidity_Today_Data) >Unknown Characteristic 4AAAF959-0DEC-11E5-B939-0800200C9A66< [pr]
  1.145:  (Current_relative_humidity) >relative-humidity.current< [pr,evc,evd]
  1.150:  (Name) >name< [pr]
1.196: >motion<
  1.1100:  (Battery_Rating) >Unknown Characteristic 4AAAF990-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1014:  (History_Count) >Unknown Characteristic 4AAAF989-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1013:  (Today_Count) >Unknown Characteristic 4AAAF988-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1008:  (One_hundred_data) >Unknown Characteristic 4AAAF95E-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1007:  (Motion_History_Data) >Unknown Characteristic 4AAAF95D-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1006:  (Motion_Today_Data) >Unknown Characteristic 4AAAF95C-0DEC-11E5-B939-0800200C9A66< [pr]
  1.197:  (Service Signature) >service-signature< [pr]
  1.202:  (Status_low_battery) >status-lo-batt< [pr,evc,evd]
  1.198:  (Motion_detected) >motion-detected< [pr,evc,evd]
  1.203:  (Name) >name< [pr]
1.9: >pairing<
  1.13:  () >pairing.pairings< [pr,pw]
  1.12:  () >pairing.features< [r]
  1.11:  () >pairing.pair-verify< [r,w]
  1.10:  () >pairing.pair-setup< [r,w]
1.7: >service<
  1.8:  () >version< [pr]
  1.60000:  () >service-signature< [pr]
1.1: >accessory-information<
  1.17:  () >Unknown Characteristic 34AB8811-AC7F-4340-BAC3-FD6A85F9943B< [pr,hd]
  1.15:  () >hardware.revision< [pr]
  1.14:  () >firmware.revision< [pr]
  1.6:  () >serial-number< [pr]
  1.2:  () >name< [pr]
  1.5:  () >model< [pr]
  1.4:  () >manufacturer< [pr]
  1.3:  () >identify< [pw]
```

# Step 7 - get characteristics

## used command

```json
python3 -m homekit.get_characteristic -f onvis-sms1.json -a Onvis-SMS1 -c 1.257 -c 1.145 -c 1.198
```

## result ✔

```text
{
    "1.257": {
        "value": 25.0
    },
    "1.145": {
        "value": 42.0
    },
    "1.198": {
        "value": false
    }
}
```

# Step 8 - put characteristics

## used command

```bash
python3 -m homekit.put_characteristic -f onvis-sms1.json -a Onvis-SMS1 -c 1.1005 0
```

## result ✔

```text

```

# Step 9 - get events

## used command

```bash
python3 -m homekit.get_events -f onvis-sms1.json -a Onvis-SMS1 -s 5 -c 1.198
```

## result ✘

[Issue](https://github.com/jlusiardi/homekit_python/issues/62)

```text
Traceback (most recent call last):
  File "/usr/lib/python3.6/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "/usr/lib/python3.6/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "/usr/local/lib/python3.6/dist-packages/homekit/get_events.py", line 76, in <module>
    for key, value in results.items():
AttributeError: 'NoneType' object has no attribute 'items'
```

# Step 10 - remove pairing

## used command

```bash
python3 -m homekit.unpair -f onvis-sms1.json -a Onvis-SMS1
```

## result ✔

```text
Pairing for "Onvis-SMS1" was removed.
```
