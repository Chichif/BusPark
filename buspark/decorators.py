
def are_there_buses(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор, який перевіряє наявність автобусів перед викликом функції.

        Якщо жодного автобусу немає, виводить повідомлення про створення нового автобусу.
        """
        if not self.bus_list:
            return self.show_menu('Жодного автобусу не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper


def are_there_routes(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор, який перевіряє наявність маршрутів перед викликом функції.

        Якщо жодного маршруту немає, виводить повідомлення про створення нового маршруту.
        """
        if not self.route_list:
            return self.show_menu('Жодного маршруту не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper


def are_there_departed_buses(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор, який перевіряє наявність відправлених автобусів перед викликом функції.

        Якщо жодного активного відправлення немає, виводить повідомлення про відсутність автобусів у дорозі.
        """
        if not self.active_departures:
            return self.show_menu("[!] Автобуси у дорозі відсутні!")
        return func(self, *args, **kwargs)
    return wrapper


def are_there_departures(func):
    def wrapper(self, *args, **kwargs):
        """
        Декоратор, який перевіряє наявність відправлень перед викликом функції.

        Якщо жодного відправлення немає, виводить повідомлення про відсутність автобусів у дорозі.
        """
        if not self.departure_list:
            return self.show_menu("[!] Жодного відправлення не відбувалось!")
        return func(self, *args, **kwargs)
    return wrapper
