from models import (Bus,
                    Route,
                    Departure)
from exceptions import ReturnMenu


def get_selected_object_from_input(objects: list[Bus | Route]) -> Bus | Route:
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
        options = compose_objects_list_for_selection(objects)
        options.append(f'[{len(options)}] - повернутись до меню: ')

        try:
            selected_option = int(input('\n'.join(options)) + '\n\n')
        except ValueError:
            print('\n\n [!] Введено не цифру/число!')
            return get_selected_object_from_input(objects)
        else:
            if is_answer_existent(options, selected_option):
                if selected_option == range(len(options))[-1]:
                    raise ReturnMenu()
                selected_object = objects[selected_option]
                return selected_object
            else:
                print("\n\n [!] Обрана неіснуюча опція :(")
                return get_selected_object_from_input(objects)
            

def get_bus_active_departure(bus: Bus, active_departures: list[Departure]) -> Departure | None:
        """
        Приватний метод, який повертає активне відправлення для заданого автобуса.
        """
        bus_departure: tuple[Departure] = tuple(
            filter(lambda departure: departure.bus == bus, active_departures)
        )
        if bus_departure: # гарантовано, що не більше 1
                          # адже відправити один автобус два рази на маршрут - неможливо
            return bus_departure[0]
        else: 
            return None
        

def get_route_buses(route: Route, bus_list: list[Bus]) -> list[Bus]:
        """
        Приватний метод, який повертає список автобусів, прив'язаних до вказаного маршруту.
        """
        return list(
            filter(lambda bus: bus.route is route, bus_list)
        )
        

def compose_objects_list_for_selection(objects: list[Bus | Route]) -> list[str]:
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
                f"[{option_index}] - {object}"
            )
        return options
            
    
def is_answer_existent(options: list[str], selected_option: int) -> bool:
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
    return False