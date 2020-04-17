# Plugins

Plugins for HomeKit Python will be used to offer support for vendor specific
services and characteristics.

Currently there are two use cases for plugins:

 * decoders for vendor specific characteristics of format tlv
 * commands to interact with vendor specific characteristics

As an example, let's have a look at
[the Koogeek P1EU](./tested_devices/Koogeek%20P1EU.md). This device has some
vendor specific characteristics mostly read only like the characteristic
with UUID `4AAAF93E-0DEC-11E5-B939-0800200C9A66` (`MONTH_DATA_LAST_YEAR`
holding information on power consumption on a monthly basis for the last year).
To read those characteristics with the `get_accessory` or `get_characteristic`
commands with the `-d` (decode) option set, we need special decoders. Other
characteristics can also be written, in case of this accessory its
`4AAAF942-0DEC-11E5-B939-0800200C9A66` (`TIMER_SETTINGS`). To manipulate the
setting of the independent timing function a new command would be useful.

## How to create a plugin

Simple, create a PyPI module. The name pattern of the module is not specified.
The dependency list of the module **must** contain `homekit_python`

### Plugins providing only additional commands

A plugin that provides just additional commands are not bound to anything else.

### Plugins providing vendor specific

A plugin that provides decoders for vendor specific characteristics **must**
have a dependency on `homekit_python>=0.17.0` (this is the version plugins
got implemented) and **must** contain a package whose name starts with
`homekit_`. Within the plugin, there **must** be this structure:

```
plugin_module_directory
  \homekit_XXX
    \model
      \characteristics
        \uuid_XXXXXXXX_YYYY_ZZZZ_AAAA_BBBBBBBBBBBB.py
        \...
```

Each of these `uuid_XXXXXXXX_YYYY_ZZZZ_AAAA_BBBBBBBBBBBB.py` must contain a
function `decoder`:
```python
def decoder(bytes_data: bytes) -> tlv8.EntryList:
    pass
```
