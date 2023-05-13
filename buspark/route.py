class Route:
    def __init__(self, start_point: str, end_point: str):
        self.start_point: str = start_point
        self.end_point: str = end_point

    def add_bus(self, bus):
        bus.status = 'На маршруті'
        bus.route = self
        self.bus_list.append(bus)

    def remove_bus(self, bus):
        self.bus_list.remove(bus)

    def get_buses_on_route(self):
        return self.bus_list
    
