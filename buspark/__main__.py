from .bus import Bus
from .park import BusPark
from .route import Route
from .exceptions import ReturnMenu, SelectedNonExistentBus


class BusStation:
    def __init__(self) -> None:
        self.park = BusPark()
        self.routes: list[Route] = []
        self.buses: list[Bus] = []

    def show_menu(self):
        options = (
            {
                'title': 'Вийти',
                'callback': lambda: exit('Чекаємо на Вас знову!')
            },
            {
                'title': 'Створити автобус та додати його у парк',
                'callback': self.create_bus
            },
            {
                'title': 'Призначити маршрут автобусу',
                'callback': self.create_bus
            },
            {
                'title': 'Видалити автобус',
                'callback': self.delete_bus
            },
            {
                'title': 'Створити маршрут',
                'callback': self.create_bus
            },
            {
                'title': 'Видалити маршрут',
                'callback': self.create_bus
            },
            {
                'title': 'Відправити автобус на маршрут',
                'callback': self.create_bus
            },
            {
                'title': 'Повернути автобус у парк',
                'callback': self.create_bus
            },
            {
                'title': 'Вивести список автобусів на маршрутах',
                'callback': self.create_bus
            },
            {
                'title': 'Вивести список автобусів у парку',
                'callback': self.create_bus
            }
        )

        msg = ''
        for option_index, option in enumerate(options):
            msg += f"[{option_index}] - {option.get('title')}\n"
        
        try:
            choosed_option: int = int(input(msg))
        except ValueError as ex:
            print('[!] Необхідно ввести саме цифру/число.')
            return self.show_menu()
        else:
            if choosed_option in range(len(options)):
                return options[choosed_option]['callback']()
            print('[!] Обрана неіснуюча опція :(')
            return self.show_menu()


    def create_bus(self):
        bus_number, driver_name = (
            input('Введіть назву автобусу: '),
            input('Введіть ім\'я водія: ')
        )
        bus = Bus(bus_number, driver_name)
        self.park.add_bus(bus)
        self.buses.append(bus)
        print('Автобус успішно створено та відправлено до парку!')
        return self.show_menu()


    def delete_bus(self):
        if not self.buses:
            print('Жодного автобусу не існує, пропонуємо створити хоч якийсь!')
            return self.show_menu()

        try:
            selected_bus = self._get_selected_bus_from_input()
        except SelectedNonExistentBus:
            print("Обрано неіснуючий автобус!")
            return self.show_menu()
        except ReturnMenu:
            return self.show_menu()
        match selected_bus.status:
            case 'У парку':
                self.park.remove_bus(selected_bus)
            case 'На маршруті':
                selected_bus.route.remove_bus(selected_bus)

        self.buses.remove(selected_bus)
        print('Автобус було вдало видалено!')
        return self.show_menu()
    

    def set_route_for_bus(self): pass


    
    def _get_selected_bus_from_input(self) -> Bus:
        msg = ''
        for option_index, bus in enumerate(self.buses):

            msg += f'[{option_index}] - автобус под номером {str(bus)}\n'
        msg += f'{len()} - вернуться в меню'

        try:
            selected_option = int(input(f'{msg}'))
        except ValueError:
            print('Введено не цифру/число!')
            return self._get_selected_bus_from_input()
        else:
            if selected_option in range(len(options)):
                if selected_option == len(options):
                    raise ReturnMenu()
                selected_bus = options[selected_option]
                return selected_bus
            else:
                raise SelectedNonExistentBus()
            
    
    def _get_selected_route_from_input(self):
        msg = ''
        existing_bus_numbers = [bus.number for bus in self.buses]
        options = []
        for option_index, bus in enumerate(self.buses):
            options.append(
                {
                'option': option_index,
                'bus': bus 
                }
            )
            msg += f'[{option_index}] - автобус под номером {bus_number}\n'

        try:
            selected_option = int(input(f'{msg}'))
        except ValueError as ex:
            print('Введено не цифру/число!')
            return self.show_menu()
        else:
            if selected_option in range(len(options)):
                selected_bus_number = options[selected_option]['bus_number']
                return selected_bus_number
            else:
                raise SelectedNonExistentBus("Обрано неіснуючий автобус!")

            

if __name__ == '__main__':
    # # Создание автобусов
    # bus1 = Bus("A1", "Водій 1", "Маршрут 1")
    # bus2 = Bus("B2", "Водій 2", "Маршрут 2")

    # # Создание парка и маршрута
    # bus_park = BusPark()
    # route = Route()

    # # Добавление автобусов в парк
    # bus_park.add_bus(bus1)
    # bus_park.add_bus(bus2)


    # # Создание симуляции
    # simulation = Simulation(bus_park, route)

    # # Запуск симуляции
    # simulation.bus_departure(bus1)
    # simulation.bus_departure(bus2)
    # departed_buses = route.get_buses_on_route()
    # print(f"Автобуси, що знаходяться на разі у рейсі: {', '.join(bus.number for bus in departed_buses)} \n\n")

    # # Пауза для имитации работы автобусов
    # simulation.analyze_performance()
    # time.sleep(5)
    # simulation.analyze_performance()

    # # Прибытие автобусов в парк
    # simulation.bus_arrival(bus1)
    # simulation.bus_arrival(bus2)

    # parked_buses = bus_park.get_parked_buses()
    # print(f"Автобуси, що знаходяться на разі у парку: {', '.join(bus.number for bus in parked_buses)}")
    # # Анализ производительности автобусов на маршруте
    # simulation.analyze_performance()
    # simulation.bus_arrival(bus2)
    BusStation().show_menu()