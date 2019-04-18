This page will describe how to implement a HomeKit Accessory with this package.

# Use Cases

The HomeKit Accessory Api will cover the following use cases:
 1. Handle the communication with HomeKit controllers
 2. Add accessories to the server
 3. Add services to accessories
 4. React to HomeKit requests via callbacks

**Important**
Only IP Accessories are currently supported. No Bluetooth LE yet.

# Implementation

The use cases are split onto two main classes. These are shown in the class diagram below:

![UML Class diagram for Accessory API](https://github.com/jlusiardi/homekit_python/wiki/accessory.png)

# Example

This example shall demonstrate how to implement a simple HomeKit Accessory acting as a light bulb. It can just be turned on and off.

```python
# callback function
def callback_function(value):
  print(value)

# create server
server = AccessoryServer(config_file)

# create an accessory
accessory = Accessory('Name', 'Manufacturer', 'Model', \
                      'SerialNumber', 'FirmwareRevision')

# create a service 
lightBulbService = LightBulbService()
lightBulbService.set_on_set_callback(callback_function)

# add the service to the accessory
accessory.add_services(lightBulbService)

# add accessory to the server
server.add_accessory(accessory)

# start the server
server.publish_device()
server.serve_forever()

# let it run, e.g. until KeyboardInterrupt and clean up after that
server.unpublish_device()
server.shutdown()
```

The configuration file contains the persistent data for the accessory:

```json
{
  "accessory_ltpk": "7986cf939de8986f428744e36ed72d86189bea46b4dcdc8d9d79a3e4fceb92b9",
  "accessory_ltsk": "3d99f3e959a1f93af4056966f858074b2a1fdec1c5fd84a51ea96f9fa004156a",
  "accessory_pairing_id": "12:34:56:78:AB:CD",
  "accessory_pin": "081-54-711",
  "c#": 1,
  "category": "Lightbulb",
  "host_ip": "127.0.0.1",
  "host_port": 12345,
  "name": "demoLight",
  "peers": {
    "47447316-2cda-4fb6-a8c7-dd45e3d6c8f8": {
      "admin": true,
      "key": "ee56badb65f151e338b4fee26bd3768157aa996002790acc8a06cd1dfb678534"
    }
  },
  "unsuccessful_tries": 0
}
```
Please adjust **host_ip** to an IP address on your machine that is reachable from your iOS device and **host_port** to an unused one.

# How are services created

Each service must inherit `homekit.model.services.AbstractService` and must have at least one characteristic.
To ease adding characteristics, each characteristic has an associated mix-in. E.g. the `OnCharacteristic` has the 
`OnCharacteristicMixin`, that on inheritance adds an `OnCharacteristic` and 2 callback setter functions to the inheriting class.

Example **OnCharacteristicMixin** and **LightBulbService**:

```python
class OnCharacteristicMixin(object):
    def __init__(self, iid):
        self._onCharacteristic = OnCharacteristic(iid)
        self.characteristics.append(self._onCharacteristic)

    def set_on_set_callback(self, callback):
        self._onCharacteristic.set_set_value_callback(callback)

    def set_on_get_callback(self, callback):
        self._onCharacteristic.set_get_value_callback(callback)


class LightBulbService(AbstractService, OnCharacteristicMixin):
    def __init__(self):
        AbstractService.__init__(self, ServicesTypes.get_uuid('public.hap.service.lightbulb'), get_id())
        OnCharacteristicMixin.__init__(self, get_id())
```

The **LightBulbService** should be switchable (on / off) so we add the **_onCharacteristic** via the mix-in. Just inherited and initialize it and the to methods (**set_on_set_callback** and **set_on_get_callback**) are available.
