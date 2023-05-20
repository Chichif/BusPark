from typing import Self
from pydantic import BaseModel
from datetime import (timedelta, 
                      datetime)

from models import (City,
                    Driver,
                    Bus,
                    Park,
                    Route,
                    Departure)
from exceptions import (ReturnMenu,
                        NoBusesWithRoute)
from decorators import (are_here_buses,
                        are_here_buses_tied_to_route,
                        are_here_departures, 
                        are_here_routes,
                        are_here_departed_buses,
                        are_here_free_buses)
from formatters import timedelta_to_str


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
    __instance = None

    
    def __new__(mcs, *args, **kwargs) -> Self:
        if not mcs.__instance:
            mcs.__instance = super().__new__(mcs, *args, **kwargs)
        return mcs.__instance


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

        bus_number,  driver_first_name, driver_second_name = (
            input("Введіть номер автобусу: "),
            input("Введіть ім'я водія: "),
            input("Введіть фамілію водія: ")
        )
        if bus_number in (bus.number for bus in self.bus_list):
            print("\n\n[!] Автобус з таким номером вже існує!")
            return self.create_bus()
        driver = Driver(first_name = driver_first_name, second_name = driver_second_name)
        bus = Bus(number = bus_number, driver = driver)
        self.park.add_bus(bus)
        self.bus_list.append(bus)
        return self.show_menu(f"""
            {str(bus)[0].capitalize() + str(bus)[1:]} успішно створено та відправлено до парку!
        """.strip()) # str.capitalize() - не підходить, оскільки останні символи строки переводить у нижній регістр

    @are_here_buses
    @are_here_buses_tied_to_route
    @are_here_routes
    @are_here_free_buses
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
        

    @are_here_buses
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
        

    @are_here_buses
    @are_here_routes
    @are_here_departed_buses
    def show_departed_buses(self):
        """
        Метод для відображення списку автобусів у дорозі.

        Виводиться список автобусів, які знаходяться у дорозі разом з назвами маршрутів та часом у дорозі.

        Повертає: None
        """
        options = []
        for index, departure in enumerate(self.active_departures):
            options.append(f"[{index} - {departure.bus} | {departure.bus.route} | у дорозі {timedelta_to_str(departure.travel_time)}]")
        return self.show_menu("\n".join(options))
    

    @are_here_buses
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


    @are_here_buses
    @are_here_routes
    def set_route_for_bus(self):
        """
        Метод для призначення маршруту для автобуса.

        Користувачеві буде запропоновано вибрати автобус та маршрут зі списку.
        Після вибору, перевіряється поточний маршрут автобуса. Якщо він вже співпадає з обраним,
        виводиться повідомлення про це. В іншому випадку, маршрут для автобуса змінюється,
        а автобус додається до нового маршруту.

        Якщо до цього 

        Повертає: None
        """
        try:
            selected_bus = self._get_selected_object_from_input(self.bus_list)
            selected_route = self._get_selected_object_from_input(self.route_list)
        except ReturnMenu:
            return self.show_menu()
        else:
            bus_active_departure = self._get_bus_active_departure(selected_bus)

            if selected_bus.route:
                if selected_bus.route is selected_route:
                    return self.show_menu("[!] Обрано один й той самий маршрут для автобусу, ніяких змін не внесено.")
                
                msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}'"
                if bus_active_departure:
                    bus_active_departure.finish_travel()
                    self.park.add_bus(selected_bus)
                    msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}', а рейс зупинено!\nАвтобус повернено у парк."

                selected_bus.route = selected_route
                return self.show_menu(msg)
            
            msg = f"Для автобусу встановлено {selected_route}"
            selected_bus.route = selected_route
            return self.show_menu(msg)


    @are_here_buses
    def delete_bus(self):
        """
        Метод для видалення автобуса.

        Користувачу будуть запропоновані вибрати автобус зі списку, який потрібно видалити.
        Вибраний автобус буде видалений зі списку автобусів та зі зв'язаного з ним маршруту (якщо такий існує).
        Активне відправлення з цим автобусом буде завершено.

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
    

    @are_here_buses
    @are_here_routes
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
    

    @are_here_routes
    def delete_route(self):
        """
        Метод для видалення маршруту.

        Користувачу будуть запропоновані вибрати маршрут зі списку, який потрібно видалити.
        Вибраний маршрут буде видалений зі списку маршрутів.
        Усі автобуси, пов'язані з видаленим маршрутом, будуть повернуті до парку автобусів.
        Діючі відправлення за цим маршрутом будуть зупинені.

        Повертає: None
        """
        try:
            selected_route: Route = self._get_selected_object_from_input(self.route_list)
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
    

    @are_here_buses
    @are_here_departures
    def show_analytics(self):
        """

        Підраховує кількість рейсів для кожного автобуса та обчислює загальний час, 
        витрачений на кожен рейс. Виводить інформацію відповідно до заданого формату.

        :return: Повертає результат функції `show_menu()`.


        Алгоритм роботи функції:

        Список self.bus_list сортується за номером автобуса.

        Для кожного автобуса:
        - Виводиться заголовок рейсів для даного автобуса.
        - Ініціалізуються змінні total_count і total_time для підрахунку загальної кількості рейсів та часу.

        Для кожного відправлення в self.departure_list:
        * Якщо номер автобуса відправлення співпадає з номером поточного автобуса:
                - Збільшується лічильник total_count на 1.
                - Час подорожі перетворюється у формат datetime.
                - Час подорожі додається до загального часу total_time.
                - Виводиться інформація про маршрут та час подорожі.
        * Виводиться загальна кількість рейсів та загальний час для даного автобуса.
        * Повертається результат функції show_menu().
        """
        sorted_buses = sorted(self.bus_list, key = lambda bus: bus.number)

        for bus in sorted_buses:
            print(f"\n\nРейсы '{bus.number} з водієм {bus.driver.first_name}'")
            total_count = 0
            total_time = timedelta()

            for departure in self.departure_list:
                if departure.bus.number == bus.number:
                    total_count += 1
                    total_time += departure.travel_time
                    print(f'{departure.route} | {timedelta_to_str(departure.travel_time)}')

            print(f"Ітого - {total_count} за {timedelta_to_str(total_time)}")

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
    def not_departed_buses(self) -> list[Bus]:
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
            
    
    def _is_answer_existent(self, options: list[str], selected_option: int) -> bool:
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