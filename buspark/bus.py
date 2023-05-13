from .route import Route

class Bus:
    def __init__(self, bus_number, driver_name):
        self.number = bus_number
        self.driver_name = driver_name
        self.route: Route = None
        self.status: str = "У парку"
        self.performance = 0
        self.num_trips = 0
        self.last_departure_time = 0
        self.last_arrival_time = 0

    
    def __str__(self) -> str:
        return f'автобус під номером {self.number}'
