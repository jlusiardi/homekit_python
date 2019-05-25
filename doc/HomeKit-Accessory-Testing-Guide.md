This describes how to report a working HomeKit Accessory.

**Important**
Please inform yourself how to reset the HomeKit Accessory under test to factory settings just in case anything goes wrong with the testing.

# Required Information

Please give detailed information on which device was tested. This should whenever possible include:
 * device manufacturer (can be taken from `accessory-information.manufacturer`)
 * device model (can be taken from `accessory-information.model`)
 * device firmware version (can be taken from `accessory-information.firmware.revision`)
 * device hardware version (can be taken from `accessory-information.hardware.revision`)
 * type of used communication channel (Bluetooth LE or IP via Wifi etc.)
 * the version of the homekit library that was used to perform the test

# Step 1) - discovery / disovery_ble

[Documentation for the discover command](https://github.com/jlusiardi/homekit_python#discover)

[Documentation for the discover command](https://github.com/jlusiardi/homekit_python#discover_ble)

The first step is to check whether the accessory can be discovered:

For IP based accessories:
```bash
python3 -m homekit.discover
```
For Bluetooth LE based accessories:
```bash
python3 -m homekit.discover_ble
```

Try to identify the block that corresponds to your accessory under test and attach the lines. This should look like this:
```
Name: Testsensor1._hap._tcp.local.
Url: http_impl://192.168.178.219:5556
Configuration number (c#): 1
Feature Flags (ff): Paired (Flag: 0)
Device ID (id): ED:DF:7E:2E:E4:69
Model Name (md): MyBreadBoardSensor
Protocol Version (pv): 1.0
State Number (s#): 1
Status Flags (sf): 1
Category Identifier (ci): Sensor (Id: 10)
```

Note down the Device ID for further steps.

# Step 2) - unpaired identify (optional)

[Documentation for the identify command](https://github.com/jlusiardi/homekit_python#identify)

This step is optional since no output should be provided. Take a short note if the accessory under test reacts to the call as it does with the iOS app.

```bash
python3 -m homekit.identify -d  ${Device ID} 
```

# Step 3) - initialize controller storage (optional)

[Documentation for the init_controller_storage command](https://github.com/jlusiardi/homekit_python#init_controller_storage)

Use this command to create a new storage for the controller's data. Currently this is basically a file containing an empty JSON hash (`{}`).

# Step 4) - pairing / pairing_ble

[Documentation for the pair command](https://github.com/jlusiardi/homekit_python#pair)

[Documentation for the pair command](https://github.com/jlusiardi/homekit_python#pair_ble)

The next step is to pair the accessory under test. Execute this command:

For IP based accessories:
```bash
python3 -m homekit.pair -d  ${Device ID} -p ${Device Setup Code} -f test_report.json -a deviceUnderTest
```
For Bluetooth LE based accessories:
```bash
python -m homekit.pair_ble -m ${Device MAC} -p ${Device Setup Code} -f test_report.json -a deviceUnderTest
```

The output should be:

```
Pairing for deviceUnderTest was established.
```

# Step 5) - paired identify (optional)

[Documentation for the identitfy command](https://github.com/jlusiardi/homekit_python#identitfy)

This step is optional since no output should be provided. Take a short note if the accessory under test reacts to the call as it does with the iOS app.

```bash
python3 -m homekit.identitfy -f test_report.json -a deviceUnderTest
```

# Step 6) - get accessories 

[Documentation for the get_accessories command](https://github.com/jlusiardi/homekit_python#get_accessories)

This step checks for the ability on how to read out the available accessories.

```bash
python3 -m homekit.get_accessories -f test_report.json -a deviceUnderTest
```

The example below is from a slightly patched firmware build from the demos of [maximkulkin/esp-homekit](https://github.com/maximkulkin/esp-homekit). 
Your output should look similar:
```
1.1: >accessory-information<
  1.2: Testsensor1 (Name) >name< [pr]
  1.3: JL (Manufacturer) >manufacturer< [pr]
  1.4: 0012347 (Serial Number) >serial-number< [pr]
  1.5: MyBreadBoardSensor (Model) >model< [pr]
  1.6: 0.1 (Firmware Revision) >firmware.revision< [pr]
  1.7:  (Identify) >identify< [pw]
1.8: >temperature<
  1.9: Temperature Sensor (Name) >name< [pr]
  1.10: 30.1000003814697 (Current Temperature) >temperature.current< [pr,ev]
1.11: >humidity<
  1.12: Humidity Sensor (Name) >name< [pr]
  1.13: 28.7999992370605 (Current Relative Humidity) >relative-humidity.current< [pr,ev]
```

# Step 7) - get characteristics

[Documentation for the get_characteristic command](https://github.com/jlusiardi/homekit_python#get_characteristic)

This step checks if characteristics can be read selectivly. For the example from above to read the current humidity and temperature:

```bash
python3 -m homekit.get_characteristic -f test_report.json -a deviceUnderTest -c 1.13 -c 1.10 
```

This should return some json like:
```json
{
    "1.13": {
        "value": 28.7999992370605
    },
    "1.10": {
        "value": 30.1000003814697
    }
}
```

**Note**
It might not be possible to read all characteristics with all possible options (`-m`, `-p`, `-t` and `-e`). So it is best to take the essential characteristics for the accessory and only work with them.


# Step 8) - put characteristics

[Documentation for the put_characteristic command](https://github.com/jlusiardi/homekit_python#put_characteristic)

This step tries to manipulate one or more characteristic of an accessory.

```bash
python3 -m homekit.put_characteristic -f test_report.json -a deviceUnderTest -c 23.42 On
```

There should be no output generated and the accessory should react accordingly.

**Note**
Skip this step, if no characteristic is writable (**pr**) in the listing of `get_accessories`.

# Step 9) - get events

[Documentation for the get_events command](https://github.com/jlusiardi/homekit_python#get_events)

This step tests the capabilities to receive event notifications from accessories. For our example, this will wait for either 5 events or 5 seconds: 

```bash
python3 -m homekit.get_events -f test_report.json -a deviceUnderTest -e 5 -s 5 -c 1.13 -c 1.10 
```

One line should be printed for every event:
```
event for 1.13: 28.7999992370605
event for 1.10: 30.1000003814697
event for 1.13: 28.8999992370605
event for 1.10: 30.0000003814697
```

**Note**
Skip this step, if no characteristic offers events (**ev**) in the listing of `get_accessories`.

# Step 10) - remove pairing

[Documentation for the unpair command](https://github.com/jlusiardi/homekit_python#unpair)

Finally the pairing to the accessory is removed. 

```bash
python3 -m homekit.unpair -f test_report.json -a deviceUnderTest
```

This should result in:
```
Pairing for "deviceUnderTest" was removed.
```



