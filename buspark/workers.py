from datetime import timedelta

from models import (City,
                    Driver,
                    Bus,
                    Park,
                    Route,
                    Departure,
                    BusStatusEnum,
                    BusDepartureResults)
from utils import (get_object_from_suggested_options,
                   get_bus_active_departure,
                   get_route_buses)
from signals import (ReturnMenu,
                     SameRouteSelected,
                     RouteChangedDuringDeparture,
                     RouteSet)


class Dispatcher:
    def depart_bus(self, not_departed_buses: list[Bus]) -> tuple[Bus, Departure]:
        """Відправляє обраний автобус у рейс.

        Параметри:
            not_departed_buses (list[Bus]): Список невідправлених автобусів.

        Кроки:
        1. Отримання обраний автобус зі списку невідправлених автобусів за допомогою функції get_object_from_suggested_options.
        2. Створення рейсу за допомогою створення об'єкту Departure з обраним автобусом та його маршрутом.
        3. Видалення автобуса з парку за допомогою виклику методу remove_bus класу Park.
        4. Запуск рейсу за допомогою виклику методу start_travel об'єкту Departure.
        5. Зміна статусу обраного автобуса на "У русі" (BusStatusEnum.ON_THE_ROAD).
        6. Повернення обраного автобуса та рейсу як результат функції.

        Returns:
            Tuple[Bus, Departure]: Кортеж з обраним автобусом та рейсом.
        
        Raises:
            ReturnMenu: Виключення, яке сигналізує про повернення до головного меню.
        """
        try:
            selected_bus = get_object_from_suggested_options(not_departed_buses)
        except ReturnMenu:
            raise ReturnMenu()
        else:
            departure = Departure(bus = selected_bus, route = selected_bus.route)
            Park().remove_bus(selected_bus)
            departure.start_travel()
            selected_bus.status = BusStatusEnum.ON_THE_ROAD
            return selected_bus, departure
    
    
    def return_bus_to_park(self, active_departures: list[Departure]) -> Bus:
        """Повертає обраний автобус у парк.

        Параметри:
            active_departures (list[Departure]): Список активних рейсів.

        Кроки:
        1. Отримання обраного автобуса зі списку автобусів, що знаходяться у активних рейсах, за допомогою функції get_object_from_suggested_options.
        2. Отримання активного рейсу обраного автобуса за допомогою функції get_bus_active_departure.
        3. Завершення активного рейсу за допомогою виклику методу finish_travel об'єкту активного рейсу.
        4. Додавання автобуса у парк за допомогою виклику методу add_bus класу Park.
        5. Зміна статусу обраного автобуса на "У парку" (BusStatusEnum.IN_THE_PARKING).
        6. Повернення обраного автобуса.

        Returns:
            Bus: Обраний автобус для повернення у парк.

        Raises:
            ReturnMenu: Виключення, яке сигналізує про повернення до головного меню.
        """
        try:
            selected_bus = get_object_from_suggested_options([departure.bus for departure in active_departures])
        except ReturnMenu:
            raise ReturnMenu()
        else:
            bus_departure: Departure = get_bus_active_departure(selected_bus, active_departures) # гарантовано, що має бути лише один результат
            bus_departure.finish_travel()
            Park().add_bus(selected_bus)
            selected_bus.status = BusStatusEnum.IN_THE_PARKING
            return selected_bus
    
    
    def set_route_for_bus(self, bus_list: list[Bus], 
                                route_list: list[Route],
                                active_departures: list[Departure]):
        """Встановлює маршрут для обраного автобуса.

        Параметри:
            bus_list (list[Bus]): Список автобусів.
            route_list (list[Route]): Список маршрутів.
            active_departures (list[Departure]): Список активних рейсів.

        Кроки:
        1. Отримання обраного автобуса зі списку автобусів за допомогою функції get_object_from_suggested_options.
        2. Отримання обраного маршруту зі списку маршрутів за допомогою функції get_object_from_suggested_options.
        3. Перевірка, чи обраний автобус вже прив'язаний до обраного маршруту.
            - Якщо так, повертається повідомлення про те, що зміни не внесено.
        4. Виклик функції change_route з обраним автобусом, обраним маршрутом та списком активних рейсів.
        5. Повернення повідомлення з результатом зміни маршруту.

        Returns:
            str: Сигнал з результатом зміни маршруту.

        Raises:
        1. ReturnMenu: Виключення, яке сигналізує про повернення до головного меню.
        2. RouteSet: Сигнал з результатом встановлення маршруту.
        3. RouteChangedDuringDeparture: Сигнал з результатом зміни маршруту під час відправлення.
        4. SameRouteSelected: Сигнал з повідомленням, що обраний маршрут наразі актуальний. 
        """
        try:
            selected_bus: Bus = get_object_from_suggested_options(bus_list)
            selected_route: Route = get_object_from_suggested_options(route_list)
        except ReturnMenu:
            raise ReturnMenu()
        
        if selected_bus.route == selected_route:
            raise SameRouteSelected("[!] Обрано один й той самий маршрут для автобусу, ніяких змін не внесено.")

        try:
            self.change_route(selected_bus, selected_route, active_departures)
        except RouteChangedDuringDeparture as ex:
            raise RouteChangedDuringDeparture(str(ex))
        except RouteSet as ex:
            raise RouteSet(str(ex))


    def change_route(self, bus: Bus, route: Route, active_departures: list[Departure]):
        """Змінює маршрут для обраного автобуса.

        Параметри:
            bus (Bus): Обраний автобус.
            route (Route): Обраний маршрут.
            active_departures (list[Departure]): Список активних рейсів.

        Кроки:
        1. Отримання активного рейсу для обраного автобуса за допомогою функції get_bus_active_departure.
        2. Якщо активний рейс існує:
            - Завершення активного рейсу за допомогою виклику методу finish_travel об'єкту активного рейсу.
            - Додавання автобуса у парк за допомогою виклику методу add_bus класу Park.
            - Оновлення повідомлення про зміну маршруту.
        3. Зміна маршруту для обраного автобуса.
        4. Повернення повідомлення з результатом зміни маршруту.

        Raises:
        1. RouteSet: Сигнал з результатом встановлення маршруту.
        2. RouteChangedDuringDeparture: Сигнал з результатом зміни маршруту під час відправлення.
        """
        bus_active_departure = get_bus_active_departure(bus, active_departures)

        if bus_active_departure:
            bus_active_departure.finish_travel()
            Park().add_bus(bus)
            raise RouteChangedDuringDeparture(f"Маршрут автобусу було змінено з '{bus.route}' на '{route}', а рейс зупинено!\nАвтобус повернено у парк.")   
        bus.route = route
        raise RouteSet(f"Встановлено '{route}'!")


