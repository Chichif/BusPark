def are_there_buses(func):
    def wrapper(self, *args, **kwargs):
        if not self.buses:
            return self.show_menu('Жодного автобусу не існує, пропонуємо створити хоч якийсь!')
        return func(self, *args, **kwargs)
    return wrapper

