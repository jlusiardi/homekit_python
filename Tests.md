# Testing

# Running unit tests

```bash
python3 -m unittest -v
```

# Test pair & unpair

# Bluetooth LE
```bash
PYTHONPATH=. python3 homekit/pair_ble.py -f ble.json -a DW1 -m e2:a3:cb:26:77:61 -p 893-01-591;\
PYTHONPATH=. python3 homekit/unpair.py -f ble.json -a DW1
```

# IP
```bash
PYTHONPATH=. python3 homekit/pair.py -f controller.json -a esp -d EC:73:A0:BD:97:22 -p 111-11-111;\
PYTHONPATH=. python3 homekit/unpair.py -f controller.json -a esp
```