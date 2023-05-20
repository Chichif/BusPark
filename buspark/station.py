from typing import Self
from datetime import timedelta

from models import (City,
                    Driver,
                    Bus,
                    Park,
                    Route,
                    Departure,
                    BusStatusEnum)
from exceptions import (ReturnMenu,
                        NoBusesWithRoute)
from decorators import (are_here_buses,
                        are_here_buses_tied_to_route,
                        are_here_departures, 
                        are_here_routes,
                        are_here_departed_buses,
                        are_here_free_buses)
from serializers import timedelta_to_str
from utils import (get_selected_object_from_input,
                   get_bus_active_departure,
                   get_route_buses,
                   compose_objects_list_for_selection)


class Dispatcher:
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
            selected_bus = get_selected_object_from_input(AutoStation().analytic.not_departed_buses)
        except ReturnMenu:
            return AutoStation().show_menu()
        else:
            departure = Departure(bus = selected_bus, route = selected_bus.route)
            Park().remove_bus(selected_bus)
            departure.start_travel()
            selected_bus.status = BusStatusEnum.ON_THE_ROAD
            AutoStation().departure_list.append(departure)
            return AutoStation().show_menu(f"""
                {str(selected_bus)[0].capitalize() + str(selected_bus)[1:]} відправлено у {selected_bus.route}!
            """.strip()) # str.capitalize() - не підходить, оскільки останні символи строки переводить у нижній регістр
    
    
    def return_bus_to_park(self):
        """
        Метод для повернення автобуса до парку.

        Користувачеві буде запропоновано вибрати автобус зі списку.
        Після вибору, перевіряється поточний маршрут автобуса.
        Якщо автобус вже знаходиться у парку, виводиться відповідне повідомлення.
        В іншому випадку, автобус повертається до парку, його маршрут знімається.

        Повертає: None
        """
        if not AutoStation().analytic.active_departures:
            return AutoStation().show_menu("[!] Всі автобуси наразі у парку!")

        try:
            selected_bus = get_selected_object_from_input([departure.bus for departure in AutoStation().analytic.active_departures])
        except ReturnMenu:
            return AutoStation().show_menu()
        else:
            msg = f"Автобус вдало повернено до парку та знято з '{str(selected_bus.route)}'"
            bus_departure: Departure = get_bus_active_departure(selected_bus, AutoStation().analytic.active_departures) # гарантовано, що має бути лише один результат
            bus_departure.finish_travel()
            Park().add_bus(selected_bus)
            selected_bus.status = BusStatusEnum.IN_THE_PARKING
            return AutoStation().show_menu(msg)
    
    
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
            selected_bus: Bus = get_selected_object_from_input(AutoStation().bus_list)
            selected_route: Route = get_selected_object_from_input(AutoStation().route_list)
        except ReturnMenu:
            return AutoStation().show_menu()
        else:
            bus_active_departure: Departure = get_bus_active_departure(selected_bus, AutoStation().analytic.active_departures)

            if selected_bus.route:
                if selected_bus.route is selected_route:
                    return AutoStation().show_menu("[!] Обрано один й той самий маршрут для автобусу, ніяких змін не внесено.")
                
                msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}'"
                if bus_active_departure:
                    bus_active_departure.finish_travel()
                    Park().add_bus(selected_bus)
                    msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}', а рейс зупинено!\nАвтобус повернено у парк."

                selected_bus.route = selected_route
                return AutoStation().show_menu(msg)
            
            msg = f"Для автобусу встановлено {selected_route}"
            selected_bus.route = selected_route
            return AutoStation().show_menu(msg)


class Manager:
    def create_bus(self):
        """
        Метод для створення нового автобуса та додавання його до парку.
        Користувачу будуть запропоновані ввести номер автобуса та ім'я водія.
        Після цього автобус буде створено, додано до парку та до списку автобусів.

        Повертає:
        None
        """

        bus_number, driver_first_name, driver_second_name = (
            input("Введіть номер автобусу: "),
            input("Введіть ім'я водія: "),
            input("Введіть фамілію водія: ")
        )
        if bus_number in (bus.number for bus in AutoStation().bus_list):
            print("\n\n[!] Автобус з таким номером вже існує!")
            return self.create_bus()
        driver = Driver(first_name = driver_first_name, second_name = driver_second_name)
        bus = Bus(number = bus_number, driver = driver)
        Park().add_bus(bus)
        AutoStation().bus_list.append(bus)
        return AutoStation().show_menu(f"""
            {str(bus)[0].capitalize() + str(bus)[1:]} успішно створено та відправлено до парку!
        """.strip()) # str.capitalize() - не підходить, оскільки останні символи строки переводить у нижній регістр
    
    
    def delete_bus(self):
        """
        Метод для видалення автобуса.

        Користувачу будуть запропоновані вибрати автобус зі списку, який потрібно видалити.
        Вибраний автобус буде видалений зі списку автобусів та зі зв'язаного з ним маршруту (якщо такий існує).
        Активне відправлення з цим автобусом буде завершено.

        Повертає: None
        """
        try:
            selected_bus = get_selected_object_from_input(AutoStation().bus_list)
        except ReturnMenu:
            return AutoStation().show_menu()
        else:
            selected_bus_active_departure: Departure = get_bus_active_departure(
                selected_bus,
                AutoStation().analytic.active_departures
            )
            if selected_bus_active_departure:
                selected_bus_active_departure.finish_travel()
                AutoStation().bus_list.remove(selected_bus)
                return AutoStation().show_menu("Автобус було вдало знято з маршруту та видалено!")
            
            Park().remove_bus(selected_bus)
            AutoStation().bus_list.remove(selected_bus)
            return AutoStation().show_menu("Автобус було вдало видалено!")
    
    
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
        AutoStation().route_list.append(route)
        return AutoStation().show_menu("Маршрут вдало створено!")
    
    
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
            selected_route: Route = get_selected_object_from_input(AutoStation().route_list)
        except ReturnMenu:
            return AutoStation().show_menu()
        else:
            msg = "Маршрут вдало видалено!"
            for bus in get_route_buses(selected_route, AutoStation().bus_list):
                bus_departure: Departure = get_bus_active_departure(bus, AutoStation().analytic.active_departures)
                if bus_departure:
                    bus_departure.finish_travel()
                    Park().add_bus(bus)
                bus.route = None
            else:
                msg = "Маршрут вдало видалено, а всі його автобуси, що були у дорозі, відправлено до парку!"
            AutoStation().route_list.remove(selected_route)
            return AutoStation().show_menu(msg)


