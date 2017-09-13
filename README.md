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
  "unsuccessful_tries": 0
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
./discover.py
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

## identify.py

This tool will use the Identify Routine of a HomeKit IP Accessory.

Usage:
```bash
./identify.py -d ${DEVICEID}
```

Output:

Either *identify succeeded.* or *identify failed* followed by a reason (see table 5-12 page 80). 

## pair.py

This tool will perform a paring to a new accessory.

Usage:
```bash
./pair.py -d ${DEVICEID} -p ${SETUPCODE} -f ${PAIRINGDATAFILE}
```

The file with the pairing data will be required to for any additional commands to the accessory.

## get_accessories.py

This tool will read the accessory attribute database.

Usage:
```bash
./get_accessories.py -f ${PAIRINGDATAFILE} [-o {json,compact}]
```

The option `-o` specifies the format of the output:
 * `json` displays the result as pretty printed JSON
 * `compact` reformats the output to get more on one screen

## get_characteristics.py
This tool will read values from one or more characteristics.

Usage:
```bash
./get_characteristics.py -f ${PAIRINGDATAFILE} -c {Characteristics} [-m] [-p] [-t] [-e]
```

The option `-c` specifies the characteristics to read. The format is `<aid>.<cid>[,<aid>.<cid>]*`.
 
The option `-m` specifies if the meta data should be read as well.

The option `-p` specifies if the permissions should be read as well.

The option `-t` specifies if the type information should be read as well.

The option `-e` specifies if the event data should be read as well.

# HomeKit Accessory

# Tests

The code was tested with the following devices:
 * Koogeek P1EU Plug ([Vendor](https://www.koogeek.com/smart-home-2418/p-p1eu.html))
