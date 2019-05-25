
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


```bash
python3 -m homekit.discover
``` 

## result ✔

```text
... 

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

...
```

# Step 2 - unpaired identify
## used command


```bash
python3 -m homekit.identify -d 19:9A:41:EA:25:CF
```

## result ✔

Eve Light Strip Flashes

# Step 3 - initialize controller storage

## used command


```bash
python3 -m homekit.init_controller_storage -f eve_light_strip
```

## result ✔

# Step 4 - pairing

## used command


```bash
python3 -m homekit.pair -d 19:9A:41:EA:25:CF -p 555-55-555 -a Eve -f eve_light_strip
```


## result ✔

```text
Pairing for "Eve" was established.
```

# Step 5 - paired identify

## used command


```bash
python3 -m homekit.identify -f eve_light_strip -a Eve
```

## result ✔

Eve Light Strip Flashes

# Step 6 - get accessories

## used command


```bash
python3 -m homekit.get_accessories -f eve_light_strip -a Eve
```

## result ✔

```text
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
```

# Step 7 - get characteristics

## used command


```bash
python3 -m homekit.get_characteristic -f eve_light_strip -a Eve -c 1.4
```

## result  ✔

```text
{
    "1.4": {
        "value": "Eve Light Strip 20EAS9901"
    }
}
```

# Step 8 - put characteristics

## used command


```bash
python3 -m homekit.put_characteristic -f eve_light_strip -a Eve -c 1.14 50
```

## result  ✔

Light lowered to 50% brightness

# Step 9 - get events

## used command

Note: Ran *python3 -m homekit.put_characteristic -f eve_light_strip -a Eve -c 1.14 100* from a seperate terminal window to get output. 


```bash
python3 -m homekit.get_events -f eve_light_strip -a Eve -c 1.14
```

## result  ✔

```text
event for 1.14: 100
^C
```


# Step 10 - remove pairing

## used command


```bash
python -m homekit.unpair -f eve_light_strip -a Eve
```

## result  ✔

```text
Pairing for "Eve" was removed.
```



