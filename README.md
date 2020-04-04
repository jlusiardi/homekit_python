# HomeKit Python [![Build Status](https://travis-ci.org/jlusiardi/homekit_python.svg?branch=master)](https://travis-ci.org/jlusiardi/homekit_python) [![Coverage Status](https://coveralls.io/repos/github/jlusiardi/homekit_python/badge.svg?branch=master)](https://coveralls.io/github/jlusiardi/homekit_python?branch=master) [![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/homekit_python/community)

With this code it is possible to implement either a HomeKit Accessory or simulate a
HomeKit Controller.

The code presented in this repository was created based on release R1 from 2017-06-07.

# Contributors

 * [jc2k](https://github.com/Jc2k) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=jc2k)
 * [quarcko](https://github.com/quarcko) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=quarcko)
 * [mjg59](https://github.com/mjg59) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=mjg59)
 * [mrstegeman](https://github.com/mrstegeman) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=mrstegeman)
 * [netmanchris](https://github.com/netmanchris) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=netmanchris)
 * [limkevinkuan](https://github.com/limkevinkuan) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=limkevinkuan)
 * [tleegaard](https://github.com/tleegaard) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=tleegaard)
 * [benasse](https://github.com/benasse) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=benasse)
 * [PaulMcMillan](https://github.com/PaulMcMillan) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=PaulMcMillan)
 * [elmopl](https://github.com/lmopl) [Commits](https://github.com/jlusiardi/homekit_python/commits/master?author=elmopl)

(The contributors are not listed in any particular order!)

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

## `init_controller_storage`

This tool initializes the HomeKit controller's storage file.

Usage:
```bash
python3 -m homekit.init_controller_storage -f ${PAIRINGDATAFILE}
```

The option `-f` specifies the name of the file to contain the controller's data.

## `discover`

This tool will list all available HomeKit IP Accessories within the local network.

Usage:
```bash
python3 -m homekit.discover [-t ${TIMEOUT}] [-u] [--log ${LOGLEVEL}]
```

The option `-t` specifies the timeout for the inquiry. This is optional and 10s are the default.

The option `-u` activates a filter to show only unpaired devices. This is optional and deactivated by default.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

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

 * Some devices like the Koogeek P1EU Plug need bluetooth to set up wireless (e.g. join the wireless network) before. 
   Use your phone or the proper app to perform this
 * paired devices should not show up

## `discover_ble`

This tool will list all available HomeKit BLE Accessories within range of the Bluetooth LE device.

Usage:
```bash
python3 -m homekit.discover_ble [-t ${TIMEOUT}] [-u] [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-t` specifies the timeout for the inquiry. This is optional and 10s are the default.

The option `-u` activates a filter to show only unpaired devices. This is optional and deactivated by default.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

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

## `identify`

This tool will use the Identify Routine of a HomeKit Accessory. It has 3 modes of operation.

### identify unpaired Homekit IP Accessory

Usage:
```bash
python3 -m homekit.identify -d ${DEVICEID} [--log ${LOGLEVEL}]
```

The option `-d` specifies the device id of the accessory to identify. Can be obtained via *discovery*.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.


### identify unpaired Homekit BLE Accessory

Usage:
```bash
python3 -m homekit.identify -m ${MACADDRESS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-m` specifies the Bluetooth LE mac id of the accessory to identify. Can be obtained via *discovery_ble*.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

### identify paired Homekit Accessory

Usage:
```bash
python3 -m homekit.identify -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

## `pair`

This tool will perform a pairing to a new IP accessory.

Usage:
```bash
python3 -m homekit.pair -d ${DEVICEID} -p ${SETUPCODE} -f ${PAIRINGDATAFILE} -a ${ALIAS} [--log ${LOGLEVEL}]
```

The option `-d` specifies the device id of the accessory to pair. Can be obtained via discovery.

The option `-p` specifies the HomeKit Setup Code. Can be obtained from the accessory. This must look like `XXX-XX-XXX` 
(X is a single digit and the dashes are important).

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

The file with the pairing data will be required to send any additional commands to the accessory.

## `pair_ble`

This tool will perform a pairing to a new Bluetooth LE accessory.

Usage:
```bash
python3 -m homekit.pair -m ${MACADDRESS} -p ${SETUPCODE} -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-m` specifies the device id of the accessory to pair. Can be obtained via discovery.

The option `-p` specifies the HomeKit Setup Code. Can be obtained from the accessory.

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

The file with the pairing data will be required to send any additional commands to the accessory.

## `list_pairings`

This tool will perform a query to list all pairings of an accessory. The
controller that performs the query must be registered as `Admin`. If this is
not the case, no pairings are listed.

Usage:
```bash
python3 -m homekit.list_pairings -f ${PAIRINGDATAFILE} -a ${ALIAS} [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

This will print information for each controller that is paired with the accessory:

```
Pairing Id: 3d65d692-90bb-41c2-9bd0-2cb7a3a5dd18
        Public Key: 0xed93c78f80e7bc8bce4fb548f1a6681284f952d37ffcb439d21f7a96c87defaf
        Permissions: 1 (admin user)
```

The information contains the pairing id, the public key of the device and permissions of the controller.

## `prepare_add_remote_pairing`

This tool will prepare data required for the `add_additional_pairing` command.

Usage:
```bash
python3 -m homekit.prepare_add_remote_pairing -f ${PAIRINGDATAFILE} -a ${ALIAS} \
        [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device to be added.

The option `--log` specifies the log level for the command. This is optional. 
Use `DEBUG` to get more output.

This will print information to be fed into `homekit.add_additional_pairing` 
(via a second channel):

```
Please add this to homekit.add_additional_pairing:
    -i cec11edd-7363-42c4-8d13-aeb06b608ffc -k 0cbfd3abc377f6c3bfd3b4c119c1c5ff0c840ef1f9530e0f99c68b1f531dd66a
```

## `add_additional_pairing`

This tool is used to tell a HomeKit Accessory accept a new pairing for an 
additional controller.
 
Usage:
```bash
python3 -m homekit.add_additional_pairing -f ${PAIRINGDATAFILE} -a ${ALIAS} \
        -i ${PAIRINGID} -k ${PUBLIC_KEY} -p ${LEVEL} [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device to be added.

The option `-i` specifies the additional controller's pairing id.

The option `-k` specifies the additional controller's public key.

The option `-p` specifies the additional controller's access privileges, this can be `User` or `Admin` for a pairing
with higher privileges.

The option `--log` specifies the log level for the command. This is optional. 
Use `DEBUG` to get more output.

This will print information to be fed into `homekit.finish_add_remote_pairing` (via a second channel):

```
Please add this to homekit.finish_add_remote_pairing:
    -c BLE -i D0:CA:1E:56:13:AA -m cb:e0:b0:c9:e8:72 -k a07c471e12682b161034b91c0d016201516eb51d9bf1071b6dcf0e3be71e9269
```

## `finish_add_remote_pairing`

This tool finalizes the addition of a pairing to a HomeKit Accessory.

Usage:
```bash
python3 -m homekit.finish_add_remote_pairing -f ${PAIRINGDATAFILE} -a ${ALIAS} \
        -c ${CONNECTIONTYPE} -i ${DEVICEID} -k ${DEVICEPUBLICKEY} \
        [-m ${MACADDRESS}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device to be added.

The option `-c` specifies the type of connection for the accessory (values are
IP and BLE).

The option `-i` specifies the accessory's device id.

The option `-k` specifies the accessory's public key.

The option `-m` specifies the accessory's mac address for Bluetooth Low Energy 
accessories. This is not required for IP accessories. 

The option `--log` specifies the log level for the command. This is optional. 
Use `DEBUG` to get more output.

## `remove_pairing`

This tool will remove a pairing from an accessory.

Usage:
```bash
python -m homekit.remove_pairing -f ${PAIRINGDATAFILE} -a ${ALIAS} [-i ${PAIRINGID}] [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-i` specifies the controller pairing id to remove. This is optional. If left out, the calling controller's
pairing id is used and the controller looses the ability to controll the device. See the output of `list_pairings` 
how to get the controller's pairing id. *Important*: this is not the accessory's device id.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

## `get_accessories`

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

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

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

## `get_characteristic`
This tool will read values from one or more characteristics.

Usage:
```bash
python3 -m homekit.get_characteristic -f ${PAIRINGDATAFILE} -a ${ALIAS} -c ${CHARACTERISTICS} [-m] [-p] [-t] [-e] \
                                     [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-c` specifies the characteristics to read. The format is `<aid>.<cid>`. This option can be repeated to 
retrieve multiple characteristics with one call (e.g. `-c 1.9 -c 1.8`). 
 
The option `-m` specifies if the meta data should be read as well.

The option `-p` specifies if the permissions should be read as well.

The option `-t` specifies if the type information should be read as well.

The option `-e` specifies if the event data should be read as well.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.

The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

For example, this command reads 2 characteristics of a Koogeek P1EU Plug:
```
python3 -m homekit.get_characteristic -f koogeek.json -a koogeek -c 1.8 -c 1.9
```

The result will be a json with data for each requested characteristic:
```json
{
    "1.8": {
        "value": false
    },
    "1.9": {
        "value": true
    }
}
```

## `put_characteristic`
This tool will write values to one or more characteristics.

Usage:
```bash
python3 -m homekit.put_characteristic -f ${PAIRINGDATAFILE} -a ${ALIAS} -c ${Characteristics} ${value} \
                                     [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-c` specifies the characteristics to change. The format is `<aid>.<cid> <value>`. This option can be 
repeated to change multiple characteristics with one call  (e.g. `-c 1.9 On -c 1.8 22.3`) . 
 
The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is only 
used if the paired device is using Bluetooth LE.
 
The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

For example, this command turns of a Koogeek P1EU Plug:
```
python3 -m homekit.put_characteristic -f koogeek.json -a koogeek -c 1.8 false
```

No output is given on successful operation or a error message is displayed.

## `get_events`

**!!Not yet implemented for Bluetooth LE Accessories!!**

This tool will register with an accessory and listen to the events send back from it.

Usage
```bash
python3 -m homekit.get_events -f ${PAIRINGDATAFILE} -a ${ALIAS} -c ${Characteristics} \
                             [--adapter ${ADAPTER}] [--log ${LOGLEVEL}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-a` specifies the alias for the device.

The option `-c` specifies the characteristics to change. The format is `<aid>.<cid>`. This 
option can be repeated to listen to multiple characteristics with one call.

The option `--adapter` specifies which Bluetooth device to use. This is optional and `hci0` is the default and is 
only used if the paired device is using Bluetooth LE.
 
The option `--log` specifies the log level for the command. This is optional. Use `DEBUG` to get more output.

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

## `debug_proxy`

This can be used to debug and trace the communication of a controller and a accessory. The communication will be 
logged to standard out. 

It works as follows:
  1) create a pairing with the accessory under test and store it in `pairingdata.json` under alias `target` (The
      names are free to choose)
  2) create `server.json` as described under creating [HomeKit Accessory](#homekit-accessory). **Important**: the 
      `category` heare must match the category of the proxied accessory
  3) run the `debug_proxy` like `python3 -m homekit.debug_proxy --client-data pairingdata.json --alias target --server-data server.json`
  4) inspect the log and analyse the data. Right to the beginning, the list of proxied characteristics is logged and 
      the get and set value calls come later:
```text
2020-03-15 18:34:09,725 debug_proxy.py:0199 INFO %<------ creating proxy ------
2020-03-15 18:34:09,725 debug_proxy.py:0204 INFO accessory with aid=1
2020-03-15 18:34:09,725 debug_proxy.py:0212 INFO   1.1: >accessory-information< (0000003E-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,725 debug_proxy.py:0225 INFO     1.5: Logi Circle >name< (00000023-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,725 debug_proxy.py:0225 INFO     1.2: None >identify< (00000014-0000-1000-8000-0026BB765291) [pw] bool
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.3: Logitech >manufacturer< (00000020-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.4: V-R0008 >model< (00000021-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.6: 1933CDC04478 >serial-number< (00000030-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.7: 5.6.49 >firmware.revision< (00000052-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.9: >camera-rtp-stream-management< (00000110-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.10: AQEC >streaming-status< (00000120-0000-1000-8000-0026BB765291) [pr,ev] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.11: AREBAQACDAEBAQIBAgMBAAQBAA== >supported-video-stream-configuration< (00000114-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.12: AQ8BAgMAAgkBAQECAQADAQECAQA= >supported-audio-configuration< (00000115-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.13: AgEA >supported-rtp-configuration< (00000116-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.14:  >setup-endpoints< (00000118-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.15:  >selected-rtp-stream-configuration< (00000117-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.16: >camera-rtp-stream-management< (00000110-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.17: AQEA >streaming-status< (00000120-0000-1000-8000-0026BB765291) [pr,ev] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.18: AVoBAQACDAEBAQIBAgMBAAQBAAMLAQIABQIC0AIDAR7/AAMLAQKAAgICaAEDAR7/AAMLAQIABAICAAMDAR7/AAMLAQKAAgIC4AEDAR7/AAMLAQJAAQIC8AADAR4= >supported-video-stream-configuration< (00000114-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.19: AQ8BAgMAAgkBAQECAQADAQECAQA= >supported-audio-configuration< (00000115-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.20: AgEA >supported-rtp-configuration< (00000116-0000-1000-8000-0026BB765291) [pr] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.21: ARA+sNO7kUtMIYyHgEWPvo4KAgEAAxwBAQACDzE5Mi4xNjguMTc4LjIxMgMCKfcEAq7iBCUBAQACEB1niC5AAAcwwBb7IO4e7oYDDmQylh7GJdhOjZ5Yrq67BSUBAQACEBcDMU3e6vrRmHl0Ze2NrrADDuPZEzuug4WjLKreG4PUBgQEV+ZuBwQzoa0p >setup-endpoints< (00000118-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.22:  >selected-rtp-stream-configuration< (00000117-0000-1000-8000-0026BB765291) [pr,pw] tlv8
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.34: >microphone< (00000112-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.35: False >mute< (0000011A-0000-1000-8000-0026BB765291) [pr,pw,ev] bool
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.37: >speaker< (00000113-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.38: False >mute< (0000011A-0000-1000-8000-0026BB765291) [pr,pw,ev] bool
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.40: >motion< (00000085-0000-1000-8000-0026BB765291)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.41: False >motion-detected< (00000022-0000-1000-8000-0026BB765291) [pr,ev] bool
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.42: Logi Circle Motion Detector >name< (00000023-0000-1000-8000-0026BB765291) [pr] string
2020-03-15 18:34:09,726 debug_proxy.py:0212 INFO   1.400: >Unknown Service: 5C20E6E7-0B8B-43C4-9C5F-CA0DE8A7BCD2< (5C20E6E7-0B8B-43C4-9C5F-CA0DE8A7BCD2)
2020-03-15 18:34:09,726 debug_proxy.py:0225 INFO     1.401: AQECAgEA >Unknown Characteristic 30B32518-5C01-4470-9C9F-7AEB89E93419< (30B32518-5C01-4470-9C9F-7AEB89E93419) [pr,ev] tlv8
2020-03-15 18:34:09,727 debug_proxy.py:0225 INFO     1.402: EQYAAAAAAAA= >Unknown Characteristic F1E5CE1A-2185-4798-BDF4-86A6557CBA54< (F1E5CE1A-2185-4798-BDF4-86A6557CBA54) [pr] tlv8
2020-03-15 18:34:09,727 debug_proxy.py:0225 INFO     1.403: None >Unknown Characteristic B45787D2-EE61-471B-9213-AEDBFC67186D< (B45787D2-EE61-471B-9213-AEDBFC67186D) [pw] tlv8
2020-03-15 18:34:09,727 debug_proxy.py:0238 INFO %<------ finished creating proxy ------

...

020-03-15 18:37:04,292 accessoryserver.py:1227 INFO "GET /characteristics?id=1.20,1.18,1.19 HTTP/1.1" 207 -
2020-03-15 18:37:04,437 debug_proxy.py:0088 INFO loading module setup_endpoints for type 00000118-0000-1000-8000-0026BB765291
2020-03-15 18:37:04,440 debug_proxy.py:0117 INFO write value to 1.21 (type 00000118-0000-1000-8000-0026BB765291 / setup-endpoints): 
[
  <SetupEndpointsKeys.SESSION_ID, b'n\x17\x8dh\xed\x90M8\x9d\xb7\\\x9b\x19`\x0bt'>,
  <SetupEndpointsKeys.ADDRESS, [
    <ControllerAddressKeys.IP_ADDRESS_VERSION, IPVersionValues.IPV4>,
    <ControllerAddressKeys.IP_ADDRESS, 192.168.178.222>,
    <ControllerAddressKeys.VIDEO_RTP_PORT, 58833>,
    <ControllerAddressKeys.AUDIO_RTP_PORT, 54612>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, [
    <SrtpParameterKeys.SRTP_MASTER_KEY, b'\x88\x81\xa6\xdd=\xe0\xd4,\x11\x89\x96\x89\xd06\xd1\xf7'>,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b's\xd4\x17\xbeJ\xee\xcf\xde\x170\xcd\x98qk'>,
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, [
    <SrtpParameterKeys.SRTP_MASTER_KEY, b"I\x8c\xb5\xf5up'w\xa8\x0b\x9b\xe8\th|8">,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b'Yg\x85z\xaa&\x809\xc2\x9d\x05`\xe6\xaf'>,
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
  ]>,
]
2020-03-15 18:37:04,441 accessoryserver.py:1227 INFO "PUT /characteristics HTTP/1.1" 204 -
2020-03-15 18:37:04,485 debug_proxy.py:0097 INFO got decoder for 00000118-0000-1000-8000-0026BB765291 from cache
2020-03-15 18:37:04,485 debug_proxy.py:0117 INFO get value from 1.21 (type 00000118-0000-1000-8000-0026BB765291 / setup-endpoints): 
[
  <SetupEndpointsKeys.SESSION_ID, b'n\x17\x8dh\xed\x90M8\x9d\xb7\\\x9b\x19`\x0bt'>,
  <SetupEndpointsKeys.STATUS, EndpointStatusValues.SUCCESS>,
  <SetupEndpointsKeys.ADDRESS, [
    <ControllerAddressKeys.IP_ADDRESS_VERSION, IPVersionValues.IPV4>,
    <ControllerAddressKeys.IP_ADDRESS, 192.168.178.212>,
    <ControllerAddressKeys.VIDEO_RTP_PORT, 58833>,
    <ControllerAddressKeys.AUDIO_RTP_PORT, 54612>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_VIDEO, [
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
    <SrtpParameterKeys.SRTP_MASTER_KEY, b'\x14\xfc\xa9\x12\x03\x89\x19\xfdcMC\xd4hI\xd6T'>,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b'\x97\x95\xd9\xc2#\x84\xfd\xa6\x83\xba\xf2I\xcf\xed'>,
  ]>,
  <SetupEndpointsKeys.SRTP_PARAMETERS_FOR_AUDIO, [
    <SrtpParameterKeys.SRTP_CRYPTO_SUITE, CameraSRTPCryptoSuiteValues.AES_CM_128_HMAC_SHA1_80>,
    <SrtpParameterKeys.SRTP_MASTER_KEY, b'h\xc7\xf6\x8f\x8d\xb9\xc1[~\xdc\x88\x18X\xd78]'>,
    <SrtpParameterKeys.SRTP_MASTER_SALT, b'\xb0\x8f\xbd\x95)\x9b\xdd\x97\xc0\xe1\x14JX4'>,
  ]>,
  <SetupEndpointsKeys.VIDEO_RTP_SSRC, b'&M\xd0w'>,
  <SetupEndpointsKeys.AUDIO_RTP_SSRC, b'\xa7ik\x07'>,
]
2020-03-15 18:37:04,485 accessoryserver.py:1227 INFO "GET /characteristics?id=1.21 HTTP/1.1" 200 -
2020-03-15 18:37:06,118 debug_proxy.py:0088 INFO loading module selected_rtp_stream_configuration for type 00000117-0000-1000-8000-0026BB765291

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
