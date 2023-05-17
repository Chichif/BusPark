'''
Наданий код, здається, є реалізацією системи управління автовокзалом на мові Python. Клас BusStation представляє автовокзал та надає методи для управління автобусами, маршрутами та взаємодією між ними.

Основні компоненти такі:

Атрибути класу:

park: Екземпляр класу BusPark, що представляє автостоянку.
routes: Список об'єктів класу Route, що представляють доступні маршрути.
buses: Список об'єктів класу Bus, що представляють автобуси на вокзалі.
Методи:

__init()__: Ініціалізує об'єкт класу BusStation з порожньою автостоянкою, маршрутами та автобусами.
show_menu(): Відображає меню з варіантами і обробляє вибрані дії.
create_bus(): Створює новий автобус і додає його на автостоянку та до списку автобусів.
delete_bus(): Видаляє автобус із списку автобусів та видаляє його з пов'язаного маршруту, якщо це застосовно.
create_route(): Створює новий маршрут і додає його до списку маршрутів.
delete_route(): Видаляє маршрут із списку маршрутів та повертає пов'язані автобуси на автостоянку.
show_route_buses(): Відображає автобуси, пов'язані з обраним маршрутом.
show_buses_in_routes(): Відображає автобуси, які знаходяться на маршрутах.
show_buses_in_park(): Відображає автобуси, які знаходяться на автостоянці.
set_route_for_bus(): Призначає маршрут для обраного автобуса та оновлює його поточний маршрут.
return_bus_to_park(): Повертає автобус на автостоянку та видаляє його поточний маршрут.
Код використовує кілька користувацьких декораторів (are_there_buses та are_there_routes), щоб перевірити на наявність автобусів або маршрутів перед виконанням певних методів.

Загалом, цей код надає основну структуру для управління автобусами та маршрутами на автовокзалі.
'''
from collections import defaultdict
from pydantic import BaseModel
from datetime import (timedelta, 
                      datetime)

from models import (City,
                    Bus,
                    Park,
                    Route,
                    Departure,
                    BusStatusEnum)
from exceptions import (ReturnMenu,
                        NoBusesWithRoute)
from decorators import (are_there_buses, 
                        are_there_departures, 
                        are_there_routes,
                        are_there_departed_buses)


