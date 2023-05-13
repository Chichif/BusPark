from .bus import Bus
from .park import BusPark
from .route import Route
from .exceptions import ReturnMenu, SelectedNonExistentBus
from .decorators import are_there_buses


class BusStation:
    def __init__(self) -> None:
        self.park = BusPark()
        self.routes: list[Route] = []
        self.buses: list[Bus] = []

    def show_menu(self, menu_msg: str = None):

        if menu_msg: print(menu_msg)
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
                'callback': self.set_route_for_bus
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

        text = ''
        for option_index, option in enumerate(options):
            text += f"[{option_index}] - {option.get('title')}\n"
        
        try:
            choosed_option: int = int(input(text))
        except ValueError as ex:
            return self.show_menu('[!] Необхідно ввести саме цифру/число.')
        else:
            if choosed_option in range(len(options)):
                options[choosed_option]['callback']()
            return self.show_menu('[!] Обрана неіснуюча опція :(')


    def create_bus(self):
        bus_number, driver_name = (
            input('Введіть назву автобусу: '),
            input('Введіть ім\'я водія: ')
        )
        bus = Bus(bus_number, driver_name)
        self.park.add_bus(bus)
        self.buses.append(bus)
        return self.show_menu('Автобус успішно створено та відправлено до парку!')

    @are_there_buses
    def delete_bus(self):
        try:
            selected_bus = self._get_selected_bus_from_input()
        except SelectedNonExistentBus:
            return self.show_menu("Обрано неіснуючий автобус!")
        except ReturnMenu:
            return self.show_menu('\n\n')
        else:
            match selected_bus.status:
                case 'У парку':
                    self.park.remove_bus(selected_bus)
                case 'На маршруті':
                    selected_bus.route.remove_bus(selected_bus)

            self.buses.remove(selected_bus)
            return self.show_menu('Автобус було вдало видалено!')
    
    @are_there_buses
    def set_route_for_bus(self):
        pass

    
    def _get_selected_bus_from_input(self) -> Bus:
        options = []
        for option_index, bus in enumerate(self.buses):
            options.append(
                f'[{option_index}] - автобус под номером {str(bus)}'
            )
        options.append(f'[{len(options)}] - повернутись до меню: ')

        try:
            selected_option = int(input('\n'.join(options)))
        except ValueError:
            print('Введено не цифру/число!')
            return self._get_selected_bus_from_input()
        else:
            options_range = range(len(options))
            if selected_option in options_range:
                if selected_option == options_range[-1]:
                    raise ReturnMenu()
                selected_bus = self.buses[selected_option]
                return selected_bus
            else:
                raise SelectedNonExistentBus()
            
    
    def _get_selected_route_from_input(self): pass

            

if __name__ == '__main__':
   BusStation().show_menu()