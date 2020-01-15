# Device Name: Koogeek P1EU

Important Information:
 * device manufacturer : Koogeek
 * device model : P1EU
 * device firmware version : 1.2.9
 * device hardware version : not available
 * communication channel : IP
 * version of *homekit* library: 0.14.0

[Product Page](https://www.koogeek.com/p-p1eu.html)

# Step 1 - discovery

## used command

```bash
python -m homekit.discover
```

## result ✔

```text
Name: Koogeek-P1-770D90._hap._tcp.local.
Url: http_impl://192.168.178.227:80
Configuration number (c#): 1
Feature Flags (ff): Supports HAP Pairing (Flag: 1)
Device ID (id): 0E:8F:DD:94:15:D3
Model Name (md): P1EU
Protocol Version (pv): 1.0
State Number (s#): 1
Status Flags (sf): Accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Outlet (Id: 7)
```

# Step 2 - unpaired identify

## used command

```bash
python -m homekit.identify -d 0E:8F:DD:94:15:D3
```

## result ✔

The plug's LED changes from green to red and back again.

# Step 3 - initialize controller storage

## used command

```bash
python -m homekit.init_controller_storage -f controller.json
```

## result ✔

The file `controller.json` is created and contains `{}`.

# Step 4 - pairing

## used command

```bash
python -m homekit.pair -f controller.json -a koogeek -p XXX-XX-XXX -d 0E:8F:DD:94:15:D3
```

## result ✔

```text
Pairing for "koogeek" was established.
```

The file `controller.json` contains the data for the alias `koogeek`.

# Step 5 - paired identify

## used command

```bash
python -m homekit.identify -f controller.json -a koogeek
```

## result ✔

The plug's LED changes from green to red and back again.


# Step 6 - get accessories

## used command

```bash
python -m homekit.get_accessories -f controller.json -a koogeek
```

## result ✔

```text
1.1: >accessory-information<
  1.2: Koogeek-P1-770D90 () >name< [pr]
  1.3: Koogeek () >manufacturer< [pr]
  1.4: P1EU () >model< [pr]
  1.5: EUCP031715001435 () >serial-number< [pr]
  1.6:  () >identify< [pw]
  1.37: 1.2.9 () >firmware.revision< [pr]
1.7: >outlet<
  1.8: True () >on< [pr,pw,ev]
  1.9: False () >outlet-in-use< [pr,ev]
  1.10: Outlet () >name< [pr]
1.11: >Unknown Service: 4AAAF940-0DEC-11E5-B939-0800200C9A66<
  1.12: AHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (TIMER_SETTINGS) >Unknown Characteristic 4AAAF942-0DEC-11E5-B939-0800200C9A66< [pr,pw]
1.13: >Unknown Service: 151909D0-3802-11E4-916C-0800200C9A66<
  1.14: url,data (FW Upgrade supported types) >Unknown Characteristic 151909D2-3802-11E4-916C-0800200C9A66< [pr,hd]
  1.15:  (FW Upgrade URL) >Unknown Characteristic 151909D1-3802-11E4-916C-0800200C9A66< [pw,hd]
  1.16: 0 (FW Upgrade Status) >Unknown Characteristic 151909D6-3802-11E4-916C-0800200C9A66< [pr,ev,hd]
  1.17:  (FW Upgrade Data) >Unknown Characteristic 151909D7-3802-11E4-916C-0800200C9A66< [pw,hd]
1.18: >Unknown Service: 151909D3-3802-11E4-916C-0800200C9A66<
  1.19: 0 (Timezone) >Unknown Characteristic 151909D5-3802-11E4-916C-0800200C9A66< [pr,pw]
  1.20: 1556704317 (Time value since Epoch) >Unknown Characteristic 151909D4-3802-11E4-916C-0800200C9A66< [pr,pw]
1.21: >Unknown Service: 4AAAF930-0DEC-11E5-B939-0800200C9A66<
  1.22: 0.0 (1 REALTIME_ENERGY) >Unknown Characteristic 4AAAF931-0DEC-11E5-B939-0800200C9A66< [pr,ev]
  1.23: 0.0 (2 CURRENT_HOUR_DATA) >Unknown Characteristic 4AAAF932-0DEC-11E5-B939-0800200C9A66< [pr,ev]
  1.24: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (3 HOUR_DATA_TODAY) >Unknown Characteristic 4AAAF933-0DEC-11E5-B939-0800200C9A66< [pr]
  1.25: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (4 HOUR_DATA_YESTERDAY) >Unknown Characteristic 4AAAF934-0DEC-11E5-B939-0800200C9A66< [pr]
  1.26: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (5 HOUR_DATA_2_DAYS_BEFORE) >Unknown Characteristic 4AAAF935-0DEC-11E5-B939-0800200C9A66< [pr]
  1.27: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (6 HOUR_DATA_3_DAYS_BEFORE) >Unknown Characteristic 4AAAF936-0DEC-11E5-B939-0800200C9A66< [pr]
  1.28: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (7 HOUR_DATA_4_DAYS_BEFORE) >Unknown Characteristic 4AAAF937-0DEC-11E5-B939-0800200C9A66< [pr]
  1.29: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (8 HOUR_DATA_5_DAYS_BEFORE) >Unknown Characteristic 4AAAF938-0DEC-11E5-B939-0800200C9A66< [pr]
  1.30: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (9 HOUR_DATA_6_DAYS_BEFORE) >Unknown Characteristic 4AAAF939-0DEC-11E5-B939-0800200C9A66< [pr]
  1.31: AGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (10 HOUR_DATA_7_DAYS_BEFORE) >Unknown Characteristic 4AAAF93A-0DEC-11E5-B939-0800200C9A66< [pr]
  1.32: AHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (11 DAY_DATA_THIS_MONTH) >Unknown Characteristic 4AAAF93B-0DEC-11E5-B939-0800200C9A66< [pr]
  1.33: AHwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (12 DAY_DATA_LAST_MONTH) >Unknown Characteristic 4AAAF93C-0DEC-11E5-B939-0800200C9A66< [pr]
  1.34: ADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (13 MONTH_DATA_THIS_YEAR) >Unknown Characteristic 4AAAF93D-0DEC-11E5-B939-0800200C9A66< [pr]
  1.35: ADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= (14 MONTH_DATA_LAST_YEAR) >Unknown Characteristic 4AAAF93E-0DEC-11E5-B939-0800200C9A66< [pr]
  1.36: 0 (15 RUNNING_TIME) >Unknown Characteristic 4AAAF93F-0DEC-11E5-B939-0800200C9A66< [pr,ev]
```

# Step 7 - get characteristics

## used command

Query 2 characteristics (`1.8` power state and `1.22` the current real time power) including all optional parameters:

```bash
python -m homekit.get_characteristic -f controller.json -a koogeek -c 1.8 -c 1.22 -m -p -t
```

## result ✔

```json
{
    "1.8": {
        "perms": [
            "pr",
            "pw",
            "ev"
        ],
        "type": "25",
        "format": "bool",
        "value": true
    },
    "1.22": {
        "perms": [
            "pr",
            "ev"
        ],
        "value": 102.0,
        "type": "4aaaf931-0dec-11e5-b939-0800200c9a66",
        "format": "float",
        "description": "1 REALTIME_ENERGY"
    }
}
```

# Step 8 - put characteristics

## used command

```bash
python -m homekit.put_characteristic -f controller.json -a koogeek -c 1.8 Off
```

## result ✔

The plug turns itself off.

# Step 9 - get events

## used command

Listen to events for characteristic `1.22` current real time power
```bash
python -m homekit.get_events -f controller.json -a koogeek -c 1.22 -e 5
```

## result ✔

As requested 5 events get printed:
```text
event for 1.22: 99.0
event for 1.22: 102.0
event for 1.22: 103.0
event for 1.22: 102.0
event for 1.22: 103.0
```

# Step 10 - remove pairing

## used command

```bash
python -m homekit.unpair -f controller.json -a koogeek
```

## result ✔

```text
Pairing for "koogeek" was removed.
```
