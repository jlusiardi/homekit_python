# Device Name: VELUX KIX 300

Important Information:
 * device manufacturer : Velux
 * device model : KIX 300
 * device firmware version : 61
 * device hardware version : NXG01E
 * communication channel : IP
 * version of *homekit* library: 0.15.0

[Product Page](https://www.velux.dk/produkter/smart-home/velux-active)

# Step 1 - discovery

## used command

```bash
python3 -m homekit.discover
```

## result (✔)

```text
Name: VELUX gateway._hap._tcp.local.
Url: http_impl://192.168.1.157:5001
Configuration number (c#): 24
Feature Flags (ff): Supports HAP Pairing (Flag: 1)
Device ID (id): A5:56:86:8B:8F:67
Model Name (md): VELUX Gateway
Protocol Version (pv): 1.1
State Number (s#): 1
Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Bridge (Id: 2)
```

# Step 2 - unpaired identify

## used command

```bash
python3 -m homekit.identify -d A5:56:86:8B:8F:67
```

## result **REPLACEME** (✔ or ✘)

Led is blinking on gateway

# Step 3 - initialize controller storage

## used command

```bash
python3 -m homekit.init_controller_storage -f velux
```

## result **REPLACEME** (✔ or ✘)

The file `velux.json` is created and contains `{}`.

# Step 4 - pairing

## used command

```bash
python3 -m homekit.pair -d A5:56:86:8B:8F:67 -p RED-AC-TED -f velux -a velux
```

## result (✔)

```text
Pairing for "velux" was established.
```

# Step 5 - paired identify

## used command

```bash
python3 -m homekit.identify -f velux -a velux
```

## result **REPLACEME** (✔ or ✘)

Led is pulsing on gateway

# Step 6 - get accessories

## used command

```bash
python3 -m homekit.get_accessories -f velux -a velux
```

## result **REPLACEME** (✔ or ✘)

```text
1.1: >accessory-information<
  1.2: VELUX gateway () >name< [pr]
  1.3: VELUX () >manufacturer< [pr]
  1.4: VELUX Gateway () >model< [pr]
  1.5: g37416e () >serial-number< [pr]
  1.6:  () >identify< [pw]
  1.7: 61 () >firmware.revision< [pr]
1.8: >service<
  1.9: 1.1.0 () >version< [pr]
2.1: >accessory-information<
  2.2: VELUX Sensor () >name< [pr]
  2.3: VELUX () >manufacturer< [pr]
  2.4: VELUX Sensor () >model< [pr]
  2.5: p0040fd () >serial-number< [pr]
  2.7:  () >identify< [pw]
  2.6: 16 () >firmware.revision< [pr]
2.8: >temperature<
  2.9: Temperature sensor () >name< [pr]
  2.10: 22.7 () >temperature.current< [pr,ev]
2.11: >humidity<
  2.12: Humidity sensor () >name< [pr]
  2.13: 71.0 () >relative-humidity.current< [pr,ev]
2.14: >carbon-dioxide<
  2.15: Carbon Dioxide sensor () >name< [pr]
  2.16: 0 () >carbon-dioxide.detected< [pr,ev]
  2.17: 400.0 () >carbon-dioxide.level< [pr,ev]
3.1: >accessory-information<
  3.2: VELUX Window () >name< [pr]
  3.3: VELUX () >manufacturer< [pr]
  3.4: VELUX Window () >model< [pr]
  3.5: 532a595a130e0c10 () >serial-number< [pr]
  3.7:  () >identify< [pw]
  3.6: 8 () >firmware.revision< [pr]
3.8: >window<
  3.9: Roof Window () >name< [pr]
  3.11: 0 () >position.target< [pr,pw,ev]
  3.10: 0 () >position.current< [pr,ev]
  3.12: 2 () >position.state< [pr,ev]
4.1: >accessory-information<
  4.2: VELUX Window () >name< [pr]
  4.3: VELUX () >manufacturer< [pr]
  4.4: VELUX Window () >model< [pr]
  4.5: 532a595a130e0c3e () >serial-number< [pr]
  4.7:  () >identify< [pw]
  4.6: 8 () >firmware.revision< [pr]
4.8: >window<
  4.9: Roof Window () >name< [pr]
  4.11: 0 () >position.target< [pr,pw,ev]
  4.10: 0 () >position.current< [pr,ev]
  4.12: 2 () >position.state< [pr,ev]
```

# Step 7 - get characteristics

## used command
Query 3 characteristics (`2.17` co2, `4.10` window position and `2.10` temperature):

```json
python3 -m homekit.get_characteristic -f velux -a velux -c 2.10 -c 2.17 -c 4.10 -m -t
```

## result **REPLACEME** (✔ or ✘)

```text
{
    "2.17": {
        "value": 400.0,
        "type": "93",
        "maxValue": 5000.0,
        "minValue": 0.0
    },
    "4.10": {
        "value": 0,
        "unit": "percentage",
        "type": "6D",
        "maxValue": 100,
        "minValue": 0,
        "minStep": 1
    },
    "2.10": {
        "value": 22.6,
        "unit": "celsius",
        "type": "11",
        "maxValue": 50.0,
        "minValue": 0.0,
        "minStep": 0.1
    }
}
```

# Step 8 - put characteristics

## used command
Open window to 100 pct
```bash
python -m homekit.put_characteristic -f controller.json -a koogeek -c 1.8 Off
```

## result **REPLACEME** (✔ or ✘)
Check result with `python3 -m homekit.get_characteristic -f velux -a velux -c 4.10 -m -t`
```text
{
    "4.10": {
        "minStep": 1,
        "unit": "percentage",
        "maxValue": 100,
        "value": 100,
        "minValue": 0,
        "type": "6D"
    }
}
```

# Step 9 - get events

## used command
Listen to events for characteristic `4.10` (window position) while closing window halfway

```bash
python3 -m homekit.get_events -f velux -a velux -c 4.10
```

## result **REPLACEME** (✔ or ✘)
```text
event for 4.10: 45
```

# Step 10 - remove pairing

## used command

```bash
python3 -m homekit.remove_pairing -f velux -a velux
```

## result **REPLACEME** (✔ or ✘)

```text
Pairing for "velux" was removed.
```
