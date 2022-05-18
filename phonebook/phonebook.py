# -*- coding: utf-8 -*-

#################################################################################################
# WEB PHONE DATA  ###############################################################################
#################################################################################################

def get_employee_data(line_input: str) -> dict:
    """
    Поулчает строку вида:
    ID;Центр;Отдел full;Отдел short;Должность full;Должность short;ФИО;Телефон;e-mail
    Перерабатывает ее в словарь. С корректировками данных.
    """

    line_input = line_input.replace('\n', '').split(';')

    if len(line_input) != 9:
        column_count_error(line_input)
        return {}
    elif line_input[4].lower().find('диспетч') != -1 or line_input[4].lower().find('водитель') != -1 or line_input[4] in post_exclude or line_input[2] in group_exclude:
        return {}

    phone_value, phone_short_value = phone_check(line_input[7], line_input[1])

    employee_data = {
        ID: line_input[0].replace('\xa0', ''),
        unit: line_input[1],
        group: cut_full_group(line_input[2], line_input[3], line_input[1]).replace('"', "'"),
        group_short: line_input[3].replace('"', "'"),
        post: line_input[4],
        post_short: line_input[5],
        fio: line_input[6],
        search_phone: line_input[7][:11],
        phone: phone_value,
        phone_short: phone_short_value,
        mail: email_check(line_input[8])
    }

    return employee_data


def cut_full_group(func_cfg_group: str, func_cfg_group_short: str, func_cfg_unit: str) -> str:
    """
    Поле 'Отдел full' содержит древовидную структуру перечисленную через запятую,
    в результате для верхушки дерева это поле дублирует поле 'Центр'.

    Функция обрезает верхушку. И в случае если верхушка == None, заменяет ее полем 'Отдел short'
    """
    func_cfg_group = func_cfg_group.split(func_cfg_unit)[1][2:]

    if not func_cfg_group:
        return func_cfg_group_short

    return func_cfg_group


def phone_check(func_pc_phone: str, func_pc_unit: str) -> tuple:
    default_phone_len = 11

    if len(func_pc_phone) < default_phone_len:
        return 'Отсутствует', '-'

    code = city_code(unit_name_switch(func_pc_unit))

    if len(func_pc_phone) > default_phone_len:
        func_pc_phone, add_phone = func_pc_phone[:default_phone_len], func_pc_phone[default_phone_len:]
    else:
        add_phone = None

    if func_pc_phone.find(code) == -1:
        code = '391'

    phone_hr = '+7 (' + code + ') ' + func_pc_phone[(1 + len(code)):(1 + len(code) + 3)] + '-' + \
               func_pc_phone[(1 + len(code) + 3):(1 + len(code) + 3 + 2)] + '-' + \
               func_pc_phone[(1 + len(code) + 3 + 2):(1 + len(code) + 3 + 2 + 2)]

    if phone_hr[-1] == '-':
        phone_hr = phone_hr[:-1]

    if add_phone:
        phone_hr += ' доб. ' + add_phone

    return phone_hr, get_short_phone(func_pc_phone, func_pc_unit)


def get_short_phone(full_phone: str, phone_unit: str) -> str:
    """
    Поулчает телефон, и наименование центра.
    В случае если в центре есть короткие номера - возвращает его значение.
    В противном случае заменяет поле символом '-'.
    """
    have_short = ['Дирекция', 'Красноярск', 'Норильск', 'Тура', 'Туруханск']

    phone_unit = unit_name_switch(phone_unit)

    if phone_unit in have_short:
        if phone_unit == 'Норильск':
            return '5' + full_phone[-3:]
        else:
            return full_phone[-4:]

    return '-'


def email_check(func_ec_mail: str) -> str:
    """
    Поулчает e-mail в виде строки.
    Проверяет его на принадлежность к корпоративному.
    Если указан личный e-mail - удаляет его.
    Помечает не заполненные.
    """

    if not func_ec_mail:
        return 'Отсутсвует'

    mail_postfix = 'cs.gkovd.ru'

    if func_ec_mail.find(mail_postfix) == -1:
        return 'confidential'

    return func_ec_mail.lower()


def unit_name_switch(func_uns_unit: str) -> str:
    """
    Принимает наименование центра, возвращает имя для файла центра
    """

    switch = {
        'Абаканский центр ОВД': 'Абакан',
        'Байкитский центр ОВД': 'Байкит',
        'Ванаварский центр ОВД': 'Ванавара',
        'Дирекция': 'Дирекция',
        'Енисейский центр ОВД': 'Енисейск',
        'Игарский центр ОВД': 'Игарка',
        'Кодинский центр ОВД': 'Кодинск',
        'Красноярский центр ОВД': 'Красноярск',
        'Норильский центр ОВД': 'Норильск',
        'Подкаменно-Тунгусский центр ОВД': 'П.Тунгуска',
        'Тувинский центр ОВД': 'Тува',
        'Туринский центр ОВД': 'Тура',
        'Туруханский центр ОВД': 'Туруханск',
        'Хатангский центр ОВД': 'Хатанга'
    }

    return switch[func_uns_unit]


