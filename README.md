# HomeKit Python [![Build Status](https://travis-ci.org/jlusiardi/homekit_python.svg?branch=master)](https://travis-ci.org/jlusiardi/homekit_python) [![Coverage Status](https://coveralls.io/repos/github/jlusiardi/homekit_python/badge.svg?branch=master)](https://coveralls.io/github/jlusiardi/homekit_python?branch=master) [![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/homekit_python/community)

With this code it is possible to implement either a HomeKit Accessory or simulate a
HomeKit Controller.

The code presented in this repository was created based on release R1 from 2017-06-07.

# Contributors

 * [jc2k](https://github.com/Jc2k) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=jc2k)
 * [quarcko](https://github.com/quarcko) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=quarcko)
 * [mjg59](https://github.com/mjg59) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=mjg59)
 * [mrstegeman](https://github.com/mrstegeman) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=mrstegeman)

# Installation

## Installation for IP based accessories

Simply use **pip3** to install the package:

```bash
pip3 install --user homekit[IP]
```

This installation only for IP based accessories can be done without any operating system level installations and should 
also work on operating systems other than linux (Mac OS X, Windows, ...).  

## Installation for Bluetooth LE based accessories

This variant requires some packages on operating systems for the access onto Bluetooth LE via dbus. These can be 
installed on Debian based operating systems via:

```bash
apt install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 libdbus-1-dev
```

After that, using **pip3** is sufficient again:

```bash
pip3 install --user homekit[BLE]
```

## Installation for both type of accessories

In this case, install the packages for your operating system and afterwards use **pip3**:

```bash
pip3 install --user homekit[IP,BLE]
```

# HomeKit Accessory
This package helps in creating a custom HomeKit Accessory.

The demonstration uses this JSON in `~/.homekit/demoserver.json`: 
```json
{
  "name": "DemoAccessory",
  "host_ip": "$YOUR IP",
  "host_port": 8080,
  "accessory_pairing_id": "12:00:00:00:00:00",
  "accessory_pin": "031-45-154",
  "peers": {},
  "unsuccessful_tries": 0,
  "c#": 0,
  "category": "Lightbulb"

}
```

Now let's spawn a simple light bulb accessory as demonstration:

```python
#!/usr/bin/env python3

import os.path

from homekit import HomeKitServer
from homekit.model import Accessory, LightBulbService


if __name__ == '__main__':
    try:
        httpd = HomeKitServer(os.path.expanduser('~/.homekit/demoserver.json'))

        accessory = Accessory('Licht')
        lightService = LightBulbService()
        accessory.services.append(lightService)
        httpd.accessories.add_accessory(accessory)

        httpd.publish_device()
        print('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('unpublish device')
        httpd.unpublish_device()
```

If everything went properly, you should be able to add this accessory to your home on your iOS device.

# HomeKit Controller

The following tools help to access HomeKit Accessories.

## init_controller_storage

This tool initializes the HomeKit controller's storage file.

Usage:
```bash
python3 -m homekit.init_controller_storage
```

The option `-f` specifies the name of the file to contain the controller's data.

## discover

This tool will list all available HomeKit IP Accessories within the local network.

Usage:
```bash
python3 -m homekit.discover [-t ${TIMEOUT}] [--log ${LOGLEVEL}]
```

The option `-t` specifies the timeout for the inquiry. This is optional and 10s are the default.

The option `--log` specifies the loglevel for the command. Use `DEBUG` to get more output.

Output:
```
Name: smarthomebridge3._hap._tcp.local.
Url: http://192.168.178.21:51827
Configuration number (c#): 2
Feature Flags (ff): Paired (Flag: 0)
Device ID (id): 12:34:56:78:90:05
Model Name (md): Bridge
Protocol Version (pv): 1.0
State Number (s#): 1
Status Flags (sf): 0
Category Identifier (ci): Other (Id: 1)
```
Hints: 
 * Some devices like the Koogeek P1EU Plug need bluetooth to set up wireless (e.g. join the wireless network) before. Use your phone 
   or the proper app to perform this
 * paired devices should not show up

## discover_ble

This tool will list all available HomeKit BLE Accessories within range of the Bluetooth LE device.

Usage:
```bash
python3 -m homekit.discover_ble [-t ${TIMEOUT}] [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-t` specifies the timeout for the inquiry. This is optional and 10s are the default.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

Output:
```
Name: Koogeek-DW1-8ca86c
MAC: c6:cc:4d:a7:7c:5e
Configuration number (cn): 1
Device ID (id): B8:D1:29:61:A1:B0
Compatible Version (cv): 2
Global State Number (s#): 2
Status Flags (sf): The accessory has been paired with a controllers. (Flag: 0)
Category Identifier (ci): Sensor (Id: 10)
```

## identify

This tool will use the Identify Routine of a HomeKit Accessory. It has 3 modes of operation.

### identify unpaired Homekit IP Accessory

Usage:
```bash
python3 -m homekit.identify -d ${DEVICEID} [--log ${LOGLEVEL}]
```

The option `-d` specifies the device id of the accessory to identify. Can be obtained via *discovery*.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.


### identify unpaired Homekit BLE Accessory

Usage:
```bash
python3 -m homekit.identify -m ${MACADDRESS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-m` specifies the Bluetooth LE mac id of the accessory to identify. Can be obtained via *discovery_ble*.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default.

### identify paired Homekit Accessory

Usage:
```bash
python3 -m homekit.identify -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

## pair

This tool will perform a pairing to a new IP accessory.

Usage:
```bash
python3 -m homekit.pair -d ${DEVICEID} -p ${SETUPCODE} -f ${PAIRINGDATAFILE} -a ${ALIAS} [--log ${LOGLEVEL}]
```

The option `-d` specifies the device id of the accessory to pair. Can be obtained via discovery.

The option `-p` specifies the HomeKit Setup Code. Can be obtained from the accessory. This must look like `XXX-XX-XXX` (X is a single digit and the dashes are important).

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

The file with the pairing data will be required to send any additional commands to the accessory.

## pair_ble

This tool will perform a pairing to a new Bluetooth LE accessory.

Usage:
```bash
python3 -m homekit.pair -m ${MACADDRESS} -p ${SETUPCODE} -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-m` specifies the device id of the accessory to pair. Can be obtained via discovery.

The option `-p` specifies the HomeKit Setup Code. Can be obtained from the accessory.

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

The file with the pairing data will be required to send any additional commands to the accessory.

## list_pairings

This tool will perform a query to list all pairings of an accessory.

Usage:
```bash
python3 -m homekit.list_pairings -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

This will print information for each controller that is paired with the accessory:

```
Pairing Id: 3d65d692-90bb-41c2-9bd0-2cb7a3a5dd18
        Public Key: 0xed93c78f80e7bc8bce4fb548f1a6681284f952d37ffcb439d21f7a96c87defaf
        Permissions: 1 (admin user)
```

The information contains the pairing id, the public key of the device and permissions of the controller.

## unpair

This tool will remove a pairing from an accessory.

Usage:
```bash
python -m homekit.unpair -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

## get_accessories

This tool will read the accessory attribute database.

Usage:
```bash
python3 -m homekit.get_accessories -f ${PAIRINGDATAFILE} -a ${ALIAS} [-o {json,compact}] [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-o` specifies the format of the output:
 * `json` displays the result as pretty printed JSON
 * `compact` reformats the output to get more on one screen

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

Using the `compact` output the result will look like:
```
1.1: >accessory-information<
  1.2: Koogeek-P1-770D90 () >name< [pr]
  1.3: Koogeek () >manufacturer< [pr]
  1.4: P1EU () >model< [pr]
  1.5: EUCP031715001435 () >serial-number< [pr]
  1.6:  () >identify< [pw]
  1.37: 1.2.9 () >firmware.revision< [pr]
1.7: >outlet<
  1.8: False () >on< [pr,pw,ev]
  1.9: True () >outlet-in-use< [pr,ev]
  1.10: Outlet () >name< [pr]
```

## get_characteristic
This tool will read values from one or more characteristics.

Usage:
```bash
python3 -m homekit.get_characteristic -f ${PAIRINGDATAFILE} -a ${ALIAS} -c ${CHARACTERISTICS} [-m] [-p] [-t] [-e] [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-c` specifies the characteristics to read. The format is `<aid>.<cid>`. This option can be repeated to retrieve multiple characteristics with one call (e.g. `-c 1.9 -c 1.8`). 
 
The option `-m` specifies if the meta data should be read as well.

The option `-p` specifies if the permissions should be read as well.

The option `-t` specifies if the type information should be read as well.

The option `-e` specifies if the event data should be read as well.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.

The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

For example, this command reads 2 characteristics of a Koogeek P1EU Plug:
```
python3 -m homekit.get_characteristic -f koogeek.json -a koogeek -c 1.8 -c 1.9
```

The result will be a json with data for each requested characteristic:
```
{
    "1.8": {
        "value": false
    },
    "1.9": {
        "value": true
    }
}
```

## put_characteristic
This tool will write values to one or more characteristics.

Usage:
```bash
python3 -m homekit.put_characteristic -f ${PAIRINGDATAFILE} -a ${ALIAS} -c ${Characteristics} ${value}[--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-c` specifies the characteristics to change. The format is `<aid>.<cid> <value>`. This option can be repeated to change multiple characteristics with one call  (e.g. `-c 1.9 On -c 1.8 22.3`) . 
 
The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.
 
The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

For example, this command turns of a Koogeek P1EU Plug:
```
python3 -m homekit.put_characteristic -f koogeek.json -a koogeek -c 1.8 false
```

No output is given on successful operation or a error message is displayed.

## get_events

**!!Not yet implemented for Bluetooth LE Accessories!!**

This tool will register with an accessory and listen to the events send back from it.

Usage
```bash
python3 -m homekit.get_events -f ${PAIRINGDATAFILE} -a ${ALIAS} -c ${Characteristics} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-c` specifies the characteristics to change. The format is `<aid>.<cid>`. This 
option can be repeated to listen to multiple characteristics with one call.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only used if the paired device is using Bluetooth LE.
 
The option `--log` specifies the loglevel for the command. This is optional. Use `DEBUG` to get more output.

For example, you can listen to characteristics 1.8 (on characteristic), 1.22 (1 REALTIME_ENERGY) and 
1.23 (2 CURRENT_HOUR_DATA) of the Koogeek P1EU Plug with:
```bash
python3 -m homekit.get_events -f koogeek.json -a koogeek -c 1.8 -c 1.22 -c 1.23
```
This results in
```
event for 1.8: True
event for 1.22: 6.0
event for 1.23: 0.01666
event for 1.22: 17.0
event for 1.23: 0.06388
event for 1.23: 0.11111
event for 1.22: 18.0
event for 1.23: 0.16111
event for 1.8: False
```

# HomeKit Accessory

# Devices Reported to work

The code was tested with the following devices by the author:
 * Koogeek P1EU Plug (IP) ([Vendor](https://www.koogeek.com/smart-home-2418/p-p1eu.html))
 * Koogeek DW1 (BLE)  ([Vendor](https://www.koogeek.com/p-dw1.html))
 * OSRAM SMART+ Classic E27 Multicolor (BLE) ([Vendor](https://smartplus.ledvance.de/produkte/innenbeleuchtung/index.jsp#_m507__2_9_col___image__video___rest_col___text_20))

Users have tried (and succeeded, not checked by the author) to use the following devices:
 * Ikea TRÅDFRI (IP) ([Issue #13](https://github.com/jlusiardi/homekit_python/issues/13))
 * Philips Hue (IP) ([Issue #13](https://github.com/jlusiardi/homekit_python/issues/13))
 * Leviton DH6HD-1BZ (IP) ([Issue #16](https://github.com/jlusiardi/homekit_python/issues/16))
 * Lutron Caseta (IP) (Smart Bridge 2 / [Issue #17](https://github.com/jlusiardi/homekit_python/issues/17))
 * iHome iSP5 (IP) ([Issue #18](https://github.com/jlusiardi/homekit_python/issues/18))
 * Xiaomi Mi Bedside Lamp 2 (IP) ([Issue #116](https://github.com/jlusiardi/homekit_python/issues/116))
