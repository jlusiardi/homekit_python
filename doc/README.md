# About this project

This project started after Apple released the HomeKit Accessory Protocol Specification (Non-Commercial Version) mid 2017. The goal is to offer two main parts:

 1. have some python code to act as a HomeKit Controller (which would usually be your iOS device). See [HomeKit Controller API](./HomeKit-Controller-API.md) for more information.
 2. coding an accessory in python to be controlled by an iOS device (and therefore by Siri). See [HomeKit Accessory API](./HomeKit-Accessory-API.md) for more information.

## Test a HomeKit Accessory

To help with testing new devices, please have a look at [HomeKit Device Testing](./HomeKit-Accessory-Testing-Guide.md). If the test was successful, please make a pull request for a new Markdown file to post the results. If the test fails, please open an issue.

## Supported operations while controlling HomeKit Accesories

|   | IP Transport | Bluetooth LE Transport |
| ------------- | ------------- | ------------- |
| pair accessory  |   :heavy_check_mark:  |  :heavy_check_mark:  |
| unpair accessory  |   :heavy_check_mark:  |  :heavy_check_mark:  |
| identify paired accessory  |   :heavy_check_mark:  |  :heavy_check_mark: |
| get accessories  |   :heavy_check_mark:  |  :heavy_check_mark: |
| handle parings  |   :heavy_check_mark:  |  :heavy_check_mark: |
| get characteristics  |   :heavy_check_mark:  |  :heavy_check_mark: |
| put characteristics  |   :heavy_check_mark:  |  :heavy_check_mark: |
| get events  |   :heavy_check_mark:  |   |

## Supported operations as HomeKit Accesory

|   | IP Transport | Bluetooth LE Transport |
| ------------- | ------------- | ------------- |
| pair accessory  |   :heavy_check_mark:  |   |
| unpair accessory  |   :heavy_check_mark:  |    |
| identify paired accessory  |   :heavy_check_mark:  |   |
| get accessories  |   :heavy_check_mark:  |   |
| handle parings  |   partly  |  |
| get characteristics  |   :heavy_check_mark:  |   |
| put characteristics  |   :heavy_check_mark:  |   |
| get events  |   :heavy_check_mark:  |   |


