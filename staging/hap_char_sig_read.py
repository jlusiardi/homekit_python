#!/usr/bin/env python3

import gatt.gatt_linux
import uuid
from argparse import ArgumentParser
import homekit.protocol.tlv
import struct
import logging
import json

# OpCodes (table 6-7 page 97)
HAP_CHAR_SIG_READ = 1
HAP_CHAR_WRITE = 2
HAP_CHAR_READ = 3
HAP_CHAR_TIMED_WRITE = 4
HAP_CHAR_EXEC_WRITE = 5
HAP_SERVICES_SIG_READ = 6


CharacteristicInstanceID='dc46f0fe-81d2-4616-b5d9-6abdd796939a'


# https://developer.nordicsemi.com/nRF5_SDK/nRF51_SDK_v4.x.x/doc/html/group___b_l_e___g_a_t_t___c_p_f___f_o_r_m_a_t_s.html
characteristic_formats = {
    0x01: 'bool',
    0x04: 'uint8',
    0x08: 'uint32',
    0x10: 'int32',
    0x19: 'utf-8',
    0x1b: 'struct'
}

# https://www.bluetooth.com/specifications/assigned-numbers/units
characteristic_units = {
    0x2700: 'none',
    0x27ad: 'percentage',
}


def parse_sig_read_response(data, tid):
    # parse header and check stuff
    logging.debug('parse sig read response %s', bytes([int(a) for a in data]).hex())

    # get body length
    length = int.from_bytes(data[3:5], byteorder='little')
    tlv = homekit.protocol.tlv.TLV.decode_bytes(data[5:])

    # chr type
    chr_type = [int(a) for a in data[7:23]]
    chr_type.reverse()
    chr_type = ''.join('%02x' % b for b in chr_type)

    svc_id = int.from_bytes(data[25:27], byteorder='little')

    svc_type = [int(a) for a in data[29:45]]
    svc_type.reverse()
    svc_type = ''.join('%02x' % b for b in svc_type)

    chr_prop = None
    desc = ''
    format = ''
    range = None
    step = None
    for t in tlv:
        if t[0] == 0x0A:
            chr_prop_int = int.from_bytes(t[1], byteorder='little')
            chr_prop = [int(a) for a in t[1]]
            chr_prop.reverse()
            chr_prop = ''.join('%02x' % b for b in chr_prop)
        if t[0] == 0x0B:
            desc = t[1].decode()
        if t[0] == 0x11:
            print('valid values', t[1])
        if t[0] == 0x12:
            print('valid values range', t[1])
        if t[0] == 0x0C:
            unit_bytes = t[1][2:4]
            unit_bytes.reverse()
            format = characteristic_formats.get(int(t[1][0]), 'unknown')
            unit = characteristic_units.get(int.from_bytes(unit_bytes, byteorder='big'), 'unknown')
            # print('format data', t[1].hex())
            # print('\tFormat', characteristic_formats.get(int(t[1][0]), 'unknown'))
            # print('\tExponent', int(t[1][1]))
            # print('\tUnit', characteristic_units.get(int.from_bytes(unit_bytes, byteorder='big'), 'unknown'))
            # print('\tNamespace', int(t[1][4]))
            # print('\tDescription', t[1][5:].hex())
        if t[0] == 0x0D:
            # print('range', t[1])
            # print(type(t[1]), format)
            lower = None
            upper = None
            if format == 'int32':
                (lower, upper) = struct.unpack('ii', t[1])
            if format == 'uint8':
                (lower, upper) = struct.unpack('BB', t[1])
            # l = len(t[1])
            # lower = t[1][:int(l/2)]
            # upper = t[1][int(l/2):]
            # print(lower, upper)
            range = (lower, upper)
        if t[0] == 0x0E:
            # print('step', t[1])
            step = None
            if format == 'int32':
                step = struct.unpack('i', t[1])[0]
            if format == 'uint8':
                step = struct.unpack('B', t[1])[0]

    # print('\t\t\t', 'chr_type', chr_type, 'svc_id', svc_id, 'svc_type', svc_type, 'chr_prop', chr_prop, 'desc >', desc, '<')

    perms = []
    if (chr_prop_int & 0x0001) > 0:
        perms.append('r')
    if (chr_prop_int & 0x0002) > 0:
        perms.append('w')
    if (chr_prop_int & 0x0004) > 0:
        perms.append('aad')
    if (chr_prop_int & 0x0008) > 0:
        perms.append('tw')
    if (chr_prop_int & 0x0010) > 0:
        perms.append('pr')
    if (chr_prop_int & 0x0020) > 0:
        perms.append('pw')
    if (chr_prop_int & 0x0040) > 0:
        perms.append('hd')
    if (chr_prop_int & 0x0080) > 0:
        perms.append('evc')
    if (chr_prop_int & 0x0100) > 0:
        perms.append('evd')

    return {'description': desc, 'perms': perms, 'format': format, 'unit': unit, 'range': range, 'step': step}