def city_code(unit_name: str) -> str:
    cc_switch = {
        'Абакан': '3902',
        'Байкит': '39178',
        'Ванавара': '391',
        'Дирекция': '391',
        'Енисейск': '39195',
        'Игарка': '39172',
        'Кодинск': '39143',
        'Красноярск': '391',
        'Норильск': '3919',
        'П.Тунгуска': '391',
        'Тува': '394',
        'Тура': '391',
        'Туруханск': '391',
        'Хатанга': '39176'
    }

    return cc_switch[unit_name]


def column_count_error(line: list) -> None:
    """
    Обработка ошибки.
    Вызывается когда колличество столбцов в строке ввода отличается от стандартного (9).
    Получает на вход разделенную строку в виде списка.
    Выводит эту строку на консоль.
    """
    multiplier = 64

    out_error_line = ''

    for el in line:
        out_error_line += el + ';'

    print('-' * multiplier)
    print('ERROR: Строка не может быть обработана')
    print('ERROR: Ошибка колличества столбцов')
    print('Line: ' + out_error_line[:-1])
    print('-' * multiplier)

    return None


#################################################################################################
# Ппараметры ####################################################################################
#
#
#   Входные данные, путь к выгрузке и его кодировка
input_data_path = '/mnt/phonebook_data/PhoneBook.csv'
default_encoding = 'cp1251'
#
#
#   Выходные данные
out_data_path = '/var/www/PhoneBook/data/'
#
#
#   Ключи словарая, не влияют на результат
#   Нужны только для визуальной отладки
ID = 'ID'
unit = 'Центр'
group = 'Отдел'
group_short = 'Отдел кратко'
post = 'Должность'
post_short = 'Должность кратко'
fio = 'ФОИ'
phone = 'Телефон'
phone_short = 'Короткий'
search_phone = 'Телефон (поиск)'
mail = 'e-mail'
#
#
#   Исключения, должности / отделы не попадут в финальный результат
post_exclude = [
    'Инспектор',
    'Уборщик произв и служ помещений',
    'Уборщик территорий',
    'Слесарь-сантехник',
    'Санитарка',
    'Сменный инженер службы ЭРТОС',
    'Старший сменный инженер ЭРТОС',
    'Лифтёр',
    'Маляр',
    'Грузчик',
    'Плотник',
    'Электрогазосварщик',
    'Сторож',
    'Техник',
    'Токарь',
    'Слесарь по рем автомобилей',
    'Слесарь-ремонтник',
    'Машинист экскаватора',
    'Машинист ДВС',
 #   'Инженер по р/н, р/л и связи',
 #   'Техник по р/н, р/л и связи',
 #   'Ст техник по р/н, р/л и связи',
 #   'Вед инженер по р/н, р/л и связи'
]

group_exclude = [
]

#
#
#################################################################################################

#################################################################################################
#   Читаем файл и определяем список состоящий из словарей
#   где каждый словарь - информация о сотруднике
employees = []
with open(input_data_path, 'r', encoding=default_encoding) as data_input:
    for data_line in data_input:

        data_line = get_employee_data(data_line)

        if data_line:
            employees.append(data_line)
#################################################################################################


#################################################################################################

data_header = 'window.dataSet = [\n'
data_footer = '];'

data_full = open(out_data_path + '0.data.js', 'w')
data_full.write(data_header)

unit_list = []

for employee in employees:
    if employee[unit] not in unit_list:
        unit_list.append(employee[unit])
        data_unit = open(out_data_path + unit_name_switch(employee[unit]) + '.js', 'w')
        data_unit.write(data_header)
    else:
        data_unit = open(out_data_path + unit_name_switch(employee[unit]) + '.js', 'a')

    line_all = f'\t["{employee[ID]}", "{employee[unit]}", ' \
               f'"{employee[group]}", "{employee[group_short]}", ' \
               f'"<a title=\'{employee[group]}\'>{employee[group_short]}</a>", ' \
               f'"{employee[post]}", "{employee[post_short]}", ' \
               f'"<a title=\'{employee[post]}\'>{employee[post_short]}</a>", ' \
               f'"{employee[fio]}", "{employee[search_phone]}", "{employee[phone]}", ' \
               f'"<a align=\'center\'>{employee[phone_short]}</a>", "{employee[mail]}"],\n'

    line_unit = f'\t["{employee[ID]}", ' \
                f'"{employee[group]}", "{employee[group_short]}", ' \
                f'"<a title=\'{employee[group]}\'>{employee[group_short]}</a>", ' \
                f'"{employee[post]}", "{employee[post_short]}", ' \
                f'"<a title=\'{employee[post]}\'>{employee[post_short]}</a>", ' \
                f'"{employee[fio]}", "{employee[search_phone]}", "{employee[phone]}", ' \
                f'"<a align=\'center\'>{employee[phone_short]}</a>", "{employee[mail]}"],\n'

    data_full.write(line_all)
    data_unit.write(line_unit)

    data_unit.close()

for unit in unit_list:

    data_unit = open(out_data_path + unit_name_switch(unit) + '.js', 'a')
    data_unit.write(data_footer)
    data_unit.close()

data_full.write(data_footer)
data_full.close()
