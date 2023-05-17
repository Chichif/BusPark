def are_there_buses(func):
    def wrapper(self, *args, **kwargs):
        if not self.bus_list:
            return self.show_menu('Жодного автобусу не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper


def are_there_routes(func):
    def wrapper(self, *args, **kwargs):
        if not self.route_list:
            return self.show_menu('Жодного маршруту не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper

