class BusPark:
    def __init__(self):
        self.bus_list = []

    def add_bus(self, bus, create: bool = False):
        if not create:
            bus.route.remove_bus(bus)
        self.bus_list.append(bus)

    def remove_bus(self, bus):
        self.bus_list.remove(bus)

    def get_parked_buses(self):
        return self.bus_list