class _CharacteristicsTypes(object):
    """
    Translate the characteristic's UUIDs into the type description (as defined by Apple).
    E.g:
        "6D" becomes "0000006D-0000-1000-8000-0026BB765291" and translates to
        "public.hap.characteristic.position.current" or "position.current"
    Data is taken from chapter 8 of the specification (page 144ff)
    """
    ACCESSORY_PROPERTIES = 'A6'
    ACTIVE = 'B0'
    ADMINISTRATOR_ONLY_ACCESS = '1'
    AIR_PARTICULATE_DENSITY = '64'
    AIR_PARTICULATE_SIZE = '65'
    AIR_PURIFIER_STATE_CURRENT = 'A9'
    AIR_PURIFIER_STATE_TARGET = 'A8'
    AIR_QUALITY = '95'
    AUDIO_FEEDBACK = '5'
    BATTERY_LEVEL = '68'
    BRIGHTNESS = '8'
    CARBON_DIOXIDE_DETECTED = '92'
    CARBON_DIOXIDE_LEVEL = '93'
    CARBON_DIOXIDE_PEAK_LEVEL = '94'
    CARBON_MONOXIDE_DETECTED = '69'
    CARBON_MONOXIDE_LEVEL = '90'
    CARBON_MONOXIDE_PEAK_LEVEL = '91'
    CHARGING_STATE = '8F'
    COLOR_TEMPERATURE = 'CE'
    CONTACT_STATE = '6A'
    DENSITY_NO2 = 'C4'
    DENSITY_OZONE = 'C3'
    DENSITY_PM10 = 'C7'
    DENSITY_PM25 = 'C6'
    DENSITY_SO2 = 'C5'
    DENSITY_VOC = 'C8'
    DOOR_STATE_CURRENT = 'E'
    DOOR_STATE_TARGET = '32'
    FAN_STATE_CURRENT = 'AF'
    FAN_STATE_TARGET = 'BF'
    FILTER_CHANGE_INDICATION = 'AC'
    FILTER_LIFE_LEVEL = 'AB'
    FILTER_RESET_INDICATION = 'AD'
    FIRMWARE_REVISION = '52'
    HARDWARE_REVISION = '53'
    HEATING_COOLING_CURRENT = 'F'
    HEATING_COOLING_TARGET = '33'
    HORIZONTAL_TILT_CURRENT = '6C'
    HORIZONTAL_TILT_TARGET = '7B'
    HUE = '13'
    IDENTIFY = '14'
    IMAGE_MIRROR = '11F'
    IMAGE_ROTATION = '11E'
    INPUT_EVENT = '73'
    LEAK_DETECTED = '70'
    LIGHT_LEVEL_CURRENT = '6B'
    LOCK_MANAGEMENT_AUTO_SECURE_TIMEOUT = '1A'
    LOCK_MANAGEMENT_CONTROL_POINT = '19'
    LOCK_MECHANISM_CURRENT_STATE = '1D'
    LOCK_MECHANISM_LAST_KNOWN_ACTION = '1C'
    LOCK_MECHANISM_TARGET_STATE = '1E'
    LOCK_PHYSICAL_CONTROLS = 'A7'
    LOGS = '1F'
    MANUFACTURER = '20'
    MODEL = '21'
    MOTION_DETECTED = '22'
    MUTE = '11A'
    NAME = '23'
    NIGHT_VISION = '11B'
    OBSTRUCTION_DETECTED = '24'
    OCCUPANCY_DETECTED = '71'
    ON = '25'
    OUTLET_IN_USE = '26'
    PAIR_SETUP = '4C'        # new for BLE, page 57
    PAIR_VERIFY = '4E'       # new for BLE, page 57
    PAIRING_FEATURES = '4F'       # new for BLE, page 58
    PAIRING_PAIRINGS = '50'       # new for BLE, page 58
    POSITION_CURRENT = '6D'
    POSITION_HOLD = '6F'
    POSITION_STATE = '72'
    POSITION_TARGET = '7C'
    RELATIVE_HUMIDITY_CURRENT = '10'
    RELATIVE_HUMIDITY_TARGET = '34'
    ROTATION_DIRECTION = '28'
    ROTATION_SPEED = '29'
    SATURATION = '2F'
    SECURITY_SYSTEM_ALARM_TYPE = '8E'
    SECURITY_SYSTEM_STATE_CURRENT = '66'
    SECURITY_SYSTEM_STATE_TARGET = '67'
    SELECTED_RTP_STREAM_CONFIGURATION = '117'
    SERIAL_NUMBER = '30'
    SERVICE_LABEL_INDEX = 'CB'
    SERVICE_LABEL_NAMESPACE = 'CD'
    SERVICE_INSTANCE_ID = 'e604e95d-a759-4817-87d3-aa005083a0d1'.upper() # new for BLE, page 127
    SERVICE_SIGNATURE = 'A5'    # new for BLE, page 128
    SETUP_ENDPOINTS = '118'
    SLAT_STATE_CURRENT = 'AA'
    SMOKE_DETECTED = '76'
    STATUS_ACTIVE = '75'
    STATUS_FAULT = '77'
    STATUS_JAMMED = '78'
    STATUS_LO_BATT = '79'
    STATUS_TAMPERED = '7A'
    STREAMING_STATUS = '120'
    SUPPORTED_AUDIO_CONFIGURATION = '115'
    SUPPORTED_RTP_CONFIGURATION = '116'
    SUPPORTED_VIDEO_STREAM_CONFIGURATION = '114'
    SWING_MODE = 'B6'
    TEMPERATURE_COOLING_THRESHOLD = 'D'
    TEMPERATURE_CURRENT = '11'
    TEMPERATURE_HEATING_THRESHOLD = '12'
    TEMPERATURE_TARGET = '35'
    TEMPERATURE_UNITS = '36'
    TILT_CURRENT = 'C1'
    TILT_TARGET = 'C2'
    TYPE_SLAT = 'C0'
    VERSION = '37'
    VERTICAL_TILT_CURRENT = '6E'
    VERTICAL_TILT_TARGET = '7D'
    VOLUME = '119'
    ZOOM_DIGITAL = '11D'
    ZOOM_OPTICAL = '11C'

    def __init__(self):
        self.baseUUID = '-0000-1000-8000-0026BB765291'
        self._characteristics = {
            '1': 'public.hap.characteristic.administrator-only-access',
            '5': 'public.hap.characteristic.audio-feedback',
            '8': 'public.hap.characteristic.brightness',
            'D': 'public.hap.characteristic.temperature.cooling-threshold',
            'E': 'public.hap.characteristic.door-state.current',
            'F': 'public.hap.characteristic.heating-cooling.current',
            '10': 'public.hap.characteristic.relative-humidity.current',
            '11': 'public.hap.characteristic.temperature.current',
            '12': 'public.hap.characteristic.temperature.heating-threshold',
            '13': 'public.hap.characteristic.hue',
            '14': 'public.hap.characteristic.identify',
            '1A': 'public.hap.characteristic.lock-management.auto-secure-timeout',
            '1C': 'public.hap.characteristic.lock-mechanism.last-known-action',
            '1D': 'public.hap.characteristic.lock-mechanism.current-state',
            '1E': 'public.hap.characteristic.lock-mechanism.target-state',
            '1F': 'public.hap.characteristic.logs',
            '19': 'public.hap.characteristic.lock-management.control-point',
            '20': 'public.hap.characteristic.manufacturer',
            '21': 'public.hap.characteristic.model',
            '22': 'public.hap.characteristic.motion-detected',
            '23': 'public.hap.characteristic.name',
            '24': 'public.hap.characteristic.obstruction-detected',
            '25': 'public.hap.characteristic.on',
            '26': 'public.hap.characteristic.outlet-in-use',
            '28': 'public.hap.characteristic.rotation.direction',
            '29': 'public.hap.characteristic.rotation.speed',
            '2F': 'public.hap.characteristic.saturation',
            '30': 'public.hap.characteristic.serial-number',
            '32': 'public.hap.characteristic.door-state.target',
            '33': 'public.hap.characteristic.heating-cooling.target',
            '34': 'public.hap.characteristic.relative-humidity.target',
            '35': 'public.hap.characteristic.temperature.target',
            '36': 'public.hap.characteristic.temperature.units',
            '37': 'public.hap.characteristic.version',
            '4C': 'public.hap.characteristic.pairing.pair-setup',               # new for BLE, page 57
            '4E': 'public.hap.characteristic.pairing.pair-verify',              # new for BLE, page 57
            '4F': 'public.hap.characteristic.pairing.features',                 # new for BLE, page 58
            '50': 'public.hap.characteristic.pairing.pairings',                 # new for BLE, page 58
            'e604e95d-a759-4817-87d3-aa005083a0d1'.upper(): 'public.hap.service.protocol.service-id',  # new for BLE, page 127
            '52': 'public.hap.characteristic.firmware.revision',
            '53': 'public.hap.characteristic.hardware.revision',
            '64': 'public.hap.characteristic.air-particulate.density',
            '65': 'public.hap.characteristic.air-particulate.size',
            '66': 'public.hap.characteristic.security-system-state.current',
            '67': 'public.hap.characteristic.security-system-state.target',
            '68': 'public.hap.characteristic.battery-level',
            '69': 'public.hap.characteristic.carbon-monoxide.detected',
            '6A': 'public.hap.characteristic.contact-state',
            '6B': 'public.hap.characteristic.light-level.current',
            '6C': 'public.hap.characteristic.horizontal-tilt.current',
            '6D': 'public.hap.characteristic.position.current',
            '6E': 'public.hap.characteristic.vertical-tilt.current',
            '6F': 'public.hap.characteristic.position.hold',
            '70': 'public.hap.characteristic.leak-detected',
            '71': 'public.hap.characteristic.occupancy-detected',
            '72': 'public.hap.characteristic.position.state',
            '73': 'public.hap.characteristic.input-event',
            '75': 'public.hap.characteristic.status-active',
            '76': 'public.hap.characteristic.smoke-detected',
            '77': 'public.hap.characteristic.status-fault',
            '78': 'public.hap.characteristic.status-jammed',
            '79': 'public.hap.characteristic.status-lo-batt',
            '7A': 'public.hap.characteristic.status-tampered',
            '7B': 'public.hap.characteristic.horizontal-tilt.target',
            '7C': 'public.hap.characteristic.position.target',
            '7D': 'public.hap.characteristic.vertical-tilt.target',
            '8E': 'public.hap.characteristic.security-system.alarm-type',
            '8F': 'public.hap.characteristic.charging-state',
            '90': 'public.hap.characteristic.carbon-monoxide.level',
            '91': 'public.hap.characteristic.carbon-monoxide.peak-level',
            '92': 'public.hap.characteristic.carbon-dioxide.detected',
            '93': 'public.hap.characteristic.carbon-dioxide.level',
            '94': 'public.hap.characteristic.carbon-dioxide.peak-level',
            '95': 'public.hap.characteristic.air-quality',
            'A5': 'public.hap.characteristic.service-signature',
            'A6': 'public.hap.characteristic.accessory-properties',
            'A7': 'public.hap.characteristic.lock-physical-controls',
            'A8': 'public.hap.characteristic.air-purifier.state.target',
            'A9': 'public.hap.characteristic.air-purifier.state.current',
            'AA': 'public.hap.characteristic.slat.state.current',
            'AB': 'public.hap.characteristic.filter.life-level',
            'AC': 'public.hap.characteristic.filter.change-indication',
            'AD': 'public.hap.characteristic.filter.reset-indication',
            'AF': 'public.hap.characteristic.fan.state.current',
            'B0': 'public.hap.characteristic.active',
            'B6': 'public.hap.characteristic.swing-mode',
            'BF': 'public.hap.characteristic.fan.state.target',
            'C0': 'public.hap.characteristic.type.slat',
            'C1': 'public.hap.characteristic.tilt.current',
            'C2': 'public.hap.characteristic.tilt.target',
            'C3': 'public.hap.characteristic.density.ozone',
            'C4': 'public.hap.characteristic.density.no2',
            'C5': 'public.hap.characteristic.density.so2',
            'C6': 'public.hap.characteristic.density.pm25',
            'C7': 'public.hap.characteristic.density.pm10',
            'C8': 'public.hap.characteristic.density.voc',
            'CB': 'public.hap.characteristic.service-label-index',
            'CD': 'public.hap.characteristic.service-label-namespace',
            'CE': 'public.hap.characteristic.color-temperature',
            '114': 'public.hap.characteristic.supported-video-stream-configuration',
            '115': 'public.hap.characteristic.supported-audio-configuration',
            '116': 'public.hap.characteristic.supported-rtp-configuration',
            '117': 'public.hap.characteristic.selected-rtp-stream-configuration',
            '118': 'public.hap.characteristic.setup-endpoints',
            '119': 'public.hap.characteristic.volume',
            '11A': 'public.hap.characteristic.mute',
            '11B': 'public.hap.characteristic.night-vision',
            '11C': 'public.hap.characteristic.zoom-optical',
            '11D': 'public.hap.characteristic.zoom-digital',
            '11E': 'public.hap.characteristic.image-rotation',
            '11F': 'public.hap.characteristic.image-mirror',
            '120': 'public.hap.characteristic.streaming-status',
        }

        self._characteristics_rev = {self._characteristics[k]: k for k in self._characteristics.keys()}

    def __getitem__(self, item):
        if item in self._characteristics:
            return self._characteristics[item]

        if item in self._characteristics_rev:
            return self._characteristics_rev[item]

        # https://docs.python.org/3.5/reference/datamodel.html#object.__getitem__ say, KeyError should be raised
        raise KeyError('Unknown Characteristic {i}?'.format(i=item))

    def get_short(self, uuid: str):
        """
        Returns the short type for a given UUID. That means that "0000006D-0000-1000-8000-0026BB765291" and "6D" both
        translates to "position.current" (after looking up "public.hap.characteristic.position.current").

        if item in self._characteristics:
            return self._characteristics[item].split('.', 3)[3]
        :param uuid: the UUID in long form or the shortened version as defined in chapter 5.6.1 page 72.
        :return: the textual representation
        """
        orig_item = uuid
        if uuid.endswith(self.baseUUID):
            uuid = uuid.split('-', 1)[0]
            uuid = uuid.lstrip('0')

        if uuid in self._characteristics:
            return self._characteristics[uuid].split('.', maxsplit=3)[3]

        return 'Unknown Characteristic {i}'.format(i=orig_item)

    def get_short_uuid(self, item_name):
        """
        Returns the short UUID for either a full UUID or textual characteristic type name. For information on
        full and short UUID consult chapter 5.6.1 page 72 of the specification. It also supports to pass through full
        non-HomeKit UUIDs.

        :param item_name: either the type name (e.g. "public.hap.characteristic.position.current") or the short UUID as
                          string or a HomeKit specific full UUID.
        :return: the short UUID (e.g. "6D" instead of "0000006D-0000-1000-8000-0026BB765291")
        :raises KeyError: if the input is neither a UUID nor a type name. Specific error is given in the message.
        """
        orig_item = item_name
        if item_name.endswith(self.baseUUID):
            item_name = item_name.split('-', 1)[0]
            return item_name.lstrip('0')
        if item_name in self._characteristics:
            return item_name
        if item_name in self._characteristics_rev:
            return self._characteristics_rev[item_name]
        try:
            uuid.UUID('{{{s}}}'.format(s=item_name))
            return item_name
        except ValueError:
            raise KeyError('No short UUID found for Item {item}'.format(item=orig_item))

    def get_uuid(self, item_name):
        """
        Returns the full length UUID for either a shorted UUID or textual characteristic type name. For information on
        full and short UUID consult chapter 5.6.1 page 72 of the specification. It also supports to pass through full
        HomeKit UUIDs.

        :param item_name: either the type name (e.g. "public.hap.characteristic.position.current") or the short UUID or
                          a HomeKit specific full UUID.
        :return: the full UUID (e.g. "0000006D-0000-1000-8000-0026BB765291")
        :raises KeyError: if the input is neither a short UUID nor a type name. Specific error is given in the message.
        """
        orig_item = item_name
        # if we get a full length uuid with the proper base and a known short one, this should also work.
        if item_name.endswith(self.baseUUID):
            item_name = item_name.split('-', 1)[0]
            item_name = item_name.lstrip('0')
        if item_name in self._characteristics_rev:
            short = self._characteristics_rev[item_name]
        elif item_name in self._characteristics:
            short = item_name
        else:
            raise KeyError('No UUID found for Item {item}'.format(item=orig_item))
        medium = '0' * (8 - len(short)) + short
        long = medium + self.baseUUID
        return long