class Manager:
    def create_bus(self, bus_list: list[Bus]):
        """Створює новий автобус.

        Параметри:
            bus_list (list[Bus]): Список існуючих автобусів.

        Кроки:
        1. Отримання від користувача номеру автобусу, імені та прізвища водія за допомогою функції input.
        2. Перевірка, чи автобус з введеним номером вже існує у списку існуючих автобусів.
            - Якщо так, виведення повідомлення про те, що автобус з таким номером вже існує і повторення процесу створення автобуса.
        3. Створення об'єкту водія за допомогою введених імені та прізвища.
        4. Створення об'єкту автобуса з отриманим номером та створеним об'єктом водія.
        5. Повернення створеного автобуса.

        Returns:
            Bus: Створений автобус.
        """
        bus_number, driver_first_name, driver_second_name = (
            input("Введіть номер автобусу: "),
            input("Введіть ім'я водія: "),
            input("Введіть фамілію водія: ")
        )
        if bus_number in (bus.number for bus in bus_list):
            print("\n\n[!] Автобус з таким номером вже існує!")
            return self.create_bus()
        driver = Driver(first_name = driver_first_name, second_name = driver_second_name)
        bus = Bus(number = bus_number, driver = driver)
        return bus
    
    
    def delete_bus(self, bus_list: list[Bus], active_departures: list[Departure]):
        """Видаляє обраний автобус.

        Параметри:
            bus_list (list[Bus]): Список автобусів.
            active_departures (list[Departure]): Список активних рейсів.

        Кроки:
        1. Отримання обраного автобуса зі списку автобусів за допомогою функції get_object_from_suggested_options.
        2. Отримання активного рейсу для обраного автобуса за допомогою функції get_bus_active_departure.
        3. Якщо активний рейс існує:
            - Завершення активного рейсу за допомогою виклику методу finish_travel об'єкту активного рейсу.
            - Видалення обраного автобуса зі списку автобусів.
        4. Інакше:
            - Видалення обраного автобуса зі списку автобусів у парку за допомогою виклику методу remove_bus класу Park.

        Raises:
            ReturnMenu: Виключення, яке сигналізує про повернення до головного меню.
        """
        try:
            selected_bus = get_object_from_suggested_options(bus_list)
        except ReturnMenu:
            raise ReturnMenu()
        else:
            selected_bus_active_departure: Departure = get_bus_active_departure(selected_bus,
                                                                                active_departures)
            if selected_bus_active_departure:
                selected_bus_active_departure.finish_travel()
                bus_list.remove(selected_bus)
                return
            Park().remove_bus(selected_bus)
    
    
    def create_route(self) -> Route:
        """Створює новий маршрут.

        Кроки:
        1. Отримання початкової та кінцевої точок маршруту від користувача за допомогою функції input.
        2. Створення об'єкту міста для початкової точки за допомогою отриманих даних.
        3. Створення об'єкту міста для кінцевої точки за допомогою отриманих даних.
        4. Створення об'єкту маршруту з отриманими об'єктами міст.

        Returns:
            Route: Створений маршрут.
        """
        start_point, end_point = (
            City(title = input("Початкова точка: ")),
            City(title = input("Кінцева точка: "))
        )
        return Route(start_point = start_point, end_point = end_point)

    
    def delete_route(self, 
                     route_list: list[Route], 
                     bus_list: list[Bus],
                     active_departures: list[Departure]):
        """Видаляє обраний маршрут.

        Параметри:
            route_list (list[Route]): Список маршрутів.
            bus_list (list[Bus]): Список автобусів.
            active_departures (list[Departure]): Список активних рейсів.

        Кроки:
        1. Отримання обраного маршруту зі списку маршрутів за допомогою функції get_object_from_suggested_options.
        2. Перебір автобусів, які обслуговують обраний маршрут.
            - Отримання активного рейсу для кожного автобуса за допомогою функції get_bus_active_departure.
            - Якщо активний рейс існує:
                - Завершення активного рейсу за допомогою виклику методу finish_travel об'єкту активного рейсу.
                - Додавання автобуса у парк за допомогою виклику методу add_bus класу Park.
            - Скидання маршруту для кожного автобуса шляхом присвоєння значення None атрибуту route.
        3. Видалення обраного маршруту зі списку маршрутів.

        Raises:
            ReturnMenu: Виключення, яке сигналізує про повернення до головного меню.
        """
        try:
            selected_route: Route = get_object_from_suggested_options(route_list)
        except ReturnMenu:
            raise ReturnMenu()
        else:
            for bus in get_route_buses(selected_route, bus_list):
                bus_departure: Departure = get_bus_active_departure(bus, active_departures)
                if bus_departure:
                    bus_departure.finish_travel()
                    Park().add_bus(bus)
                bus.route = None
            route_list.remove(selected_route)


