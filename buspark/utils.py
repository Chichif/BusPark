from models import (Bus,
                    Route,
                    Departure)
from signals import ReturnMenu


def get_object_from_suggested_options(objects: list[Bus | Route]) -> Bus | Route:
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
            return get_object_from_suggested_options(objects)
        else:
            if is_answer_existent(options, selected_option):
                if selected_option == range(len(options))[-1]:
                    raise ReturnMenu()
                selected_object = objects[selected_option]
                return selected_object
            else:
                print("\n\n [!] Обрана неіснуюча опція :(")
                return get_object_from_suggested_options(objects)
            

def get_bus_active_departure(bus: Bus, active_departures: list[Departure]) -> Departure | None:
    """Повертає активний рейс автобуса.

    Параметри:
        bus (Bus): Автобус.
        active_departures (list[Departure]): Список активних рейсів.

    Returns:
        Departure | None: Об'єкт рейсу, в якому знаходиться автобус, або None, якщо автобус не знаходиться у жодному активному рейсі.
    """
    bus_departure: tuple[Departure] = next(
        filter(lambda departure: departure.bus == bus, active_departures),
        None
    )
    return bus_departure    

def get_route_buses(route: Route, bus_list: list[Bus]) -> list[Bus]:
    """Повертає список автобусів, які обслуговують заданий маршрут.

    Параметри:
        route (Route): Маршрут.
        bus_list (list[Bus]): Список автобусів.

    Returns:
        list[Bus]: Список автобусів, які обслуговують заданий маршрут.
    """
    return list(
        filter(lambda bus: bus.route is route, bus_list)
    )
        

def compose_objects_list_for_selection(objects: list[Bus | Route]) -> list[str]:
    """Створює список рядків для вибору об'єктів.

    Параметри:
        objects (list[Bus | Route]): Список об'єктів.

    Returns:
        list[str]: Список рядків для вибору об'єктів.
    """
    options = []
    for option_index, object in enumerate(objects):
        options.append(
            f"[{option_index}] - {object}"
        )
    return options
            
    
def is_answer_existent(options: list[str], selected_option: int) -> bool:
    """Перевіряє, чи існує вибраний варіант в списку.

    Параметри:
        options (list[str]): Список варіантів.
        selected_option (int): Вибраний варіант.

    Returns:
        bool: True, якщо вибраний варіант існує в списку, False - в іншому випадку.
    """
    options_range = range(len(options))
    if selected_option in options_range:
        return True
    return False