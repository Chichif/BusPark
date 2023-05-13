class Route:
    def __init__(self, start_point: str, end_point: str):
        self.start_point: str = start_point
        self.end_point: str = end_point
        self.bus_list = []

    def add_bus(self, bus):
        bus.route = self
        self.bus_list.append(bus)

    def remove_bus(self, bus):
        bus.route = None
        self.bus_list.remove(bus)

    def get_buses_on_route(self):
        return self.bus_list
    
    def __str__(self) -> str:
        return f'маршрут {self.start_point} - {self.end_point}'
    
