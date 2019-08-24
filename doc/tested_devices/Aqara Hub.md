# Device Name: Aqara Hub

Important Information:
 * device manufacturer : Xiaomi
 * device model : Aqara Hub v3 ( homekit )
 * device firmware version : 1.6.2_003
 * device hardware version : ZHWG11LM
 * communication channel : IP
 * version of *homekit* library: 0.15.0

Note: there is two [Temperature, humidity, and atmospheric](https://www.aqara.com/en/temperature_humidity_sensor.html) and one [Aqara Cube](https://www.aqara.com/en/cube.html) connected to the aqara hub.

[Product Page](https://www.aqara.com/en/smart_home_hub.html)

# Step 1 - discovery

## used command

```bash
python3 -m homekit.discover
```

## result ✔

```text
Name: Aqara Hub-8094._hap._tcp.local.
Url: http_impl://192.168.0.202:4567
Configuration number (c#): 1
Feature Flags (ff): Supports HAP Pairing (Flag: 1)
Device ID (id): 25:64:DE:DF:DA:52
Model Name (md): Aqara Hub-8094
Protocol Version (pv): 1.1
State Number (s#): 1
Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Bridge (Id: 2)
```

# Step 2 - unpaired identify

## used command

```bash
python3 -m homekit.identify -d 25:64:DE:DF:DA:52
```

## result ✔

The gateway flashes green twice

# Step 3 - initialize controller storage

## used command

```bash
python3 -m homekit.init_controller_storage -f aqara
```

## result ✔

The file `aqara.json` is created and contains `{}`.

# Step 4 - pairing

## used command

```bash
python3 -m homekit.pair -d 25:64:DE:DF:DA:52 -p RED-AC-TED -f aqara -a aqara
```

## result ✔

```text
Pairing for "aqara" was established.
```

# Step 5 - paired identify

## used command

```bash
python3 -m homekit.identify -f aqara -a aqara
```

## result ✔

The gateway flashes green twice

# Step 6 - get accessories

## used command

```bash
python3 -m homekit.get_accessories -f aqara -a aqara
```

## result ✔

```text
1.1: >accessory-information<
  1.3: Aqara (Manufacturer) >manufacturer< [pr]
  1.4: ZHWG11LM (Model) >model< [pr]
  1.5: Aqara Hub-8094 (Name) >name< [pr]
  1.6: 0000000268408094 (Serial Number) >serial-number< [pr]
  1.7:  (Identify) >identify< [pw]
  1.8: 1.6.2 (Firmware Revision) >firmware.revision< [pr]
1.60: >service<
  1.62: 1.1.0 (Protocol Version) >version< [pr]
1.65536: >Unknown Service: 9715BF53-AB63-4449-8DC7-2785D617390A<
  1.65538: False (New Accessory Permission) >Unknown Characteristic B1C09E4C-E202-4827-B863-B0F32F727CFF< [pr,pw,ev,hd]
  1.65539: () (Accessory Joined) >Unknown Characteristic 2CB22739-1E4C-4798-A761-BC2FAF51AFC3< [pr,ev,hd]
  1.65540:   (Remove Accessory) >Unknown Characteristic 75D19FA9-218B-4943-997E-341E5D1C60CC< [pr,pw,ev,hd]
  1.65541: 5 (Gateway Volume) >Unknown Characteristic EE56B186-B0D3-488E-8C79-C21FC9BCF437< [pr,pw]
  1.65542: Chinese (Language) >Unknown Characteristic 4CF1436A-755C-4377-BDB8-30BE29EB8620< [pr,pw]
  1.65543: 2019-08-24 12:16:00+8 (Date and Time) >Unknown Characteristic 4CB28907-66DF-4D9C-962C-9971ABF30EDC< [pr,pw]
  1.65544:   (Identify Accessory) >Unknown Characteristic E1C20B22-E3A7-4B92-8BA3-C16E778648A7< [pr,ev,hd]
  1.65545:  (Country Domain) >Unknown Characteristic 25D889CB-7135-4A29-B5B4-C1FFD6D2DD5C< [pr,pw,hd]
  1.65546: -1 (Firmware Update Status) >Unknown Characteristic 7D943F6A-E052-4E96-A176-D17BF00E32CB< [pr,ev,hd]
  1.65547:  (Firmware Update Data) >Unknown Characteristic 7F51DC43-DC68-4297-BAE8-D705E61139F5< [pw,hd]
  1.65548:  (Firmware Update URL) >Unknown Characteristic A45EFD52-0DB5-4C1A-9727-513FBCD8185F< [pw,hd]
  1.65549:  (Firmware Update Checksum) >Unknown Characteristic 40F0124A-579D-40E4-865E-0EF6740EA64B< [pw,hd]
1.65792: >lightbulb<
  1.65794: Lightbulb-8094 (Name) >name< [pr]
  1.65795: False (On) >on< [pr,pw,ev]
  1.65796: 0 (Hue) >hue< [pr,pw,ev]
  1.65797: 100 (Saturation) >saturation< [pr,pw,ev]
  1.65798: 40 (Brightness) >brightness< [pr,pw,ev]
  1.65799:  (Timers) >Unknown Characteristic 232AA6BD-6CE2-4D7F-B7CF-53605F0D2BCF< [pr,pw,hd]
1.66048: >Unknown Service: 6EF066C0-08F8-46DE-9581-B89B77E459E7<
  1.66050: MIIO Service (Name) >name< [pr]
  1.66051: False (miio provisioned) >Unknown Characteristic 6EF066C1-08F8-46DE-9581-B89B77E459E7< [pr,hd]
  1.66052:  (miio bindkey) >Unknown Characteristic 6EF066C2-08F8-46DE-9581-B89B77E459E7< [pw,hd]
  1.66053: 268408094 (miio did) >Unknown Characteristic 6EF066C5-08F8-46DE-9581-B89B77E459E7< [pr,hd]
  1.66054: lumi.gateway.aqhm01 (miio model) >Unknown Characteristic 6EF066C4-08F8-46DE-9581-B89B77E459E7< [pr,hd]
  1.66055:  (miio country domain) >Unknown Characteristic 6EF066C3-08F8-46DE-9581-B89B77E459E7< [pr,pw,hd]
  1.66056: country code (miio country code) >Unknown Characteristic 6EF066D1-08F8-46DE-9581-B89B77E459E7< [pr,pw,hd]
  1.66057: app (miio config type) >Unknown Characteristic 6EF066D3-08F8-46DE-9581-B89B77E459E7< [pr,pw,hd]
  1.66058: 28800 (miio gmt offset) >Unknown Characteristic 6EF066D2-08F8-46DE-9581-B89B77E459E7< [pr,pw,hd]
  1.66059:  (miio tz) >Unknown Characteristic 6EF066D4-08F8-46DE-9581-B89B77E459E7< [pr,pw,hd]
1.66304: >security-system<
  1.66306: Security System (Name) >name< [pr]
  1.66307: 3 (Security System Current State) >security-system-state.current< [pr,ev]
  1.66308: 3 (Security System Target State) >security-system-state.target< [pr,pw,ev]
  1.66309: AAA= (Alarm Trigger Devices) >Unknown Characteristic 4AB2460A-41E4-4F05-97C3-CCFDAE1BE324< [pr,pw,hd]
3.1: >accessory-information<
  3.3: Aqara (Manufacturer) >manufacturer< [pr]
  3.4: AS008 (Model) >model< [pr]
  3.5: Temperature and Humidity Sensor-F4E5 (Name) >name< [pr]
  3.6: 00158D000309F4E5 (Serial Number) >serial-number< [pr]
  3.7:  (Identify) >identify< [pw]
  3.8: 1.0.3 (Firmware Revision) >firmware.revision< [pr]
3.196608: >temperature<
  3.196610: Temperature Sensor-F4E5 (Name) >name< [pr]
  3.196611: 25.5 (Current Temperature) >temperature.current< [pr,ev]
  3.196612: 0 (Status Low Battery) >status-lo-batt< [pr,ev]
3.196864: >humidity<
  3.196866: Humidity Sensor-F4E5 (Name) >name< [pr]
  3.196867: 52 (Current Relative Humidity) >relative-humidity.current< [pr,ev]
3.197120: >Unknown Service: C9886279-AE05-4FE1-8BF9-B6E2BAA32C01<
  3.197122: Atmospheric Pressure Sensor-F4E5 (Name) >name< [pr]
  3.197123: 34332 (Current Atmospheric Pressure) >Unknown Characteristic 1DAE55B6-36CD-4AF6-91F8-197725ED161B< [pr,ev]
4.1: >accessory-information<
  4.3: Aqara (Manufacturer) >manufacturer< [pr]
  4.4: AS008 (Model) >model< [pr]
  4.5: Temperature and Humidity Sensor-F51A (Name) >name< [pr]
  4.6: 00158D000309F51A (Serial Number) >serial-number< [pr]
  4.7:  (Identify) >identify< [pw]
  4.8: 1.0.3 (Firmware Revision) >firmware.revision< [pr]
4.262144: >temperature<
  4.262146: Temperature Sensor-F51A (Name) >name< [pr]
  4.262147: 23.3 (Current Temperature) >temperature.current< [pr,ev]
  4.262148: 0 (Status Low Battery) >status-lo-batt< [pr,ev]
4.262400: >humidity<
  4.262402: Humidity Sensor-F51A (Name) >name< [pr]
  4.262403: 59 (Current Relative Humidity) >relative-humidity.current< [pr,ev]
4.262656: >Unknown Service: C9886279-AE05-4FE1-8BF9-B6E2BAA32C01<
  4.262658: Atmospheric Pressure Sensor-F51A (Name) >name< [pr]
  4.262659: 99880 (Current Atmospheric Pressure) >Unknown Characteristic 1DAE55B6-36CD-4AF6-91F8-197725ED161B< [pr,ev]
```

# Step 7 - get characteristics

## used command
Query 3 characteristics (`4.262659` Atmospheric Pressure, `4.262403` Humidity and `4.262147` temperature):

```json
python3 -m homekit.get_characteristic -f aqara -a aqara -c 4.262659 -c 4.262403 -c 4.262147 -m -t
```

## result ✔

```text
{
    "4.262659": {
        "type": "1dae55b6-36cd-4af6-91f8-197725ed161b",
        "value": 34326,
        "format": "uint32"
    },
    "4.262403": {
        "type": "10",
        "value": 59,
        "maxValue": 100,
        "minStep": 1,
        "minValue": 0,
        "format": "float",
        "unit": "percentage"
    },
    "4.262147": {
        "type": "11",
        "value": 23.4,
        "maxValue": 100,
        "minStep": 0.1,
        "minValue": -50,
        "format": "float",
        "unit": "celsius"
    }
}
```

# Step 8 - put characteristics

## used command
Turn on the light
```bash
python -m homekit.put_characteristic -f aqara -a aqara -c 1.65795 True
```

## result ✔
Check result with `python3 -m homekit.get_characteristic -f aqara -a aqara -c 1.65795 -m -t`
```text
{
    "1.65795": {
        "type": "25",
        "value": true,
        "format": "bool"
    }
}
```

# Step 9 - get events

## used command
Listen to events for characteristic `1.65795` (light status) while turning it on an off

```bash
python3 -m homekit.get_events -f aqara -a aqara -c 1.65795
```

## result ✔
```text
event for 1.65795: False
event for 1.65795: True
event for 1.65795: False
```

# Step 10 - remove pairing

## used command

```bash
python3 -m homekit.remove_pairing -f aqara -a aqara
```

## result ✔

```text
Pairing for "aqara" was removed.
```
