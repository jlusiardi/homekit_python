# HomeKit client

This code only works with HomeKit IP Accessories. no Bluetooth LE Accessories (yet)!

The code presented in this repository was created based on release R1 from 2017-06-07.

## discover.py

This tool will list all available HomeKit IP Accessories.

Usage:
```bash
python3 discover.py
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

## identfy.py

This tool will use the Identify Routine of a HomeKit IP Accessory.

Usage:
```bash
python3 identify.py -d ${DEVICEID}
```

Output:

Either *identify succeeded.* or *identify failed* followed by a reason (see table 5-12 page 80). 

## pair.py

This tool will perform a paring to a new accessory.

Usage:
```bash
python3 pair.py -d ${DEVICEID} -p ${SETUPCODE} -f ${PAIRINGDATAFILE}
```

## perform.py