#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__all__ = [
    'CharacteristicsTypes', 'CharacteristicPermissions', 'AbstractCharacteristic', 'BatteryLevelCharacteristic',
    'BatteryLevelCharacteristicMixin', 'BrightnessCharacteristic', 'BrightnessCharacteristicMixin',
    'CharacteristicFormats', 'CharacteristicUnits', 'CurrentHeatingCoolingStateCharacteristic',
    'CurrentHeatingCoolingStateCharacteristicMixin', 'CurrentTemperatureCharacteristic',
    'CurrentTemperatureCharacteristicMixin', 'FirmwareRevisionCharacteristic', 'HardwareRevisionCharacteristic',
    'HueCharacteristic', 'HueCharacteristicMixin', 'IdentifyCharacteristic', 'ManufacturerCharacteristic',
    'ModelCharacteristic', 'NameCharacteristic', 'OnCharacteristic', 'OnCharacteristicMixin',
    'OutletInUseCharacteristic', 'OutletInUseCharacteristicMixin', 'SaturationCharacteristic',
    'SaturationCharacteristicMixin', 'SerialNumberCharacteristic', 'TargetHeatingCoolingStateCharacteristic',
    'TargetHeatingCoolingStateCharacteristicMixin', 'TargetTemperatureCharacteristic',
    'TargetTemperatureCharacteristicMixin', 'TemperatureDisplayUnitCharacteristic', 'TemperatureDisplayUnitsMixin',
    'VolumeCharacteristic', 'VolumeCharacteristicMixin', 'CharacteristicsDecoderLoader'
]

import importlib
import logging
import pkgutil

from homekit.model.characteristics.characteristic_permissions import CharacteristicPermissions
from homekit.model.characteristics.characteristic_types import CharacteristicsTypes
from homekit.model.characteristics.characteristic_units import CharacteristicUnits
from homekit.model.characteristics.characteristic_formats import CharacteristicFormats

from homekit.model.characteristics.abstract_characteristic import AbstractCharacteristic
from homekit.model.characteristics.battery_level import BatteryLevelCharacteristic, BatteryLevelCharacteristicMixin
from homekit.model.characteristics.brightness import BrightnessCharacteristicMixin, BrightnessCharacteristic
from homekit.model.characteristics.current_heating_cooling_state import CurrentHeatingCoolingStateCharacteristicMixin, \
    CurrentHeatingCoolingStateCharacteristic
from homekit.model.characteristics.current_temperature import CurrentTemperatureCharacteristicMixin, \
    CurrentTemperatureCharacteristic
from homekit.model.characteristics.firmware_revision import FirmwareRevisionCharacteristic
from homekit.model.characteristics.hardware_revision import HardwareRevisionCharacteristic
from homekit.model.characteristics.hue import HueCharacteristicMixin, HueCharacteristic
from homekit.model.characteristics.identify import IdentifyCharacteristic
from homekit.model.characteristics.manufacturer import ManufacturerCharacteristic
from homekit.model.characteristics.model import ModelCharacteristic
from homekit.model.characteristics.name import NameCharacteristic
from homekit.model.characteristics.on import OnCharacteristicMixin, OnCharacteristic
from homekit.model.characteristics.outlet_in_use import OutletInUseCharacteristic, OutletInUseCharacteristicMixin
from homekit.model.characteristics.saturation import SaturationCharacteristicMixin, SaturationCharacteristic
from homekit.model.characteristics.serialnumber import SerialNumberCharacteristic
from homekit.model.characteristics.target_heating_cooling_state import TargetHeatingCoolingStateCharacteristic, \
    TargetHeatingCoolingStateCharacteristicMixin
from homekit.model.characteristics.target_temperature import TargetTemperatureCharacteristicMixin, \
    TargetTemperatureCharacteristic
from homekit.model.characteristics.temperature_display_unit import TemperatureDisplayUnitsMixin, \
    TemperatureDisplayUnitCharacteristic
from homekit.model.characteristics.volume import VolumeCharacteristic, VolumeCharacteristicMixin


class CharacteristicsDecoderLoader:
    """
    class to dynamically load decoders for tlv8 characteristics.
    """

    def __init__(self):
        self.decoders = {}

    def load(self, char_type: str):
        """
        This function loads a decoder for the specified characteristics:
         - get the name of the characteristic via the given uuid (via `CharacteristicsTypes.get_short()`)
         - load a module from `homekit.model.characteristics` plus the name of the characteristic
         - the module must contain a function `decoder`

        :param char_type: the uuid of the characteristic
        :return: a function that decodes the value of the characteristic into a `tlv8.EntryList`
        """
        characteristic_name = CharacteristicsTypes.get_short(char_type)
        if characteristic_name.startswith('Unknown'):
            mod_name = 'uuid_{}'.format(char_type.replace('-', '_'))
            logging.info('modname %s', mod_name)
        else:
            mod_name = characteristic_name.replace('-', '_')
        if char_type not in self.decoders:

            # try to dynamically load from the standard characteristics by name
            try:
                logging.info('loading module "%s" for type "%s"', mod_name, char_type)
                module = importlib.import_module('homekit.model.characteristics.' + mod_name)
                decoder = getattr(module, 'decoder')
                self.decoders[char_type] = decoder
                return decoder
            except Exception as e:
                logging.info('Error loading decoder: "%s" for type "%s"', e, char_type)

            # try to load from all plugins, it may be a non-standard characteristic with vendor specific data
            try:
                for _, plugin_name, _ in pkgutil.iter_modules():
                    if not plugin_name.startswith('homekit_'):
                        continue
                    logging.info('loading module "%s" for type "%s" from plugin "%s"', mod_name, char_type, plugin_name)
                    module = importlib.import_module('.model.characteristics.' + mod_name, plugin_name)
                    decoder = getattr(module, 'decoder')
                    self.decoders[char_type] = decoder
                    return decoder
            except Exception as e:
                logging.info('Error loading decoder: "%s" for type "%s"', e, char_type)

            return None
        else:
            logging.info('got decoder for %s from cache', char_type)
            return self.decoders[char_type]
