from .bus import Bus
from .park import BusPark
from .route import Route
from .exceptions import ReturnMenu
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
                'title': 'Повернути автобус у парк',
                'callback': self.create_bus
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
            selected_bus = self._get_selected_object_from_input(self.buses)
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
        try:
            selected_route = self._get_selected_object_from_input(self.routes)
            selected_bus = self._get_selected_object_from_input(self.buses)
        except ReturnMenu:
            return self.show_menu('\n\n')
        else:
            pass


    def _get_selected_object_from_input(self, objects: list[Bus | Route]) -> Bus | Route:
        options = self._compose_objects_list_for_selecting(objects)
        options.append(f'[{len(options)}] - повернутись до меню: ')

        try:
            selected_option = int(input('\n'.join(options)))
        except ValueError:
            print('Введено не цифру/число!')
            return self._get_selected_object_from_input()
        else:
            if self._is_answer_existent(options, selected_option):
                if selected_option == range(len(options))[-1]:
                    raise ReturnMenu()
                selected_object = objects[selected_option]
                return selected_object
            else:
                print("Обрано неіснуючий варіант відповіді!")
                return self._get_selected_object_from_input()
    

    def _compose_objects_list_for_selecting(self, objects: list[Bus | Route]):
        options = []
        for option_index, object in enumerate(objects):
            options.append(
                f'[{option_index}] - {str(object)}'
            )
        return options
            
    
    def _is_answer_existent(self, options: list[str], selected_option: int):
        options_range = range(len(options))
        if selected_option in options_range:
            return True
        else:
            return False
            

if __name__ == '__main__':
   BusStation().show_menu()