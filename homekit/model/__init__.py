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

    def get_name(self):
        for service in self.services:
            if isinstance(service, AcessoryInformationService):
                return service.get_name()
        return None


class Accessories(ToDictMixin):
    def __init__(self):
        self.accessories = []

    def add_accessory(self, acessory: Accessory):
        self.accessories.append(acessory)
