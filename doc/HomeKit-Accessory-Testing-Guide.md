This describes how to report a working HomeKit Accessory.

**Important**
Please inform yourself how to reset the HomeKit Accessory under test to factory settings just in case anything goes wrong with the testing.

# Step 1) - discovery

[Documentation for the discover command](https://github.com/jlusiardi/homekit_python#discover)

The first step is to check whether the accessory can be discovered:

```bash
python3 -m homekit.discover
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
python3 -m homekit.identitfy -d  ${Device ID} 
```

# Step 3) - initialize controller storage (optional)

[Documentation for the init_controller_storage command](https://github.com/jlusiardi/homekit_python#init_controller_storage)

Use this command to create a new storage for the controller's data. Currently this is basically a file containing an empty JSON hash (`{}`).

# Step 4) - pairing

[Documentation for the pair command](https://github.com/jlusiardi/homekit_python#pair)

The next step is to pair the accessory under test. Execute this command:

```bash
python3 -m homekit.pair -d  ${Device ID} -p ${Device Setup Code} -f test_report.json -a deviceUnderTest
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

# Step 8) - put characteristics

# Step 9) - get events

# Step XXX) - remove pairing


