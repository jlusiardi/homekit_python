This page will describe the stable API for acting as a Homekit controller with this python module.

# Use Cases

The HomeKit Controller API will cover the following use cases:
 1. discover HomeKit enabled devices (see [homekit.Controller.discover](#homekitcontrollerdiscover))
 2. identify unpaired and paired HomeKit devices (see [homekit.Controller.identify](#homekitcontrolleridentify) and [homekit.Pairing.identify](#homekitpairingput_characteristics))
 3. pair HomeKit devices (see [homekit.Controller.perform_pairing](#homekitcontrollerperform_pairing))
 4. read out the HomeKit accessories of a device (see [homekit.Pairing.list_accessories_and_characteristics](#homekitpairinglist_accessories_and_characteristics))
 5. read out one or more characteristics of an accessory (see [homekit.Pairing.get_characteristics](#homekitpairingget_characteristics))
 6. write back one or more characteristics of an accessory (see [homekit.Pairing.put_characteristics](#homekitpairingput_characteristics))
 7. register for events send back by the accessory to the controller (see [homekit.Pairing.get_events](#homekitpairingget_events))
 8. remove the pairing with a device (see [homekit.Controller.remove_pairing](#homekitcontrollerremove_pairing))

**Important**
Only IP Accessories are currently supported. No Bluetooth LE yet.

# Implementation

The use cases are split into two main classes. These are shown in the class diagram below:

![UML Class diagram for Controller API](https://github.com/jlusiardi/homekit_python/wiki/controller.png)

To make handling of paired accessories easier, pairings will have an alias as a shortcut in the controller objects.

## homekit.Controller

This class replaces the iOS Device acting as Controller in typical scenarios.





### homekit.Controller.discover

This method uses Bonjour / Zeroconf technology to gather HomeKit Accessories from within the same IP network.

#### Parameters
 1. `max_seconds` (default: 10): how many seconds is the inquiry running. After that time the result is prepared and 
    returned.
    
#### Result
The method returns a list of the discovered devices. The devices are represented by dicts that contain the following 
keys:
 * `name`: the Bonjour name of the HomeKit accessory (i.e. Testsensor1._hap._tcp.local.)
 * `address`: the IP address of the accessory
 * `port`: the used IP port
 * `c#`: the configuration number 
 * `ff` / `flags`: the numerical and human readable version of the feature flags (supports pairing or not, see table 5-8 page 69 or homekit.model.FeatureFlags) 
 * `id`: the accessory's pairing id 
 * `md`: the model name of the accessory 
 * `pv`: the protocol version
 * `s#`: the current state number
 * `sf`: the status flag (see table 5-9 page 70)
 * `ci` / `category`: the category identifier in numerical and human readable form. For more information see table 12-3 page 254 or homekit.model.Categories





### homekit.Controller.identify

This method is used to trigger the identification of an unpaired HomeKit Accessory. It is depending on the device's implementation on how it reacts to this call. A light bulb may be flashing in a specific pattern or a switch plug might turn its status LED on and off.

#### Parameters

 1. `accessory_id`: the HomeKit accessory's pairing id (field `id` of the results of `discover`).
    
#### Result

This method does not return anything but raises a `AccessoryNotFoundError` if no device with the `accessory_id` could be looked up via Bonjour. 




### homekit.Controller.load_data

This method loads previously stored data about the pairings known to this controller from a file. Should be performed at the beginning of a program that uses the controller.

#### Parameters

 1. `filename`: The file that should be loaded. 

#### Result

This method does not return anything but raises `ConfigLoadingError` on any error while loading the data.





### homekit.Controller.save_data

This method saves data about the pairings known to this controller to a file. Should be performed after all methods that change pairing information (`perform_pairing` and `remove_pairing`).

#### Parameters

 1. `filename`: The file that should be saved to. 

#### Result

This method does not return anything but raises `ConfigSavingError` on any error while loading the data.





### homekit.Controller.get_pairings

This method offers access to all known pairing of the controller. 

#### Parameters

No parameter is required.

#### Result

This method returns a dict of aliases to pairing objects. The aliases are defined while performing a pairing operation. 





### homekit.Controller.perform_pairing

This method performs a pairing operation with a previously unpaired device. After a successful pairing the method 
`save_data` should be called to persist the pairing data.

#### Parameters

 1. `alias`: The alias under which the device will be known to the controller, e.g. `KitchenLight`.
 2. `accessory_id`: The HomeKit accessory's pairing id (field `id` of the results of `discover`).
 3. `pin`: The HomeKit accessory's pairing PIN as printed on the device. 

#### Result

No return value but there are some exceptions to be raised on errors :
 * `AccessoryNotFoundError`: no device with the `accessory_id` could be found
 * `AlreadyPairedError`: the alias is already used for a pairing
 * `UnavailableError`: the device is already paired to some other controller. Unpair it first.
 * `MaxTriesError`: if the device received more than 100 unsuccessful pairing attempts
 * `BusyError`: if a parallel pairing is ongoing
 * `AuthenticationError`: if the verification of the device's SRP proof fails, e.g. on a wrong pin
 * `MaxPeersError`: if the device cannot accept an additional pairing
 * `IllegalDataError`: if the verification of the accessory's data fails





### homekit.Controller.remove_pairing

Removes a pairing between controller and accessory. Pairing data is cleared on both ends so the accessory can be paired by controller's again.

#### Parameters

 1. `alias`: The alias under which the device will be known to the controller, e.g. `KitchenLight`.

#### Result

No return value but there are some exceptions to be raised on errors :
 * `AuthenticationError`: no device with the `accessory_id` could be found
 * `AccessoryNotFoundError`: if the device can not be found via zeroconf e.g. if it is out of reach or turned off
 * `UnknownError`: on unknown errors

## homekit.Pairing

This class represents the pairing between the controller and a HomeKit accessory.





### homekit.Pairing.list_accessories_and_characteristics

Retrieves the accessories and characteristics behind a pairing.

#### Parameters

No parameters are required.

#### Result

If the call is successful, it returns data as specified in chapter 5.6 page 71 ff in the specification. In addtion it may raise the following error:
 * `AccessoryNotFoundError`: if the device can not be found via zeroconf e.g. if it is out of reach or turned off

 The resulting data is structured like this:
 
	 [
	    {
		'aid': 1,
		'services': [
		    {
			'iid': 2,
			'type': '0000003E-0000-1000-8000-0026BB765291',
			'characteristics': [
			    {
			        'iid': 3,
			        'perms': ['pw'],
			        'format': 'bool',
			        'description': 'Identify',
			        'type': '00000014-0000-1000-8000-0026BB765291'
			    }, ...
			]
		     }, ...
		]
	    }
	]





### homekit.Pairing.get_characteristics

Retrieves the current value of a list of characteristics and optional information if requested.

#### Parameters
 1. `characteristics`: a list of 2 tupels of accessory id and instance id `(aid, iid)`
 2. `include_meta`: set to `True` if the result should contain meta information about the characteristics. This includes details about the format, unit and limits of the characteristics. (**optional**, default `False`)
 3. `include_perms`: set to `True` if the result should contain information about permissions for the characteristics.  (**optional**, default `False`)
 4. `include_type`: set to `True` if the result should contain information about the type for the characteristics. The type result refers to the UUID defined in the specification in chapter 8. The rules for abbreviations are defined in chapter 5.6.1 page 72. (**optional**, default `False`)
 5. `include_events`: set to `True` if the result should contain information if events are subscribed for by the caller.  (**optional**, default `False`)

#### Result

The result is a dict with tupels `(aid, iid)` as keys and dicts as values. The dict contains either information why the call failed (`status` and `description`) for the particular tupel of `(aid, iid)`, or it contains the requested information.

As example, this is the result for a request for 3 characteristics (`1.50`, `1.2` and `1.3`) including meta data, permissions and type information:
```
	{
		(1, 50): {
			'status': -70409,
			'description': 'Resource does not exist.'
	    	},
		(1, 2): {
			'type': '23',
			'format': 'string',
			'maxLen': 64,
			'perms': ['pr'],
			'value': 'Name Characteristic'
		},
	    	(1, 3): {
			'type': '20',
			'format': 'string',
			'maxLen': 64,
			'perms': ['pr'],
			'value': 'Manufacturer Characteristic'
		}
	}
```





### homekit.Pairing.get_events

This function is used to register to events sent from an accessory. Om each event, the given call back function is called.

#### Parameters

1. `characteristics`: a list of 2-tupels of accessory id (aid) and instance id (iid)
2. `callback_fun`: the callback function
3. `max_events`: the maximum number of events to wait for. `-1` means unlimitted  (**optional**, default `-1`).
4. `max_seconds`: the maximum number of seconds to wait for. This is no absolute hard limit, it may take a little longer, so don't use for timing critical stuff! `-1` means unlimitted  (**optional**, default `-1`).

#### Result

As main result, the callback function is called with a list of 3-tupels each time at least one event occurs. Thevalues in the 3-tupels are:
 * accessory id (`aid`)
 * instance id (`iid`)
 * the value of the characteristic 

If there is a problem while subscribing to the events, a dict is returned. This dict contains tupels `(aid, iid)` as key for all input tupels for which no events can be subscribed. The mapped values are dicts with keys:
 * `status`: the numerical value as defined in table 5-12 on page 80 in the specification
 * `description`: a textual representation of the status (the description column of table 5-12 on page 80)

For more information see `homekit.protocol.statuscodes.HapStatusCodes`.





### homekit.Pairing.list_pairings

This method returns all pairings of a HomeKit accessory. This always includes the local controller and can only  be done by an admin controller.

#### Parameters

No paramters are required.

#### Result

One dict per pairing is returned in a list. These dicts contain keys for:
 * pairingId: the pairing id of the controller
 * publicKey: the ED25519 long-term public key of the controller
 * permissions: bit value for the permissions
 * controllerType: either admin or regular

In addtion it may raise the following errors:
 * `UnknownError`: if the function receives unexpected data
 * `UnpairedError`: if the polled accessory is not paired





### homekit.Pairing.put_characteristics

This function is used to change on or more characteristics to a new value. 

#### Parameters

1. `characteristics`: a list of characteristics (identified by accessory id `aid` and characteristic id `iid`) and the target value to set. E.g. `[(1,2,True), (1,3,0.2)]`
2. `do_conversion`: set to `True` if a conversion into the format of the characteristic should be performed. (**optional**, default `False`)
 
#### Result

Returns a dict with the same number of keys as the first parameter. For each key `(aid, iid)`  it contains a dict with two keys:
 * `status`: the numerical value as defined in table 5-12 on page 80 in the specification
 * `description`: a textual representation of the status (the description column of table 5-12 on page 80)

For more information see `homekit.protocol.statuscodes.HapStatusCodes`.

In addtion, this function may raise a `FormatError` if the parameter `do_conversion` is set to `True` and the conversion into the characteristic's format cannot be performed, e.g. when boolean value is given but a numerical format is required).





### homekit.Pairing.identify

This triggers the identify function for a paired accessory.

#### Parameters

No paramters are required.

#### Result

Returns `True` if the identify call could be executed successfully, `False` otherwise.

