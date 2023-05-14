'''
Наданий код, здається, є реалізацією системи управління автовокзалом на мові Python. Клас BusStation представляє автовокзал та надає методи для управління автобусами, маршрутами та взаємодією між ними.

Основні компоненти такі:

Атрибути класу:

park: Екземпляр класу BusPark, що представляє автостоянку.
routes: Список об'єктів класу Route, що представляють доступні маршрути.
buses: Список об'єктів класу Bus, що представляють автобуси на вокзалі.
Методи:

__init()__: Ініціалізує об'єкт класу BusStation з порожньою автостоянкою, маршрутами та автобусами.
show_menu(): Відображає меню з варіантами і обробляє вибрані дії.
create_bus(): Створює новий автобус і додає його на автостоянку та до списку автобусів.
delete_bus(): Видаляє автобус із списку автобусів та видаляє його з пов'язаного маршруту, якщо це застосовно.
create_route(): Створює новий маршрут і додає його до списку маршрутів.
delete_route(): Видаляє маршрут із списку маршрутів та повертає пов'язані автобуси на автостоянку.
show_route_buses(): Відображає автобуси, пов'язані з обраним маршрутом.
show_buses_in_routes(): Відображає автобуси, які знаходяться на маршрутах.
show_buses_in_park(): Відображає автобуси, які знаходяться на автостоянці.
set_route_for_bus(): Призначає маршрут для обраного автобуса та оновлює його поточний маршрут.
return_bus_to_park(): Повертає автобус на автостоянку та видаляє його поточний маршрут.
Код використовує кілька користувацьких декораторів (are_there_buses та are_there_routes), щоб перевірити на наявність автобусів або маршрутів перед виконанням певних методів.

Загалом, цей код надає основну структуру для управління автобусами та маршрутами на автовокзалі.
'''


from .bus import Bus
from .park import BusPark
from .route import Route
from .exceptions import ReturnMenu
from .decorators import (are_there_buses, 
                         are_there_routes)