class AutoStation(BaseModel):
    """
    Клас AutoStation представляє автобусну станцію.

    Атрибути:
    - park: Park - парк автобусів
    - route_list: list[Route] - список маршрутів
    - bus_list: list[Bus] - список автобусів
    - departure_list: list[Departure] - список всіх відправлень автобусів
    """
    park = Park()
    route_list: list[Route] = []
    bus_list: list[Bus] = []
    departure_list: list[Departure] = []


    def show_menu(self, menu_msg: str = None):
        """
        Метод для відображення меню та обробки вибраних опцій.

        Приймає необов'язковий аргумент menu_msg для виведення додаткового повідомлення у меню.

        Параметри:
        - menu_msg: str - повідомлення меню (опціонально)

        Повертає:
        None
        """

        if menu_msg: print(menu_msg)
        options = (
            {
                "title": 'Вийти',
                "callback": lambda: exit('Чекаємо на Вас знову!')
            },
            {
                "title": 'Створити автобус та додати його у парк',
                "callback": self.create_bus
            },
            {
                "title": 'Призначити маршрут автобусу',
                "callback": self.set_route_for_bus
            },
            {
                "title": 'Відправити автобус на маршрут',
                "callback": self.depart_bus
            },
            {
                "title": 'Повернути автобус у парк',
                "callback": self.return_bus_to_park
            },
            {
                "title": 'Видалити автобус',
                "callback": self.delete_bus
            },
            {
                "title": 'Створити маршрут',
                "callback": self.create_route
            },
            {
                "title": 'Видалити маршрут',
                "callback": self.delete_route
            },
            {
                "title": 'Вивести список автобусів у дорозі',
                "callback": self.show_departed_buses
            },
            {
                "title": 'Вивести список автобусів у парку',
                "callback": self.show_buses_in_park
            },
            {
                "title": 'Вивести список автобусів певного маршруту',
                "callback": self.show_route_buses
            },
            {
                "title": "Вивести аналітику роботи автобусів",
                "callback": self.show_analytics
            }
        )

        text = "\n\n"
        for option_index, option in enumerate(options):
            text += f'[{option_index}] - {option.get("title")}\n'

        try:
            choosed_option = int(input(text))
        except ValueError as ex:
            return self.show_menu("[!] Необхідно ввести саме цифру/число.")
        else:
            if choosed_option in range(len(options)):
                options[choosed_option]["callback"]()
            return self.show_menu("[!] Обрана неіснуюча опція :(")


    def create_bus(self):
        """
        Метод для створення нового автобуса та додавання його до парку.
        Користувачу будуть запропоновані ввести номер автобуса та ім'я водія.
        Після цього автобус буде створено, додано до парку та до списку автобусів.

        Повертає:
        None
        """

        bus_number, driver_name = (
            input('Введіть номер автобусу: '),
            input('Введіть ім\'я водія: ')
        )
        if bus_number in (bus.number for bus in self.bus_list):
            print("\n\n[!] Автобус з таким номером вже існує!")
            return self.create_bus()
        bus = Bus(number = bus_number, driver_name = driver_name)
        self.park.add_bus(bus)
        self.bus_list.append(bus)
        return self.show_menu(f"""
            {str(bus)[0].capitalize() + str(bus)[1:]} успішно створено та відправлено до парку!
        """.strip()) # str.capitalize() - не підходить, оскільки останні символи строки переводить у нижній регістр


    @are_there_buses
    @are_there_routes
    def depart_bus(self):
        """
        Метод для відправлення автобусу.

        Перевіряє наявність доступних автобусів.
        Вибирає обраний автобус для відправлення.
        Створює об'єкт Departure з вибраним автобусом і маршрутом.
        Видаляє обраний автобус з парку.
        Починає подорож обраного автобусу.
        Додає об'єкт Departure до списку відправлень.

        Повертає меню з повідомленням про успішне відправлення автобусу.
        """
        if not self.buses_tied_to_route:
            return self.show_menu("[!] Жодного автобусу з прив'язаним маршрутом не існує!")
        
        if not self.not_departed_buses:
            return self.show_menu("[!] Усі автобуси у дорозі, вільних немає!")
        
        try:
            selected_bus = self._get_selected_object_from_input(self.not_departed_buses)
        except ReturnMenu:
            return self.show_menu()
        else:
            departure = Departure(bus = selected_bus, route = selected_bus.route)
            self.park.remove_bus(selected_bus)
            departure.start_travel()
            self.departure_list.append(departure)
            return self.show_menu(f"""
                {str(selected_bus)[0].capitalize() + str(selected_bus)[1:]} відправлено у {selected_bus.route}!
            """.strip()) # str.capitalize() - не підходить, оскільки останні символи строки переводить у нижній регістр
        

    @are_there_buses
    def return_bus_to_park(self):
        """
        Метод для повернення автобуса до парку.

        Користувачеві буде запропоновано вибрати автобус зі списку.
        Після вибору, перевіряється поточний маршрут автобуса.
        Якщо автобус вже знаходиться у парку, виводиться відповідне повідомлення.
        В іншому випадку, автобус повертається до парку, його маршрут знімається.

        Повертає: None
        """
        if not self.active_departures:
            return self.show_menu("[!] Всі автобуси наразі у парку!")

        try:
            selected_bus = self._get_selected_object_from_input([departure.bus for departure in self.active_departures])
        except ReturnMenu:
            return self.show_menu()
        else:
            msg = f"Автобус вдало повернено до парку та знято з '{str(selected_bus.route)}'"
            bus_departure: Departure = self._get_bus_active_departure(selected_bus) # гарантовано, що має бути лише один результат
            bus_departure.finish_travel()
            self.park.add_bus(selected_bus)
            return self.show_menu(msg)
        

    @are_there_buses
    @are_there_routes
    @are_there_departed_buses
    def show_departed_buses(self):
        """
        Метод для відображення списку автобусів у дорозі.

        Виводиться список автобусів, які знаходяться у дорозі разом з назвами маршрутів та часом у дорозі.

        Повертає: None
        """
        options = []
        for index, departure in enumerate(self.active_departures):
            options.append(f"[{index} - {departure.bus} | {departure.bus.route} | у дорозі {departure.travel_time}]")
        return self.show_menu("\n".join(options))
    

    @are_there_buses
    def show_buses_in_park(self):
        """
        Метод для відображення списку автобусів у парку.

        Виводиться список автобусів, які знаходяться у парку автобусів.

        Повертає: None
        """
        if not self.park.parked_buses:
            return self.show_menu("[!] Парк пустий!")
        
        for index, bus in enumerate(self.park.parked_buses, 1):
            print(f"[{index}] - {bus}")
        return self.show_menu()


    @are_there_buses
    @are_there_routes
    def set_route_for_bus(self):
        """
        Метод для призначення маршруту для автобуса.

        Користувачеві буде запропоновано вибрати автобус та маршрут зі списку.
        Після вибору, перевіряється поточний маршрут автобуса. Якщо він вже співпадає з обраним,
        виводиться повідомлення про це. В іншому випадку, маршрут для автобуса змінюється,
        а автобус додається до нового маршруту.

        Повертає: None
        """
        try:
            selected_bus = self._get_selected_object_from_input(self.bus_list)
            selected_route = self._get_selected_object_from_input(self.route_list)
        except ReturnMenu:
            return self.show_menu()
        else:
            if selected_bus.route:
                if selected_bus.route is selected_route:
                    return self.show_menu("[!] Обрано один й той самий маршрут для автобусу, ніяких змін не внесено.")
                
                msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}'"
                bus_active_departure = self._get_bus_active_departure(selected_bus)
                if bus_active_departure:
                    bus_active_departure.finish_travel()
                    msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}', а рейс зупинено!"

                selected_bus.route = selected_route
                return self.show_menu(msg)
            
            msg = f"Для автобусу встановлено {selected_route}"
            bus_active_departure = self._get_bus_active_departure(selected_bus)
            if bus_active_departure:
                bus_active_departure.finish_travel()
                msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}', а рейс зупинено!"
                self.park.add_bus(selected_bus)

            selected_bus.route = selected_route
            return self.show_menu(msg)


    @are_there_buses
    def delete_bus(self):
        """
        Метод для видалення автобуса.

        Користувачу будуть запропоновані вибрати автобус зі списку, який потрібно видалити.
        Вибраний автобус буде видалений зі списку автобусів та зі зв'язаного з ним маршруту (якщо такий існує).

        Повертає: None
        """
        try:
            selected_bus = self._get_selected_object_from_input(self.bus_list)
        except ReturnMenu:
            return self.show_menu()
        else:
            selected_bus_active_departure = self._get_bus_active_departure(selected_bus)
            if selected_bus_active_departure:
                selected_bus_active_departure.finish_travel()
                self.bus_list.remove(selected_bus)
                return self.show_menu("Автобус було вдало знято з маршруту та видалено!")
            
            self.park.remove_bus(selected_bus)
            self.bus_list.remove(selected_bus)
            return self.show_menu("Автобус було вдало видалено!")
    

    def create_route(self):
        """
        Метод для створення нового маршруту.

        Користувачу будуть запропоновані ввести початкову та кінцеву точки маршруту.
        Після цього маршрут буде створено і додано до списку маршрутів.

        Повертає: None
        """
        start_point, end_point = (
            City(title = input("Початкова точка: ")),
            City(title = input("Кінцева точка: "))
        )
        route = Route(start_point = start_point, end_point = end_point)
        self.route_list.append(route)
        return self.show_menu("Маршрут вдало створено!")
    

    @are_there_buses
    @are_there_routes
    def show_route_buses(self):
        """
        Метод для відображення списку автобусів певного маршруту.

        Користувачу буде запропоновано вибрати маршрут зі списку.
        Після вибору, відображається список автобусів, пов'язаних з обраним маршрутом.

        Повертає: None
        """
        try:
            selected_route = self._get_selected_object_from_input(self.route_list)
        except ReturnMenu:
            return self.show_menu()
        else:
            buses_in_selected_route = self._get_route_buses(selected_route)
            if not buses_in_selected_route:
                return self.show_menu(f"[!] Автобуси у '{selected_route}' відсутні!")
            msg = f"У '{selected_route}' такі автобуси: \n"
            buses = self._compose_objects_list_for_selecting(buses_in_selected_route)
            return self.show_menu(msg + '\n'.join(buses))
    

    @are_there_routes
    def delete_route(self):
        """
        Метод для видалення маршруту.

        Користувачу будуть запропоновані вибрати маршрут зі списку, який потрібно видалити.
        Вибраний маршрут буде видалений зі списку маршрутів.
        Усі автобуси, пов'язані з видаленим маршрутом, будуть повернуті до парку автобусів.

        Повертає: None
        """
        try:
            selected_route = self._get_selected_object_from_input(self.route_list)
        except ReturnMenu:
            return self.show_menu()
        else:
            msg = "Маршрут вдало видалено!"
            for bus in self._get_route_buses(selected_route):
                bus_departure: Departure = self._get_bus_active_departure(bus)
                if bus_departure:
                    bus_departure.finish_travel()
                    self.park.add_bus(bus)
                bus.route = None
            else:
                msg = "Маршрут вдало видалено, а всі його автобуси, що були у дорозі, відправлено до парку!"
            self.route_list.remove(selected_route)
            return self.show_menu(msg)
    

    @are_there_buses
    @are_there_departures
    def show_analytics(self):
        trip_count = defaultdict(int)
        trip_time = defaultdict(timedelta)
        for departure in self.departure_list:
            bus_number = departure.bus.number
            route = departure.route
            travel_time = datetime.strptime(departure.travel_time, "%H:%M:%S")
            time_delta = timedelta(
                hours = travel_time.hour,
                minutes = travel_time.minute,
                seconds = travel_time.second
            )
            key = (bus_number, str(route))
            trip_count[key] += 1    
            trip_time[key] += time_delta

        sorted_buses = sorted(self.bus_list, key = lambda bus: bus.number)
        for bus in sorted_buses:
            print(f"\n\nРейсы '{bus.number}'")
            total_count = 0
            total_time = timedelta(0)
            for trip in trip_count:
                if trip[0] == bus.number:
                    route = trip[1]
                    count = trip_count[trip]
                    time = trip_time[trip]
                    total_count += count
                    total_time += time
                    print(
                        "\n".join(
                            list(
                                f'{route} | {departure.travel_time}' 
                                for departure in self.departure_list 
                                if departure.bus == bus and str(departure.route) == route
                            )
                        )
                    )
            print(f"Итого - {total_count} за {total_time}")

        return self.show_menu()
        
        

    @property
    def active_departures(self) -> list[Departure]:
        """
        Повертає список дійсних відправлень.
        """
        return list(
            filter(lambda departure: departure.arrival_time is None, self.departure_list)
        )
    

    @property
    def departed_buses(self) -> list[Bus]:
        """
        Властивість, яка повертає список відправлених автобусів.

        Перевіряє наявність автобусів, прив'язаних до маршруту.
        Якщо немає автобусів з прив'язаним маршрутом, викликає виключення NoBusesWithRoute.

        Повертає список автобусів, які були відправлені і досі їдуть.
        """
        if not self.buses_tied_to_route:
            raise NoBusesWithRoute()
        return [departure.bus for departure in self.active_departures]
    

    @property
    def not_departed_buses(self):
        """
        Повертає список автобусів прив'язених до маршрутів, які ще не були відправлені.
        """
        return list(
            filter(lambda bus: bus not in self.departed_buses, self.buses_tied_to_route)
        )
    

    @property
    def buses_tied_to_route(self) -> list[Bus]:
        """
        Повертає список автобусів зі списку автобусів, які мають прив'язаний маршрут.
        """
        return list(
            filter(lambda bus: bus.route is not None, self.bus_list)
        ) 
    
    
    def _get_bus_active_departure(self, bus: Bus) -> Departure | None:
        """
        Приватний метод, який повертає активне відправлення для заданого автобуса.
        """
        bus_departure: tuple[Departure] = tuple(
            filter(lambda departure: departure.bus == bus, self.active_departures)
        )
        if bus_departure: # гарантовано, що не більше 1
                          # адже відправити один автобус два рази на маршрут - неможливо
            return bus_departure[0]
        else: 
            return None
        

    def _get_route_buses(self, route: Route) -> list[Bus]:
        """
        Приватний метод, який повертає список автобусів, прив'язаних до вказаного маршруту.
        """
        return list(
            filter(lambda bus: bus.route is route, self.bus_list)
        )


    def _get_selected_object_from_input(self, objects: list[Bus | Route]) -> Bus | Route:
        """
        Метод для отримання обраного об'єкта зі списку.

        Приймає список об'єктів `objects`, з якого користувач має обрати один об'єкт.
        Виводиться список об'єктів для вибору. Після вибору, перевіряється чи обрана опція
        є в списку валідних опцій. Якщо обрана опція є останньою (повернення до меню),
        викликається виняток ReturnMenu. В іншому випадку, повертається обраний об'єкт.

        Параметри:
        - objects (list[Bus | Route]): Список об'єктів для вибору.

        Повертає:
        - Bus | Route: Обраний об'єкт.

        Викидає:
        - ReturnMenu: Якщо обрана опція - повернення до меню.
        """
        options = self._compose_objects_list_for_selecting(objects)
        options.append(f'[{len(options)}] - повернутись до меню: ')

        try:
            selected_option = int(input('\n'.join(options)) + '\n\n')
        except ValueError:
            print('\n\n [!] Введено не цифру/число!')
            return self._get_selected_object_from_input(objects)
        else:
            if self._is_answer_existent(options, selected_option):
                if selected_option == range(len(options))[-1]:
                    raise ReturnMenu()
                selected_object = objects[selected_option]
                return selected_object
            else:
                print("\n\n [!] Обрана неіснуюча опція :(")
                return self._get_selected_object_from_input(objects)
    

    def _compose_objects_list_for_selecting(self, objects: list[Bus | Route]):
        """
        Метод для створення списку об'єктів для вибору.

        Приймає список об'єктів `objects` і створює список опцій для вибору об'єкта.
        Кожна опція має вигляд `[індекс] - назва_об'єкта`.

        Параметри:
        - objects (list[Bus | Route]): Список об'єктів.

        Повертає:
        - list[str]: Список опцій для вибору об'єкта.
        """
        options = []
        for option_index, object in enumerate(objects):
            options.append(
                f"[{option_index}] - {object}"
            )
        return options
            
    
    def _is_answer_existent(self, options: list[str], selected_option: int):
        """
        Метод для перевірки, чи обрана опція існує у списку опцій.

        Приймає список опцій `options` і обрану опцію `selected_option`.
        Перевіряє, чи обрана опція є в діапазоні індексів списку опцій.

        Параметри:
        - options (list[str]): Список опцій.
        - selected_option (int): Обрана опція.

        Повертає:
        - bool: True, якщо обрана опція існує, False - в іншому випадку.
        """
        options_range = range(len(options))
        if selected_option in options_range:
            return True
        else:
            return False
            

if __name__ == "__main__":
   AutoStation().show_menu()