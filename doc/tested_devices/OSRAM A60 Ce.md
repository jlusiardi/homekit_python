# Device Name: Osram A60 Ce

Important Information:
 * device manufacturer : LEDVANCE
 * device model : Ledvance A60 C
 * device firmware version : 01.00.06
 * device hardware version : not available
 * communication channel : Bluetooth LE
 * version of *homekit* library: 0.14.0

[Product Page](https://smartplus.ledvance.com/products/indoor-lighting/index.jsp)

# Step 1 - discovery

## used command

```bash
python -m homekit.discover_ble
```

## result ✔

```text
Name: A60 Ce
MAC: fd:3c:d4:13:02:59
Configuration number (cn): 1
Device ID (id): 08:49:9B:B2:A0:96
Compatible Version (cv): 2
Global State Number (s#): 1
Status Flags (sf): The accessory has not been paired with any controllers. (Flag: 1)
Category Identifier (ci): Lightbulb (Id: 5)
```

# Step 2 - unpaired identify

## used command

```bash
python -m homekit.identify -m fd:3c:d4:13:02:59
```

## result ✔

The light bulb flashes in white.

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
python -m homekit.pair_ble -m fd:3c:d4:13:02:59 -p XXX-XX-XXX -f controller.json -a a60
```

## result ✔

```text
Pairing for "a60" was established.
```

# Step 5 - paired identify

## used command

```bash
python -m homekit.identify -f controller.json -a a60
```

## result ✔

The light bulb flashes in white.

# Step 6 - get accessories

## used command

```bash
python -m homekit.get_accessories -f controller.json -a a60
```

## result ✔

```text
1.1000: >Unknown Service: B0733E83-8434-4C00-A344-25D1C982A0EF<
  1.1001:  () >service-signature< [r]
  1.1003:  () >Unknown Characteristic B2FD7F2D-EAD3-4F17-B16C-202EC758C697< [pr,pw]
  1.1002:  () >Unknown Characteristic B176BD7F-4148-47BD-A6C6-9D0796E96183< [pr,pw,evc,evd]
  1.1004:  () >Unknown Characteristic B31259A5-9ACC-45C2-838A-956F57825196< [pr]
1.30: >pairing<
  1.31:  () >pairing.pair-setup< [r,w]
  1.32:  () >pairing.pair-verify< [r,w]
  1.33:  () >pairing.features< [r]
  1.34:  () >pairing.pairings< [pr,pw]
1.1: >accessory-information<
  1.2:  () >identify< [w]
  1.7:  () >firmware.revision< [pr]
  1.5:  () >name< [pr]
  1.6:  () >serial-number< [pr]
  1.4:  () >model< [pr]
  1.3:  () >manufacturer< [pr]
1.20: >lightbulb<
  1.16:  () >name< [pr]
  1.23:  () >brightness< [pr,pw,evc,evd]
  1.19:  () >service-signature< [r]
  1.15:  () >on< [pr,pw,evc,evd]
  1.25:  () >saturation< [pr,pw,evc,evd]
  1.24:  () >hue< [pr,pw,evc,evd]
1.10: >service<
  1.11:  () >version< [pr]
```

# Step 7 - get characteristics

## used command

Query whether the bulb is on:

```bash
python -m homekit.get_characteristic -f controller.json -a a60 -c 1.15
```

## result ✔

The bulb is turned on:

```json
{
    "1.15": {
        "value": true
    }
}

```

# Step 8 - put characteristics

## used command

Turn off the bulb: 
```bash
python -m homekit.put_characteristic -f controller.json -a a60 -c 1.15 off
```

## result ✔

The bulb turns off.

# Step 9 - get events

**Not yet implemented with Bluetooth LE**

# Step 10 - remove pairing

## used command

```bash
python -m homekit.unpair -f controller.json -a a60
```

## result ✔

```text
Pairing for "a60" was removed.
```
