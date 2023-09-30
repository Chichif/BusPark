def are_here_buses(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор класу AutoStation, який перевіряє наявність автобусів перед викликом функції.

        Якщо жодного автобусу немає, виводить повідомлення про створення нового автобусу.
        """
        if not self.bus_list:
            return self.show_menu('Жодного автобусу не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper


def are_here_buses_tied_to_route(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор класу AutoStation, який перевіряє наявність автобусів зв'язаних з маршрутом
        перед викликом функції.

        Якщо жодного автобусу немає, виводить повідомлення про створення нового автобусу.
        """
        if not self.analytic.get_buses_tied_to_route(self.bus_list):
            return self.show_menu("[!] Жодного автобусу з прив'язаним маршрутом не існує!")
        return func(self, *args, **kwargs)
    return wrapper


def are_here_free_buses(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор класу AutoStation, який перевіряє наявність автобусів не у дорозі
        перед викликом функції.

        Якщо жодного автобусу немає, виводить повідомлення про створення нового автобусу.
        """
        if not self.analytic.get_not_departed_buses(self.departure_list, 
                                                    self.analytic.get_buses_tied_to_route(self.bus_list)):
            return self.show_menu("[!] Усі автобуси у дорозі, вільних немає!")
        return func(self, *args, **kwargs)
    return wrapper


def are_here_routes(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор класу AutoStation, який перевіряє наявність маршрутів перед викликом функції.

        Якщо жодного маршруту немає, виводить повідомлення про створення нового маршруту.
        """
        if not self.route_list:
            return self.show_menu('Жодного маршруту не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper


def are_here_departed_buses(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор класу AutoStation, який перевіряє наявність відправлених автобусів перед викликом функції.

        Якщо жодного активного відправлення немає, виводить повідомлення про відсутність автобусів у дорозі.
        """
        if not self.analytic.get_active_departures(self.departure_list):
            return self.show_menu("[!] Автобуси у дорозі відсутні!")
        return func(self, *args, **kwargs)
    return wrapper


def are_here_departures(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор класу AutoStation, який перевіряє наявність відправлень перед викликом функції.

        Якщо жодного відправлення немає, виводить повідомлення про відсутність автобусів у дорозі.
        """
        if not self.departure_list:
            return self.show_menu("[!] Жодного відправлення не відбувалось!")
        return func(self, *args, **kwargs)
    return wrapper