class Analytic:
    @property
    def active_departures(self) -> list[Departure]:
        """
        Повертає список дійсних відправлень.
        """
        return list(
            filter(lambda departure: departure.arrival_time is None, AutoStation().departure_list)
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
            filter(lambda bus: bus.route is not None, AutoStation().bus_list)
        ) 
    
    
    def analyze_buses(self) -> None:
        """

        Підраховує кількість рейсів для кожного автобуса та обчислює загальний час, 
        витрачений на кожен рейс. Виводить інформацію відповідно до заданого формату.

        :return: Повертає результат функції `show_menu()`.


        Алгоритм роботи функції:

        Список AutoStation().bus_list сортується за номером автобуса.

        Для кожного автобуса:
        - Виводиться заголовок рейсів для даного автобуса.
        - Ініціалізуються змінні total_count і total_time для підрахунку загальної кількості рейсів та часу.

        Для кожного відправлення в AutoStation().departure_list:
        * Якщо номер автобуса відправлення співпадає з номером поточного автобуса:
                - Збільшується лічильник total_count на 1.
                - Час подорожі перетворюється у формат datetime.
                - Час подорожі додається до загального часу total_time.
                - Виводиться інформація про маршрут та час подорожі.
        * Виводиться загальна кількість рейсів та загальний час для даного автобуса.
        * Повертається результат функції show_menu().
        """
        sorted_buses = sorted(AutoStation().bus_list, key = lambda bus: bus.number)

        for bus in sorted_buses:
            print(f"\n\nРейсы '{bus.number} з водієм {bus.driver.first_name}'")
            total_count = 0
            total_time = timedelta()

            for departure in AutoStation().departure_list:
                if departure.bus.number == bus.number:
                    total_count += 1
                    total_time += departure.travel_time
                    print(f'{departure.bus.route} | {timedelta_to_str(departure.travel_time)}')

            print(f"Ітого - {total_count} за {timedelta_to_str(total_time)}")

        return AutoStation().show_menu()


class AutoStation:
    """
    Клас AutoStation представляє автобусну станцію.

    __Атрибути__:
    - park: Park - парк автобусів
    - route_list: list[Route] - список маршрутів
    - bus_list: list[Bus] - список автобусів
    - departure_list: list[Departure] - список всіх відправлень автобусів
    """
    
    __instance = None
    

    def __new__(cls, *args, **kwargs) -> Self:
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.park = Park()
            cls.route_list: list[Route] = []
            cls.bus_list: list[Bus] = []
            cls.departure_list: list[Departure] = []
            cls.analytic: Analytic = Analytic()
            cls.manager: Manager = Manager()
            cls.dispatcher: Dispatcher = Dispatcher()
        return cls.__instance


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
        return self.manager.create_bus()


    @are_here_buses
    @are_here_buses_tied_to_route
    @are_here_routes
    @are_here_free_buses
    def depart_bus(self):
        return self.dispatcher.depart_bus()
        

    @are_here_buses
    def return_bus_to_park(self):
        return self.dispatcher.return_bus_to_park()
        

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
        return self.dispatcher.set_route_for_bus()


    @are_here_buses
    def delete_bus(self):
        return self.manager.delete_bus()
    

    def create_route(self):
        return self.manager.create_route()
    

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
            selected_route = get_selected_object_from_input(self.route_list)
        except ReturnMenu:
            return self.show_menu()
        else:
            buses_in_selected_route = get_route_buses(selected_route, self.bus_list)
            if not buses_in_selected_route:
                return self.show_menu(f"[!] Автобуси у '{selected_route}' відсутні!")
            msg = f"У '{selected_route}' такі автобуси: \n"
            buses = compose_objects_list_for_selection(buses_in_selected_route)
            return self.show_menu(msg + '\n'.join(buses))
    

    @are_here_routes
    def delete_route(self):
        return self.manager.delete_route()
    

    @are_here_buses
    @are_here_departures
    def show_analytics(self):
        return self.analytic.analyze_buses()
        

    @property
    def active_departures(self) -> list[Departure]:
        return self.analytic.active_departures
    

    @property
    def departed_buses(self) -> list[Bus]:
        return self.analytic.departed_buses
    

    @property
    def not_departed_buses(self) -> list[Bus]:
        return self.analytic.not_departed_buses
    

    @property
    def buses_tied_to_route(self) -> list[Bus]:
        return self.analytic.buses_tied_to_route
            

if __name__ == "__main__":
   AutoStation().show_menu()