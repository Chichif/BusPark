from .bus import Bus
from .park import BusPark
from .route import Route
from .exceptions import ReturnMenu
from .decorators import (are_there_buses, 
                         are_there_routes)


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
                'callback': self.return_bus_to_park
            },
            {
                'title': 'Видалити автобус',
                'callback': self.delete_bus
            },
            {
                'title': 'Створити маршрут',
                'callback': self.create_route
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
            return self.show_menu('\n\n [!] Необхідно ввести саме цифру/число.')
        else:
            if choosed_option in range(len(options)):
                options[choosed_option]['callback']()
            return self.show_menu('\n\n [!] Обрана неіснуюча опція :(')


    def create_bus(self):
        bus_number, driver_name = (
            input('Введіть назву автобусу: '),
            input('Введіть ім\'я водія: ')
        )
        bus = Bus(bus_number, driver_name)
        self.park.add_bus(bus)
        self.buses.append(bus)
        return self.show_menu('\n\nАвтобус успішно створено та відправлено до парку!')


    @are_there_buses
    def delete_bus(self):
        try:
            selected_bus = self._get_selected_object_from_input(self.buses)
        except ReturnMenu:
            return self.show_menu('\n\n')
        else:
            if selected_bus.route:
                selected_bus.route.remove_bus(selected_bus)
            else:
                self.park.remove_bus(selected_bus)

            self.buses.remove(selected_bus)
            return self.show_menu('\n\nАвтобус було вдало видалено!')
    

    def create_route(self):
        start_point, end_point = (
            input("Початкова точка: "),
            input("Кінцева точка: ")
        )
        route = Route(start_point, end_point)
        self.routes.append(route)
        return self.show_menu("\n\nМаршрут вдало створено!")


    @are_there_buses
    @are_there_routes
    def set_route_for_bus(self):
        try:
            selected_bus = self._get_selected_object_from_input(self.buses)
            selected_route = self._get_selected_object_from_input(self.routes)
        except ReturnMenu:
            return self.show_menu('\n\n')
        else:
            if selected_bus.route:
                if selected_bus.route is selected_route:
                    return self.show_menu("\n\n[!] Обрано один й той самий маршрут для автобусу, ніяких змін не внесено.")
                
                msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}'"
                selected_route.add_bus(selected_bus)
                return self.show_menu(msg)
            
            selected_route.add_bus(selected_bus)
            return self.show_menu(f"\n\nДля автобусу встановлено {selected_route}")
        
    @are_there_buses
    def return_bus_to_park(self):
        try:
            selected_bus = self._get_selected_object_from_input(self.buses)
        except ReturnMenu:
            return self.show_menu('\n\n')
        else:
            if not selected_bus.route:
                return self.show_menu("\n\n[!] Автобус наразі знаходиться у парку.")
            msg = f"Автобус вдало повернено до парку та знято з '{str(selected_bus.route)}'"
            self.park.add_bus(selected_bus)
            return self.show_menu(msg)
                

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
                print("\n\n [!] Обрана неіснуюча опція :(")
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