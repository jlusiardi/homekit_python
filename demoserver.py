#!/usr/bin/env python3

import os.path

from homekit import HomeKitServer

from homekit.model import Accessory, LightBulbService


def light_switched(newval):
    print('=======>  light switched: {x}'.format(x=newval))


if __name__ == '__main__':
    try:
        httpd = HomeKitServer(os.path.expanduser('~/.homekit/demoserver.json'))

        accessory = Accessory('Testlicht')
        lightBulbService = LightBulbService()
        lightBulbService.set_on_set_callback(light_switched)
        accessory.services.append(lightBulbService)
        httpd.accessories.add_accessory(accessory)

        print(httpd.accessories.__str__())

        httpd.publish_device()
        print('published device and start serving')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('unpublish device')
        httpd.unpublish_device()