class Analytic:
    def get_active_departures(self, departure_list: list[Departure]) -> list[Departure]:
        """Повертає список активних рейсів.

        Параметри:
            departure_list (list[Departure]): Список рейсів.

        Returns:
            list[Departure]: Список активних рейсів (рейсів, у яких час прибуття не вказаний).
        """
        return list(
            filter(lambda departure: departure.arrival_time is None, departure_list)
        )


    def get_departed_buses(self, departure_list: list[Departure]) -> list[Bus]:
        """Повертає список автобусів, що вирушили у рейс.

        Параметри:
            departure_list (list[Departure]): Список рейсів.

        Returns:
            list[Bus]: Список автобусів, що вирушили у рейс.
        """
        return [departure.bus for departure in self.get_active_departures(departure_list)]
    
    
    def get_not_departed_buses(self, 
                               departure_list: list[Bus], 
                               buses_tied_to_route: list[Bus]) -> list[Bus]:
        """Повертає список автобусів, які ще не вирушили у рейс.

        Параметри:
            departure_list (list[Bus]): Список автобусів, що знаходяться у рейсі.
            buses_tied_to_route (list[Bus]): Список автобусів, пов'язаних з маршрутом.

        Returns:
            list[Bus]: Список автобусів, які ще не вирушили у рейс.
        """
        return list(
            filter(lambda bus: bus not in self.get_departed_buses(departure_list), buses_tied_to_route)
        )
    
    
    def get_buses_tied_to_route(self, bus_list: list[Bus]) -> list[Bus]:
        """Повертає список автобусів, які пов'язані з маршрутом.

        Параметри:
            bus_list (list[Bus]): Список автобусів.

        Returns:
            list[Bus]: Список автобусів, які пов'язані з маршрутом.
        """
        return list(
            filter(lambda bus: bus.route is not None, bus_list)
        ) 
    
    
    def analyze_buses(self, bus_list: list[Bus], departure_list: list[Departure]) -> list[BusDepartureResults]:
        """Аналізує автобуси і повертає результати аналізу.

        Параметри:
            bus_list (list[Bus]): Список автобусів.
            departure_list (list[Departure]): Список рейсів.

        Returns:
            list[BusDepartureResults]: Список результатів аналізу автобусів.
        """
        sorted_buses = sorted(bus_list, key = lambda bus: bus.number)
        results = []
        for bus in sorted_buses:
            total_count = 0
            total_time = timedelta()
            bus_results_kwargs = {"bus": bus, "departures": []}

            for departure in filter(lambda departure: departure.bus == bus, departure_list):
                total_count += 1
                total_time += departure.travel_time
                bus_results_kwargs["departures"].append(
                    departure
                )
            bus_results_kwargs.update({
                "total_count": total_count,
                "total_time": total_time
            })
            results.append(BusDepartureResults(**bus_results_kwargs))
        return results