class BusStation:
    """
    Клас BusStation представляє автобусну станцію.

    Атрибути:
    - park: BusPark - парк автобусів
    - routes: List[Route] - список маршрутів
    - buses: List[Bus] - список автобусів


    """
    def __init__(self) -> None:
        self.park = BusPark()
        self.routes: list[Route] = []
        self.buses: list[Bus] = []

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
                'callback': self.show_buses_in_routes
            },
            {
                'title': 'Вивести список автобусів певного маршруту',
                'callback': self.show_route_buses
            },
            {
                'title': 'Вивести список автобусів у парку',
                'callback': self.create_bus
            }
        )

        text = '\n\n'
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
        """
        Метод для створення нового автобуса та додавання його до парку.
        Користувачу будуть запропоновані ввести номер автобуса та ім'я водія.
        Після цього автобус буде створено, додано до парку та до списку автобусів.

        Повертає:
        None
        """

        bus_number, driver_name = (
            input('Введіть назву автобусу: '),
            input('Введіть ім\'я водія: ')
        )
        bus = Bus(bus_number, driver_name)
        self.park.add_bus(bus, create = True)
        self.buses.append(bus)
        return self.show_menu('Автобус успішно створено та відправлено до парку!')


    @are_there_buses
    def delete_bus(self):
        """
        Метод для видалення автобуса.

        Користувачу будуть запропоновані вибрати автобус зі списку, який потрібно видалити.
        Вибраний автобус буде видалений зі списку автобусів та зі зв'язаного з ним маршруту (якщо такий існує).

        Повертає:
        None
        """
        try:
            selected_bus = self._get_selected_object_from_input(self.buses)
        except ReturnMenu:
            return self.show_menu('')
        else:
            if selected_bus.route:
                selected_bus.route.remove_bus(selected_bus)
            else:
                self.park.remove_bus(selected_bus)

            self.buses.remove(selected_bus)
            return self.show_menu('Автобус було вдало видалено!')
    

    def create_route(self):
        """
        Метод для створення нового маршруту.

        Користувачу будуть запропоновані ввести початкову та кінцеву точки маршруту.
        Після цього маршрут буде створено і додано до списку маршрутів.

        Повертає:
        None
        """
        start_point, end_point = (
            input("Початкова точка: "),
            input("Кінцева точка: ")
        )
        route = Route(start_point, end_point)
        self.routes.append(route)
        return self.show_menu("Маршрут вдало створено!")
    

    @are_there_routes
    def delete_route(self):
        """
        Метод для видалення маршруту.

        Користувачу будуть запропоновані вибрати маршрут зі списку, який потрібно видалити.
        Вибраний маршрут буде видалений зі списку маршрутів.
        Усі автобуси, пов'язані з видаленим маршрутом, будуть повернуті до парку автобусів.

        Повертає:
        None
        """
        try:
            selected_route = self._get_selected_object_from_input(self.routes)
        except ReturnMenu:
            return self.show_menu()
        else:
            for bus in selected_route.bus_list:
                self.park.add_bus(bus)
            self.routes.remove(selected_route)
            return self.show_menu("Маршрут вдало видалено, а всі його автобуси відправлено до парку!")
        
    
    @are_there_buses
    @are_there_routes
    def show_route_buses(self):
        """
        Метод для відображення списку автобусів певного маршруту.

        Користувачу буде запропоновано вибрати маршрут зі списку.
        Після вибору, відображається список автобусів, пов'язаних з обраним маршрутом.

        Повертає:
        None
        """
        try:
            selected_route = self._get_selected_object_from_input(self.routes)
        except ReturnMenu:
            return self.show_menu()
        else:
            msg = f"У '{selected_route}' такі автобуси: \n"
            buses = self._compose_objects_list_for_selecting(selected_route.bus_list)
            return self.show_menu(msg + '\n'.join(buses))
        
    
    @are_there_buses
    @are_there_routes
    def show_buses_in_routes(self):
        """
        Метод для відображення списку автобусів на маршрутах.

        Виводиться список автобусів, які знаходяться на маршрутах разом з назвами маршрутів.

        Повертає:
        None
        """
        for index, bus in enumerate(self.buses, 1):
            if bus.route:
                print(f'[{index}] - {bus} - {bus.route}')
        return self.show_menu()
    

    @are_there_buses
    def show_buses_in_park(self):
        """
        Метод для відображення списку автобусів у парку.

        Виводиться список автобусів, які знаходяться у парку автобусів.

        Повертає:
        None
        """
        for index, bus in enumerate(self.park.bus_list, 1):
            print(f'[{index}] - {bus}')
        return self.show_menu()


    @are_there_buses
    @are_there_routes
    def set_route_for_bus(self):
        """
        Метод для призначення маршруту для автобуса.

        Користувачеві буде запропоновано вибрати автобус та маршрут зі списку.
        Після вибору, перевіряється поточний маршрут автобуса. Якщо він вже співпадає з обраним,
        виводиться повідомлення про це. В іншому випадку, маршрут для автобуса змінюється,
        а автобус додається до нового маршруту.

        Повертає:
        None
        """
        try:
            selected_bus = self._get_selected_object_from_input(self.buses)
            selected_route = self._get_selected_object_from_input(self.routes)
        except ReturnMenu:
            return self.show_menu()
        else:
            if selected_bus.route:
                if selected_bus.route is selected_route:
                    return self.show_menu("[!] Обрано один й той самий маршрут для автобусу, ніяких змін не внесено.")
                
                msg = f"Маршрут автобусу було змінено з '{selected_bus.route}' на '{selected_route}'"
                selected_route.add_bus(selected_bus)
                return self.show_menu(msg)
            
            selected_route.add_bus(selected_bus)
            return self.show_menu(f"Для автобусу встановлено {selected_route}")
        

    @are_there_buses
    def return_bus_to_park(self):
        """
        Метод для повернення автобуса до парку.

        Користувачеві буде запропоновано вибрати автобус зі списку.
        Після вибору, перевіряється поточний маршрут автобуса.
        Якщо автобус вже знаходиться у парку, виводиться відповідне повідомлення.
        В іншому випадку, автобус повертається до парку, його маршрут знімається.

        Повертає:
        None
        """
        try:
            selected_bus = self._get_selected_object_from_input(self.buses)
        except ReturnMenu:
            return self.show_menu()
        else:
            if not selected_bus.route:
                return self.show_menu("[!] Автобус наразі знаходиться у парку.")
            msg = f"Автобус вдало повернено до парку та знято з '{str(selected_bus.route)}'"
            self.park.add_bus(selected_bus)
            return self.show_menu(msg)
                

    def _get_selected_object_from_input(self, objects: list[Bus | Route]) -> Bus | Route:
        """
        Метод для отримання обраного об'єкта зі списку.

        Приймає список об'єктів `objects`, з якого користувач має обрати один об'єкт.
        Виводиться список об'єктів для вибору. Після вибору, перевіряється чи обрана опція
        є в списку валідних опцій. Якщо обрана опція є останньою (повернення до меню),
        викликається виняток ReturnMenu. В іншому випадку, повертається обраний об'єкт.

        Параметри:
        - objects (list[Bus | Route]): Список об'єктів для вибору.

        Повертає:
        - Bus | Route: Обраний об'єкт.

        Викидає:
        - ReturnMenu: Якщо обрана опція - повернення до меню.
        """
        options = self._compose_objects_list_for_selecting(objects)
        options.append(f'[{len(options)}] - повернутись до меню: ')

        try:
            selected_option = int(input('\n'.join(options)) + '\n\n')
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
        """
        Метод для створення списку об'єктів для вибору.

        Приймає список об'єктів `objects` і створює список опцій для вибору об'єкта.
        Кожна опція має вигляд `[індекс] - назва_об'єкта`.

        Параметри:
        - objects (list[Bus | Route]): Список об'єктів.

        Повертає:
        - list[str]: Список опцій для вибору об'єкта.
        """
        options = []
        for option_index, object in enumerate(objects):
            options.append(
                f'[{option_index}] - {str(object)}'
            )
        return options
            
    
    def _is_answer_existent(self, options: list[str], selected_option: int):
        """
        Метод для перевірки, чи обрана опція існує у списку опцій.

        Приймає список опцій `options` і обрану опцію `selected_option`.
        Перевіряє, чи обрана опція є в діапазоні індексів списку опцій.

        Параметри:
        - options (list[str]): Список опцій.
        - selected_option (int): Обрана опція.

        Повертає:
        - bool: True, якщо обрана опція існує, False - в іншому випадку.
        """
        options_range = range(len(options))
        if selected_option in options_range:
            return True
        else:
            return False
            

if __name__ == '__main__':
   BusStation().show_menu()