#
#   Have a singleton to avoid overhead
#
CharacteristicsTypes = _CharacteristicsTypes()


class _ServicesTypes(object):
    """
    This data is taken from Table 12-3 Accessory Categories on page 254. Values above 19 are reserved.
    """
    INFORMATION_SERVICE = 'A2'  # new for ble, page 126
    PAIRING_SERVICE = '55'      # new for ble, page 57

    def __init__(self):
        self.baseUUID = '-0000-1000-8000-0026BB765291'
        self._services = {
            '3E': 'public.hap.service.accessory-information',
            '40': 'public.hap.service.fan',
            '41': 'public.hap.service.garage-door-opener',
            '43': 'public.hap.service.lightbulb',
            '44': 'public.hap.service.lock-management',
            '45': 'public.hap.service.lock-mechanism',
            '47': 'public.hap.service.outlet',
            '49': 'public.hap.service.switch',
            '4A': 'public.hap.service.thermostat',
            '55': 'public.hap.service.pairing',                             # new for ble, page 57
            '7E': 'public.hap.service.security-system',
            '7F': 'public.hap.service.sensor.carbon-monoxide',
            '80': 'public.hap.service.sensor.contact',
            '81': 'public.hap.service.door',
            '82': 'public.hap.service.sensor.humidity',
            '83': 'public.hap.service.sensor.leak',
            '84': 'public.hap.service.sensor.light',
            '85': 'public.hap.service.sensor.motion',
            '86': 'public.hap.service.sensor.occupancy',
            '87': 'public.hap.service.sensor.smoke',
            '89': 'public.hap.service.stateless-programmable-switch',
            '8A': 'public.hap.service.sensor.temperature',
            '8B': 'public.hap.service.window',
            '8C': 'public.hap.service.window-covering',
            '8D': 'public.hap.service.sensor.air-quality',
            '96': 'public.hap.service.battery',
            '97': 'public.hap.service.sensor.carbon-dioxide',
            'A2': 'public.hap.service.protocol.information.service',        # new for ble, page 126
            'B7': 'public.hap.service.fanv2',
            'B9': 'public.hap.service.vertical-slat',
            'BA': 'public.hap.service.filter-maintenance',
            'BB': 'public.hap.service.air-purifier',
            'CC': 'public.hap.service.service-label',
            '110': 'public.hap.service.camera-rtp-stream-management',
            '112': 'public.hap.service.microphone',
            '113': 'public.hap.service.speaker',
            '121': 'public.hap.service.doorbell',
        }

        self._services_rev = {self._services[k]: k for k in self._services.keys()}

    def __getitem__(self, item):
        if item in self._services:
            return self._services[item]

        if item in self._services_rev:
            return self._services_rev[item]

        # raise KeyError('Item {item} not found'.format_map(item=item))
        return 'Unknown Service: {i}'.format(i=item)

    def get_short(self, item):
        orig_item = item
        if item.endswith(self.baseUUID):
            item = item.split('-', 1)[0]
            item = item.lstrip('0')

        if item in self._services:
            return self._services[item].split('.')[-1]
        return 'Unknown Service: {i}'.format(i=orig_item)

    def get_uuid(self, item_name):
        if item_name not in self._services_rev:
            raise Exception('Unknown service name')
        short = self._services_rev[item_name]
        medium = '0' * (8 - len(short)) + short
        long = medium + self.baseUUID
        return long


