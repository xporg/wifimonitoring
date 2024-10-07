import pywifi
import time
from pywifi import const
import os

def scan():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)
    results = iface.scan_results()
    
    networks = {}
    for network in results:
        networks[network.ssid] = network.signal  # Сохраняем SSID как ключ, а силу сигнала как значение
    
    return networks  # Возвращаем словарь

def choose():
    os.system('cls')
    choosen = input('wi-fi monitoring.\n\n[1] - Начать калибровку\n[2] - Быстрое сканирование Wi-Fi сетей\n[3] - Запустить мониторинг устройства\n[4] - Информация\n\nВыберите действие: ')
    
    if choosen == '1':
        os.system('cls')
        calibration()
    elif choosen == '2':
        os.system('cls')
        networks = scan()
        for ssid, signal in networks.items():
            print(f"SSID: {ssid}, Signal: {signal}")
        choosen = input('Выберите действие:\n[1] - вернутся в главное меню\n[2] - выйти из программы: ')
        if choosen == '1':
            choose()
        elif choosen == '2':
            exit()
    elif choosen == '3':
        os.system('cls')
        tracking()
    elif choosen == '4':
        os.system('cls')
        print('Wi-Fi monitoring — это программа, которая позволяет отслеживать местоположение устройств на территории на основе силы Wi-Fi сигнала.\nИспользуя калибровочные данные для каждой точки пространства (верх, низ, лево, право, центр), программа вычисляет изменения в уровне сигнала для сетей Wi-Fi\nи на основе этих данных определяет расстояния по горизонтали и вертикали от центра.\n\nКак использовать программу?\n\nЕсли используете программу в 1 раз:\nВыберите опцию 1 в главном меню для начала калибровки.\nПрограмма попросит вас подойти к каждому из краев вашей территории (правый, левый, верхний, нижний). В каждом крае программа запишет силу Wi-Fi сигналов в файл.\nВ конце калибровки вам будет предложено ввести расстояния по горизонтали и вертикали между этими точками для точных вычислений.\n\nТрекинг: Выберите опцию 4 для начала отслеживания. Программа сравнит текущие данные Wi-Fi с калибровочными, рассчитает изменения сигналов и определит расстояния.\n\nПогрешность программы составляет около 1 метра на открытых пространствах и до 2-5 метров при нахождении устройства за стенами.\n')
        choosen = input('Выберите действие:\n[1] - вернутся в главное меню\n[2] - выйти из программы: ')
        if choosen == '1':
            choose()
        elif choosen == '2':
            exit()
def calibration():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    points = {
        'right': 'самой правой',
        'left': 'самой левой',
        'up': 'самой верхней',
        'down': 'самой нижней',
        'middle': 'центральной'
    }

    for point, description in points.items():
        input(f'Подойдите к {description} точке территории.\n\nНажмите любую клавишу, когда будете готовы: ')
        networks = scan()

        if networks:
            filename = os.path.join(script_dir, f'{point}networks.txt')
            with open(filename, 'w', encoding='utf-8') as file:
                for ssid, signal in networks.items():
                    file.write(f'SSID: {ssid}, Signal: {signal}\n')
            print(f'Данные калибровки сохранены в {filename}')
        else:
            print(f'Не удалось найти сети в точке {description}.')
        time.sleep(1)
        os.system('cls')
    
    with open(os.path.join(script_dir, 'distance.txt'), 'w', encoding='utf-8') as file:
        horizontal_distance = float(input("Введите расстояние слева направо (в метрах): "))
        vertical_distance = float(input("Введите расстояние сверху вниз (в метрах): "))
        file.writelines(f'{horizontal_distance}\n{vertical_distance}')
    
    print('Калибровка завершена успешно.')
    time.sleep(3)
    os.system('cls')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_right = os.path.join(script_dir, 'rightnetworks.txt')
    file_left = os.path.join(script_dir, 'leftnetworks.txt')
    file_up = os.path.join(script_dir, 'upnetworks.txt')
    file_down = os.path.join(script_dir, 'downnetworks.txt')
    compare_networks(file_right, file_left, file_up, file_down)
    choose()

