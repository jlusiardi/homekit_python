# About this project

This project started after Apple released the HomeKit Accessory Protocol Specification (Non-Commercial Version) mid 2017. The goal is to offer two main parts:

 1. have some python code to act as a HomeKit Controller (which would usually be your iOS device). See [HomeKit Controller API](./HomeKit-Controller-API.md) for more information.
 2. coding an accessory in python to be controlled by an iOS device (and therefore by Siri). See [HomeKit Accessory API](./HomeKit-Accessory-API.md) for more information.

## Test a HomeKit Accessory

To help with testing new devices, please have a look at [HomeKit Device Testing](./HomeKit-Accessory-Testing-Guide.md).

## Supported operations while controlling HomeKit Accesories

|   | IP Transport | Bluetooth LE Transport |
| ------------- | ------------- | ------------- |
| pair accessory  |   :heavy_check_mark:  |  :heavy_check_mark: (in branch add_bluetooth) |
| unpair accessory  |   :heavy_check_mark:  |  :heavy_check_mark: (in branch add_bluetooth) |
| identify paired accessory  |   :heavy_check_mark:  |  :heavy_check_mark: (in branch add_bluetooth) |
| ...  | ... | ... |

## Supported operations as HomeKit Accesory

|   | IP Transport | Bluetooth LE Transport |
| ------------- | ------------- | ------------- |
| pair accessory  |   :heavy_check_mark:  |   |
| unpair accessory  |   :heavy_check_mark:  |   |
| identify paired accessory  |   :heavy_check_mark:  |  |
| ...  | ... | ... |


