# Device Name: **REPLACEME**

Important Information:
 * device manufacturer : Koogeek
 * device model : DW1
 * device firmware version : 2.1.2
 * device hardware version : 1.0.1
 * communication channel : Bluetooth LE
 * version of *homekit* library: 0.14.0

[Product Page](https://www.koogeek.com/p-dw1.html)

# Step 1 - discovery

## used command

```bash
python -m homekit.discover_ble
```

## result ✔

```text
Name: Koogeek-DW1-8ca86c
MAC: f5:12:09:5a:a7:92
Configuration number (cn): 1
Device ID (id): D9:2E:A0:03:F2:BF
Compatible Version (cv): 2
Global State Number (s#): 4
Status Flags (sf): The accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Sensor (Id: 10)
```

# Step 2 - unpaired identify

## used command

```bash
python -m homekit.identify -m f5:12:09:5a:a7:92
```

## result ✔

The sensor's LED flashes green.

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
python -m homekit.pair_ble -m f5:12:09:5a:a7:92 -p XXX-XX-XXX -f controller.json -a koogeek
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

The sensor's LED flashes green.

# Step 6 - get accessories

## used command

```bash
python -m homekit.get_accessories -f controller.json -a koogeek
```

## result ✔

```text
1.1003: >Unknown Service: 4AAAF961-0DEC-11E5-B939-0800200C9A66<
  1.1004:  (Time_value) >Unknown Characteristic 4AAAF962-0DEC-11E5-B939-0800200C9A66< [pr,pw]
  1.1005:  (Time_zone) >Unknown Characteristic 4AAAF963-0DEC-11E5-B939-0800200C9A66< [pr,pw]
1.7: >service<
  1.60000:  () >service-signature< [pr]
  1.8:  () >version< [pr]
1.9: >pairing<
  1.12:  () >pairing.features< [r]
  1.11:  () >pairing.pair-verify< [r,w]
  1.10:  () >pairing.pair-setup< [r,w]
  1.13:  () >pairing.pairings< [pr,pw]
1.1: >accessory-information<
  1.4:  () >manufacturer< [pr]
  1.3:  () >identify< [pw]
  1.14:  () >firmware.revision< [pr]
  1.15:  () >hardware.revision< [pr]
  1.2:  () >name< [pr]
  1.6:  () >serial-number< [pr]
  1.5:  () >model< [pr]
1.57: >battery<
  1.60:  (Charging_state) >charging-state< [pr,evc,evd]
  1.61:  (Status_low_battery) >status-lo-batt< [pr,evc,evd]
  1.59:  (Battery_level) >battery-level< [pr,evc,evd]
1.91: >contact<
  1.1002:  (One_hundred_data) >Unknown Characteristic 4AAAF966-0DEC-11E5-B939-0800200C9A66< [pr]
  1.1000:  (Today_data) >Unknown Characteristic 4AAAF964-0DEC-11E5-B939-0800200C9A66< [pr]
  1.98:  (Name) >name< [pr]
  1.1001:  (Thirday_one_day_data) >Unknown Characteristic 4AAAF965-0DEC-11E5-B939-0800200C9A66< [pr]
  1.93:  (Contact_sensor_state) >contact-state< [pr,evc,evd]
1.900: >Unknown Service: 00001530-1212-EFDE-1523-785FEABCD123<
  1.901:  (DFU Control Point) >Unknown Characteristic 00001531-1212-EFDE-1523-785FEABCD123< [pw,hd]
  1.902:  (Service Signature) >service-signature< [r,pr,hd]
```

# Step 7 - get characteristics

## used command

Query 2 characteristics (`1.59` battery level and `1.93` the sensor's state) including all optional parameters:

```bash
python -m homekit.get_characteristic -f controller.json -a koogeek -c 1.59 -c 1.93
```

## result ✔

```json
{
    "1.93": {
        "value": 1
    },
    "1.59": {
        "value": 97
    }
}
```

The value `1` means open for `1.93` here.

# Step 8 - put characteristics

## used command

Change the time zone (`1.1005`) were the plug is used to `1`.
```bash
python -m homekit.put_characteristic -f controller.json -a koogeek -c 1.1005 1
```

## result ✔

Rereading the value with this command:
```bash
python -m homekit.get_characteristic -f controller.json -a koogeek -c 1.59 -c 1.93
```

Results in:

```json
{
    "1.1005": {
        "value": 1
    }
}
```

# Step 9 - get events

**Not yet implemented with Bluetooth LE**

# Step 10 - remove pairing

## used command

```bash
python -m homekit.unpair -f controller.json -a koogeek
```

## result ✔

```text
Pairing for "koogeek" was removed.
```
