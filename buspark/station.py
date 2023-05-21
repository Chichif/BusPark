from typing import Self

from workers import (Manager,
                     Dispatcher,
                     Analytic)
from models import (Bus,
                    Park,
                    Route,
                    Departure)
from signals import (ReturnMenu, 
                     SameRouteSelected,
                     RouteChangedDuringDeparture,
                     RouteSet)
from station_decorators import (are_here_buses,
                                are_here_buses_tied_to_route,
                                are_here_departures, 
                                are_here_routes,
                                are_here_departed_buses,
                                are_here_free_buses)
from serializers import timedelta_to_str
from utils import (get_object_from_suggested_options,
                   get_route_buses,
                   compose_objects_list_for_selection)


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
        """Створює автобус та додає його до парку.

        Кроки:
        1. Створення нового автобуса за допомогою методу create_bus класу manager (делегування).
        2. Додавання створеного автобуса до парку за допомогою методу add_bus класу park.
        3. Додавання автобуса до списку bus_list.
        4. Форматування заголовку автобуса для відображення.
        5. Повернення результату виклику show_menu з відформатованим повідомленням про успішне створення та відправлення автобуса до парку.

        Returns:
            Результат виклику show_menu з відформатованим повідомленням про успішне створення та відправлення автобуса до парку.
        """
        bus = self.manager.create_bus(self.bus_list)
        self.park.add_bus(bus)
        self.bus_list.append(bus)
        bus_title_formatted = str(bus)[0].capitalize() + str(bus)[1:]
        return self.show_menu(f"{bus_title_formatted} успішно створено та відправлено до парку!".strip()) 
    

    @are_here_buses
    @are_here_buses_tied_to_route
    @are_here_routes
    @are_here_free_buses
    def depart_bus(self):
        """Відправляє автобус у рейс.

        Кроки:
        1. Отримання списку невідправлених автобусів за допомогою методу get_not_departed_buses класу analytic (делегування).
        2. Отримання списку автобусів, прив'язаних до маршрутів, за допомогою методу get_buses_tied_to_route класу analytic.
        3. Виклик методу depart_bus класу dispatcher для вибору автобуса та рейсу, на який його відправити.
        4. Додавання рейсу до списку departure_list.
        5. Форматування заголовку вибраного автобуса для відображення.
        6. Повернення результату виклику show_menu з відформатованим повідомленням про успішне відправлення автобуса на маршрут.

        Returns:
            Результат виклику show_menu з відформатованим повідомленням про успішне відправлення автобуса на маршрут."""
        try:
            selected_bus, departure = self.dispatcher.depart_bus(
                self.analytic.get_not_departed_buses(
                                self.departure_list,
                                self.analytic.get_buses_tied_to_route(self.bus_list)
                            )
            )
        except ReturnMenu:
            return self.show_menu()
        
        self.departure_list.append(departure)
        bus_title_formatted = str(selected_bus)[0].capitalize() + str(selected_bus)[1:]
        return self.show_menu(f"{bus_title_formatted} відправлено у {selected_bus.route}!".strip())
        

    @are_here_buses
    @are_here_departed_buses
    def return_bus_to_park(self):
        """Повертає автобус до парку.

        Кроки:
        1. Делегування отримання списку активних рейсів до методу get_active_departures класу analytic.
        2. Виклик методу return_bus_to_park класу dispatcher для вибору автобуса, який повернеться до парку.
        3. Створення повідомлення про успішне повернення автобуса до парку та зняття його з маршруту.
        4. Повернення результату виклику show_menu з відформатованим повідомленням.

        Returns:
            Результат виклику show_menu з відформатованим повідомленням про успішне повернення автобуса до парку.
        """ 
        try:
            selected_bus = self.dispatcher.return_bus_to_park(
                self.analytic.get_active_departures(self.departure_list)
            )
        except ReturnMenu:
            return self.show_menu()
        
        msg = f"Автобус вдало повернено до парку та знято з '{selected_bus.route}'"
        return self.show_menu(msg)
        

    @are_here_buses
    @are_here_routes
    @are_here_departed_buses
    def show_departed_buses(self):
        """Відображує список активних рейсів.

        Кроки:
        1. Делегування отримання списку активних рейсів до методу get_active_departures класу analytic.
        2. Створення списку опцій для відображення активних рейсів.
        3. Повернення результату виклику show_menu зі згенерованим списком опцій.

        Returns:
            Результат виклику show_menu зі списком активних рейсів.
        """
        options = []
        for index, departure in enumerate(
            self.analytic.get_active_departures(self.departure_list)
        ):
            options.append(f"[{index} - {departure.bus} | {departure.bus.route} | у дорозі {timedelta_to_str(departure.travel_time)}]")
        return self.show_menu("\n".join(options))
    

    @are_here_buses
    def show_buses_in_park(self):
        """Відображує список автобусів у парку.

        Кроки:
        1. Перевірка, чи є автобуси в парку автобусів.
        2. В разі відсутності автобусів, виводиться повідомлення про порожній парк.
        3. У випадку наявності автобусів, виводиться список автобусів у парку.
        4. Повернення результату виклику show_menu.

        Returns:
            None: Повернення результату виклику show_menu.
        """
        if not self.park.parked_buses:
            return self.show_menu("[!] Парк пустий!")
        
        for index, bus in enumerate(self.park.parked_buses, 1):
            print(f"[{index}] - {bus}")
        return self.show_menu()


    @are_here_buses
    @are_here_routes
    def set_route_for_bus(self):
        """Встановлює маршрут для автобуса.

        Кроки:
        1. Делегування отримання списку активних рейсів до методу get_active_departures класу analytic.
        2. Перехід до відповідного пункту меню в залежності від результату виклику set_route_for_bus.
        3. Повернення результату виклику show_menu з повідомленням.

        Returns:
            Результат виклику show_menu з повідомленням про встановлення маршруту для автобуса.
        """
        try:
            self.dispatcher.set_route_for_bus(self.bus_list, 
                                                    self.route_list, 
                                                    self.analytic.get_active_departures(self.departure_list))
        except ReturnMenu:
            return self.show_menu()
        except SameRouteSelected as ex:
            return self.show_menu(str(ex))
        except RouteChangedDuringDeparture as ex:
            return self.show_menu(str(ex))
        except RouteSet as ex:
            return self.show_menu(str(ex))


    @are_here_buses
    def delete_bus(self):
        """Видаляє автобус.

        Кроки:
        1. Делегування отримання списку активних рейсів до методу get_active_departures класу analytic.
        2. Перехід до відповідного пункту меню в залежності від результату виклику delete_bus.
        3. Повернення результату виклику show_menu з повідомленням.

        Returns:
            Результат виклику show_menu з повідомленням про видалення автобуса.
        """
        try:
            self.manager.delete_bus(self.bus_list, 
                                    self.analytic.get_active_departures(self.departure_list))
        except ReturnMenu:
            return self.show_menu()
        return self.show_menu("Автобус було вдало видалено!")
    

    def create_route(self):
        """Створює новий маршрут.

        Кроки:
        1. Делегування створення маршруту до методу create_route класу manager.
        2. Додавання створеного маршруту до списку маршрутів.
        3. Повернення результату виклику show_menu з повідомленням про створення маршруту.

        Returns:
            Результат виклику show_menu з повідомленням про створення маршруту.
        """
        route = self.manager.create_route()
        self.route_list.append(route)
        return self.show_menu("Маршрут вдало створено!")
    

    @are_here_buses
    @are_here_routes
    def show_route_buses(self):
        """Відображає список автобусів на обраному маршруті.

        Кроки:
        1. Вибір маршруту зі списку за допомогою методу get_object_from_suggested_options.
        2. Перехід до відповідного пункту меню в залежності від результату вибору маршруту.
        3. Отримання списку автобусів на обраному маршруті за допомогою методу get_route_buses.
        4. Перевірка, чи є автобуси на обраному маршруті.
        5. Побудова повідомлення зі списком автобусів на обраному маршруті.
        6. Повернення результату виклику show_menu з повідомленням.

        Returns:
            Результат виклику show_menu з повідомленням про список автобусів на обраному маршруті.
        """
        try:
            selected_route = get_object_from_suggested_options(self.route_list)
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
        """Видаляє обраний маршрут.

        Кроки:
        1. Делегування виклику методу delete_route класу manager для видалення маршруту.
        2. Делегування виклику методу get_active_departures класу analytic для отримання
        активних рейсів, пов'язаних з видаляємим маршрутом.
        3. Обробка виключення ReturnMenu і повернення до головного меню.
        4. Повернення результату виклику show_menu з повідомленням про успішне видалення маршруту.

        Returns:
            Результат виклику show_menu з повідомленням про успішне видалення маршруту.
        """
        try:
            self.manager.delete_route(self.route_list, 
                                      self.bus_list, 
                                      self.analytic.get_active_departures(self.departure_list))
        except ReturnMenu:
            return self.show_menu()
        return self.show_menu("Маршрут вдало видалено!")


    @are_here_buses
    @are_here_departures
    def show_analytics(self):
        """Відображає аналітику рейсів.

        Кроки:
        1. Делегування аналізу рейсів до методу analyze_buses класу analytic.
        2. Виведення результатів аналізу на екран.
        3. Повернення результату виклику show_menu без повідомлення.

        Returns:
            Результат виклику show_menu без повідомлення.
        """
        results = self.analytic.analyze_buses(self.bus_list, self.departure_list)
        for bus_results in results:
            print(f"\n\nРейсы '{bus_results.bus.number} з водієм {bus_results.bus.driver.first_name}'")
            for departure in bus_results.departures:
                print(f'{departure.route} | {timedelta_to_str(departure.travel_time)}')
            print(f"Ітого - {bus_results.total_count} за {timedelta_to_str(bus_results.total_time)}")
        return self.show_menu()
            

if __name__ == "__main__":
   AutoStation().show_menu()