def read_networks_from_file(filename):
    networks = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(", ")
                if len(parts) == 2:
                    ssid = parts[0].split(": ")[1]  # Получаем SSID
                    signal = int(parts[1].split(": ")[1])  # Получаем силу сигнала
                    networks[ssid] = signal
                else:
                    print(f"Ошибка формата строки: {line.strip()}")
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    return networks

def compare_networks(file1, file2, file3, file4):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    networks1 = read_networks_from_file(file1)
    networks2 = read_networks_from_file(file2)
    networks3 = read_networks_from_file(file3)
    networks4 = read_networks_from_file(file4)

    common_ssids = set(networks1.keys()) & set(networks2.keys()) & set(networks3.keys()) & set(networks4.keys())
    
    if common_ssids:
        for ssid in common_ssids:
            signal1 = networks1[ssid]
            signal2 = networks2[ssid]
            signal3 = networks3[ssid]
            signal4 = networks4[ssid]

            signal_diff1 = (signal1 + abs(signal2))
            signal_diff3 = (signal3 + abs(signal4))

            with open(os.path.join(script_dir, 'distance.txt'), 'r') as file:
                horizontal_distance = float(file.readline().strip())
                vertical_distance = float(file.readline().strip())

            signal_change_per_meter_horizontal = signal_diff1 / horizontal_distance
            signal_change_per_meter_vertical = signal_diff3 / vertical_distance
            
            with open(os.path.join(script_dir, 'dbm.txt'), 'a') as file:
                file.write(f'SSID: {ssid}, hdbm: {round(signal_change_per_meter_horizontal, 1)}, vdbm: {round(signal_change_per_meter_vertical, 1)}\n')

    else:
        print("Нет общих SSID.")

def tracking():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dbm_filename = os.path.join(script_dir, 'dbm.txt')
    middle_filename = os.path.join(script_dir, 'middlenetworks.txt')

    try:
        middle_networks = read_networks_from_file(middle_filename)
    except FileNotFoundError:
        print(f"Файл {middle_filename} не найден.")
        return

    hdbm_dict = {}
    vdbm_dict = {}
    try:
        with open(dbm_filename, 'r') as file:
            for line in file:
                parts = line.strip().split(", ")
                ssid = parts[0].split(": ")[1]
                hdbm = float(parts[1].split(": ")[1])
                vdbm = float(parts[2].split(": ")[1])
                hdbm_dict[ssid] = hdbm
                vdbm_dict[ssid] = vdbm
    except FileNotFoundError:
        print(f"Файл {dbm_filename} не найден.")
        return

    current_networks = scan()

    horizontal_distances = []
    vertical_distances = []

    for ssid, current_signal in current_networks.items():
        if ssid in middle_networks and ssid in hdbm_dict and ssid in vdbm_dict:
            signal_diff = current_signal - middle_networks[ssid]
            horizontal_distance = signal_diff * hdbm_dict[ssid]
            vertical_distance = signal_diff * vdbm_dict[ssid]
            
            horizontal_distances.append(horizontal_distance)
            vertical_distances.append(vertical_distance)

            print(f"SSID: {ssid}, Горизонтальное расстояние: {horizontal_distance:.2f} м, Вертикальное расстояние: {vertical_distance:.2f} м")

    if horizontal_distances and vertical_distances:
        avg_horizontal_distance = sum(horizontal_distances) / len(horizontal_distances)
        avg_vertical_distance = sum(vertical_distances) / len(vertical_distances)

        print(f"\nСреднее расстояние по горизонтали: {avg_horizontal_distance:.2f} м")
        print(f"Среднее расстояние по вертикали: {avg_vertical_distance:.2f} м")
    else:
        print("Не найдено сетей для сравнения с калибровочными данными.")
    
    choosen = input('Выберите действие:\n[1] - вернутся в главное меню\n[2] - выйти из программы: ')
    if choosen == '1':
        choose()
    elif choosen == '2':
        exit()

choose()