#
#   Have a singleton to avoid overhead
#
ServicesTypes = _ServicesTypes()


class AnyDevice(gatt.gatt_linux.Device):
    def services_resolved(self):
        super().services_resolved()
        logging.debug('resolved %d services', len(self.services))
        self.manager.stop()
        logging.debug('stopped manager')

        self.a_data = {
            'services': []
        }
        for service in self.services:
            logging.debug('found service with UUID %s (%s)', service.uuid, ServicesTypes.get_short(service.uuid.upper()))
            s_data = {
                'sid': None,
                'type': service.uuid.upper(),
                'characteristics': []
            }
            self.a_data['services'].append(s_data)
            for characteristic in service.characteristics:
                logging.debug('\tfound characteristic with UUID %s (%s)', characteristic.uuid, CharacteristicsTypes.get_short(characteristic.uuid.upper()))

                if characteristic.uuid.upper() == CharacteristicsTypes.SERVICE_INSTANCE_ID:
                    sid = int.from_bytes(characteristic.read_value(), byteorder='little')
                    logging.debug('\t\tread service id %d', sid)
                    s_data['sid'] = sid
                else:
                    c_data = {
                        'cid': None,
                        'type': characteristic.uuid.upper(),
                        'perms': []
                    }
                    s_data['characteristics'].append(c_data)
                    cid = None
                    for descriptor in characteristic.descriptors:
                        value = descriptor.read_value()
                        if descriptor.uuid == CharacteristicInstanceID:
                            cid = int.from_bytes(value, byteorder='little')
                            logging.debug('\t\tread characteristic id %d', cid)
                            c_data['cid'] = cid
                        else:
                            # print('\t\t', 'D', descriptor.uuid, value)
                            pass

                    if cid:
                        v = cid.to_bytes(length=2, byteorder='little')
                        tid = 42
                        characteristic.write_value([0x00, 0x01, tid, v[0], v[1]])
                        d = parse_sig_read_response(characteristic.read_value(), tid)
                        for k in d:
                            c_data[k] = d[k]

        logging.debug('disconnecting from device')
        self.disconnect()
        logging.debug('disconnected from device')
        self.manager.stop()
        logging.debug('manager stopped')


