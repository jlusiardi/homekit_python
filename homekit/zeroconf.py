from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
from socket import inet_ntoa

from homekit.feature_flags import FeatureFlags
from homekit.categories import Categories


class HomeKitListener(object):
    def remove_service(self, zeroconf, type, name):
        # this is ignored since not interested in disappearing stuff
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print('Name: {name}'.format(name=name))
        print('Url: http://{ip}:{port}'.format(ip=inet_ntoa(info.address), port=info.port))
        print('Configuration number (c#): {conf}'.format(conf=info.properties[b'c#'].decode()))
        flags = int(info.properties[b'ff'].decode())
        print('Feature Flags (ff): {f} (Flag: {flags})'.format(f=FeatureFlags[flags], flags=flags))
        print('Device ID (id): {id}'.format(id=info.properties[b'id'].decode()))
        print('Model Name (md): {md}'.format(md=info.properties[b'md'].decode()))
        print('Protocol Version (pv): {pv}'.format(pv=info.properties[b'pv'].decode()))
        print('State Number (s#): {sn}'.format(sn=info.properties[b's#'].decode()))
        print('Status Flags (sf): {sf}'.format(sf=info.properties[b'sf'].decode()))
        category = int(info.properties[b'ci'].decode())
        print('Category Identifier (ci): {c} (Id: {ci})'.format(c=Categories[category], ci=category))
        print()


def discover_homekit_devices():
    zeroconf = Zeroconf()
    listener = HomeKitListener()
    browser = ServiceBrowser(zeroconf, '_hap._tcp.local.', listener)
    sleep(1)
    zeroconf.close()
