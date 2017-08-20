from homekit.model.characteristics import CharacteristicsTypes
from homekit.model.mixin import ToDictMixin, get_id
from homekit.model.services import AcessoryInformationService, LightBulbService, OutletService, FanService, \
    ThermostatService
from homekit.model.categories import Categories


class Accessory(ToDictMixin):
    def __init__(self, name):
        self.aid = get_id()
        self.services = [
            AcessoryInformationService(name)
        ]


class Accessories(ToDictMixin):
    def __init__(self):
        self.accessories = []

    def add_accessory(self, acessory: Accessory):
        self.accessories.append(acessory)
