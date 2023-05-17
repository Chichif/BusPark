from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class City(BaseModel):
    title: str

    def __str__(self) -> str:
        return self.title


class Route(BaseModel):
    start_point: City
    end_point: City

    
    def __str__(self) -> str:
        return f'маршрут {self.start_point} - {self.end_point}'
    

class BusStatusEnum(str, Enum):
    ON_THE_ROAD = 'У дорозі'
    IN_THE_PARKING = 'У парку'


class Driver(BaseModel):
    first_name: str
    second_name: str

    @property
    def initials(self):
        return f"{self.first_name[0].capitalize()}. {self.second_name[0].capitalize()}."
    
    def __str__(self) -> str:
        return self.initials


class Bus(BaseModel):
    number: str
    driver: Driver
    route: Route = None
    status: BusStatusEnum = BusStatusEnum.IN_THE_PARKING

    def __str__(self) -> str:
        return f'автобус {self.number} з водієм {self.driver}'


class Departure(BaseModel): 
    bus: Bus
    route: Route
    departure_time: datetime = None
    arrival_time: datetime | None = None


    def start_travel(self):
        self.departure_time = datetime.now()
        self.bus.status = BusStatusEnum.ON_THE_ROAD


    def finish_travel(self):
        self.arrival_time = datetime.now()
        self.bus.status = BusStatusEnum.IN_THE_PARKING


    @property
    def travel_time(self) -> str:
        if not self.arrival_time:
            time_difference = datetime.now() - self.departure_time
        else:
            time_difference = self.arrival_time - self.departure_time
        hours = time_difference.total_seconds() // 3600
        minutes = (time_difference.total_seconds() // 60) % 60
        seconds = time_difference.total_seconds() % 60

        time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return time_str


class Park(BaseModel):
    bus_list: list[Bus] = []

    def add_bus(self, bus: Bus):
        self.bus_list.append(bus)
    
    def remove_bus(self, bus: Bus):
        self.bus_list.remove(bus)

    @property
    def parked_buses(self):
        return self.bus_list