if __name__ == '__main__':
    arg_parser = ArgumentParser(description="GATT Connect Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('--log', action='store', dest='loglevel')
    args = arg_parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s')
    if args.loglevel:
        getattr(logging, args.loglevel.upper())
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        logging.getLogger().setLevel(numeric_level)

    manager = gatt.DeviceManager(adapter_name='hci0')

    device = AnyDevice(manager=manager, mac_address=args.mac_address)
    logging.debug('connecting to device')
    device.connect()
    logging.debug('connected to device')

    try:
        logging.debug('start manager')
        manager.run()
    except:
        device.disconnect()

    print('-' * 20, 'human readable', '-' * 20)
    for service in device.a_data['services']:
        s_type = service['type']
        s_iid = service['sid']
        # print('{iid}: >{stype}<'.format(iid=s_iid, stype=ServicesTypes.get_short(s_type)))

        for characteristic in service['characteristics']:
            c_iid = characteristic['cid']
            value = characteristic.get('value', '')
            c_type = characteristic['type']
            perms = ','.join(characteristic['perms'])
            desc = characteristic.get('description', '')
            c_type = CharacteristicsTypes.get_short(c_type)
            print('  {aid}.{iid}: {value} ({description}) >{ctype}< [{perms}]'.format(aid=s_iid,
                                                                                      iid=c_iid,
                                                                                      value=value,
                                                                                      ctype=c_type,
                                                                                      perms=perms,
                                                                                      description=desc))

    print('-' * 20, 'json', '-' * 20)
    json_services = []
    for service in device.a_data['services']:
        json_characteristics = []
        json_service = {
            'type': service['type'],
            'iid': service['sid'],
            'characteristics': json_characteristics
        }
        for characteristic in service['characteristics']:
            json_characteristic = {
                'type': characteristic['type'],
                'description': characteristic.get('description', ''),
                'iid': characteristic['cid'],
                'value': characteristic.get('value', ''),
                'perms': characteristic['perms'],
                'format': characteristic['format'],
                'unit': characteristic['unit'],
                'range': str(characteristic['range']),
                'step': str(characteristic['step']),
            }
            json_characteristics.append(json_characteristic)
        json_services.append(json_service)
    json_data = [{'aid':1,'services': json_services}]
    print(json.dumps(json_data, indent=4))
    