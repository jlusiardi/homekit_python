# HomeKit Python

With this code it is possible to implement either a HomeKit Accessory or simulate a
HomeKit Controller.

**Limitations**

 * This code only works with HomeKit IP Accessories. no Bluetooth LE Accessories (yet)!
 * No reaction to events whatsoever.

The code presented in this repository was created based on release R1 from 2017-06-07.

# Installation

Since the code relies on **gmpy2** for large numbers some development libraries and a compiler is required:

So for debian:
```bash
apt install libgmp-dev libmpfr-dev libmpc-dev libffi-dev build-essential python3-pip python3-dev
```

After that use **pip3** to install the package:

```bash
pip3 install --user homekit
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
  "c#": 0
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

## discover.py

This tool will list all available HomeKit IP Accessories within the local network.

Usage:
```bash
python3 -m homekit.discover
```

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
 * Some devices like the Koogeek P1EU Plug need bluetooth to set up wireless before. Use your phone 
   or the proper app to perform this
 * paired devices should not show up

## identify.py

This tool will use the Identify Routine of a HomeKit IP Accessory.

Usage:
```bash
python3 -m homekit.identify -d ${DEVICEID}
```

Output:

Either *identify succeeded.* or *identify failed* followed by a reason (see table 5-12 page 80). 
One of the most common reasons is a already paired device.

## pair.py

This tool will perform a pairing to a new accessory.

Usage:
```bash
python3 -m homekit.pair -d ${DEVICEID} -p ${SETUPCODE} -f ${PAIRINGDATAFILE} -o
```

The option `-d` specifies the device id of the accessory to pair. Can be obtained via discovery.

The option `-p` specifies the HomeKit Setup Code. Can be obtained from the accessory.

The option `-f` specifies the file that contains the pairing data.

Since the pairing data file is important, the command will exit if the file already exists.
The option `-o` will therefore overwrite the pairing data file if set.

The file with the pairing data will be required to for any additional commands to the accessory.

## list_pairings.py

This tool will perform a query to list all pairings of an accessory.

Usage:
```bash
python3 -m homekit.list_pairings -f ${PAIRINGDATAFILE}
```

The option `-f` specifies the file that contains the pairing data.

This will print information for each controller that is paired with the accessory:

```
Pairing Id: 3d65d692-90bb-41c2-9bd0-2cb7a3a5dd18
        Public Key: 0xed93c78f80e7bc8bce4fb548f1a6681284f952d37ffcb439d21f7a96c87defaf
        Permissions: 1 (admin user)
```

The information contains the pairing id, the public key of the device and permissions of the controller.

## unpair.py

This tool will remove a pairing from an accessory.

Usage:
```bash
python -m homekit.unpair -f ${PAIRINGDATAFILE} -d
```

The option `-f` specifies the file that contains the pairing data.

The option `-d` is optional and will remove the pairing data file if set.

## get_accessories.py

This tool will read the accessory attribute database.

Usage:
```bash
python3 -m homekit.get_accessories -f ${PAIRINGDATAFILE} [-o {json,compact}]
```

The option `-f` specifies the file that contains the pairing data.

The option `-o` specifies the format of the output:
 * `json` displays the result as pretty printed JSON
 * `compact` reformats the output to get more on one screen

## get_characteristic.py
This tool will read values from one or more characteristics.

Usage:
```bash
python3 -m homekit.get_characteristic -f ${PAIRINGDATAFILE} -c ${Characteristics} [-m] [-p] [-t] [-e]
```

The option `-f` specifies the file that contains the pairing data.

The option `-c` specifies the characteristics to read. The format is `<aid>.<cid>`. This 
option can be repeated to retrieve multiple characteristics with one call. 
 
The option `-m` specifies if the meta data should be read as well.

The option `-p` specifies if the permissions should be read as well.

The option `-t` specifies if the type information should be read as well.

The option `-e` specifies if the event data should be read as well.

## put_characteristic.py
This tool will write values to one characteristic.

Usage:
```bash
python3 -m homekit.put_characteristic -f ${PAIRINGDATAFILE} -c ${Characteristics} ${value}
```

The option `-f` specifies the file that contains the pairing data.

The option `-c` specifies the characteristics to change. The format is `<aid>.<cid> <value>`. This 
option can be repeated to change multiple characteristics with one call. 
 
For example, this command turns of a Koogeek P1EU Plug:
```
python3 -m homekit.put_characteristic -f koogeek.json -c 1.8 false
```

# HomeKit Accessory

# Tests

The code was tested with the following devices by the author:
 * Koogeek P1EU Plug ([Vendor](https://www.koogeek.com/smart-home-2418/p-p1eu.html))

Users have tried (and succeeded, not checked by the author) to use the following devices:
 * Ikea TRÅDFRI ([Issue #13](https://github.com/jlusiardi/homekit_python/issues/13))
 * Philips Hue ([Issue #13](https://github.com/jlusiardi/homekit_python/issues/13))
 * Leviton DH6HD-1BZ ([Issue #16](https://github.com/jlusiardi/homekit_python/issues/16))
 * Lutron Caseta (Smart Bridge 2 / [Issue #17](https://github.com/jlusiardi/homekit_python/issues/17))
 * iHome iSP5 ([Issue #18](https://github.com/jlusiardi/homekit_python/issues/18))
