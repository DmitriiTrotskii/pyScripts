# -*- coding: utf-8 -*-

#######################################################################################################################
###########################################   WEB PHONE DATA 3.0  #####################################################
#######################################################################################################################

import os

'''
company;department;email;fileAs;firstName;homeCity;homeCountry;homeState;jobTitle;lastName;middleName;workPhone;workPhone2;workURL
'''

default_path = '/var/www/PhoneBook/'
data_input = '/opt/db2inst1/list.txt'
avaya_dir = '/var/www/PhoneBackup/phonebase/'

#default_path = 'C:\\temp\\PhoneBook\\'
#data_input = 'C:\\temp\\list.txt'
#avaya_dir = 'C:\\temp\\avaya\\'

default_encoding = 'utf-8'

lists_path = default_path + 'lists/'
data_path = default_path + 'data/'
sep_in = ':'
sep_out = ';'

d_key_city = 'Город'
d_key_company = 'Подразделение'
d_key_department = 'Отдел'
d_key_department_short = 'Отдел (сокр.)'
d_key_mail = 'e-mail'
d_key_jTitle = 'Должность'
d_key_jTitle_short = 'Должность (сокр.)'
d_key_phone = 'Телефон'
d_key_phone_short = 'Добавочный'
d_key_name = 'ФИО'
d_key_id = 'ID'

key_zimbra = '4'
homeCountry = 'Россия'
homeState = 'Красноярский край'
phonebook = 'http://phonebook.cs.gkovd.ru/'


exclude_jTitle = []

###########################################################
# Получение данных и их форматирование ####################
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def read_input(input_file):
    #   Считываем файл
    d_ri = open(input_file, 'r', encoding=default_encoding).readlines()

    #   d_ri = ['line1', 'line2', ..., 'lineN']

    #   Заменяем символы в считанном файле
    for i in range(len(d_ri)):
        d_ri[i] = d_ri[i].replace('"', "'")  # Заменяем двойные кавычки на одинарные
        d_ri[i] = d_ri[i].replace('\n', '')  # Убираем символ конца строки

    ############################################################################
    #   Формат выводимых данных:
    #
    #   Центр:Отдел:Должность:ФИО:Телефон:Почта:Должность(сокр.):Отдел(сокр.):ID
    ############################################################################
    #   0: Центр
    #   1: Отдел
    #   2: Должность
    #   3: ФИО
    #   4: Телефон
    #   5: Почта
    #   6: Должность (сокр.)
    #   7: Отдел (сокр.)
    #   8: ID
    #

    return list_to_dict(d_ri)


def list_to_dict(l_base):
    #   Переделываем формат базы из списка в список словарей
    #   Каждый словарь - отдельный пользователь

    ltd_base = []

    for ltd_emp in l_base:
        ltd_emp = ltd_emp.split(sep_in)

        ltd_tmp_line = {
            d_key_city: ltd_emp[0],
            d_key_company: company(ltd_emp[0]),
            d_key_department: ltd_emp[1],
            d_key_jTitle: ltd_emp[2],
            d_key_name: ltd_emp[3],
            d_key_phone: ltd_emp[4],
            d_key_phone_short: short_phone(ltd_emp[3], ltd_emp[4], ltd_emp[0]),
            d_key_mail: ltd_emp[5].lower(),
            d_key_jTitle_short: ltd_emp[6],
            d_key_department_short: ltd_emp[7],
            d_key_id: ltd_emp[8]
        }

        if ltd_tmp_line[d_key_jTitle_short] not in exclude_jTitle:
            ltd_base.append(ltd_tmp_line)

    return ltd_base


def company(center):
    c_dict = {
        'Дирекция': 'Дирекция Филлиала',
        'Абакан': 'Абаканский Центр ОВД',
        'Байкит': 'Байкитский Центр ОВД',
        'Ванавара': 'Ванаварский Центр ОВД',
        'Енисейск': 'Енисейский Центр ОВД',
        'Кодинск': 'Кодинский Центр ОВД',
        'Игарка': 'Игарский Цетнр ОВД',
        'Красноярск': 'Красноярский Центр ОВД',
        'Норильск': 'Норильской Цетнр ОВД',
        'П.Тунгуска': 'П.Тунгуский Центр ОВД',
        'Тува': 'Тувинский Цетнр ОВД',
        'Тура': 'Туринский Центр ОВД',
        'Туруханск': 'Туруханский Центр ОВД',
        'Хатанга': 'Хатангский Центр ОВД',
    }

    return c_dict[center]


def short_phone(name, phone_number, company):

    have_short_phone = ['Красноярск', 'Дирекция', 'Норильск']

    if company in have_short_phone:

        phone_number = phone_number.replace('(', '').replace(')', '').replace('-', '')

        if company == 'Норильск':
            return '5' + phone_number[-3:]

        return phone_number[-4:]

    if company in short_phones:
        if name in short_phones[company]:
            return short_phones[company][name]

    return '-'


def short_phone_local_base():

    splb = {}

    splb_list = os.listdir(default_path + 'shortphones')

    for file in splb_list:
        splb[file] = {}
        tmp = open(default_path + 'shortphones/' + file, 'r', encoding=default_encoding).readlines()
        for el in tmp:
            el = el.replace('\n', '').split(';')
            splb[file][el[0]] = el[1]

    return splb

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
###########################################################
#
#
#
###########################################################
# Выгрузка списков контактов в .CSV  ######################
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def get_emp_name(fullName):
    g_lastName, g_firstName, g_middleName = '-', '-', '-'

    fullName = fullName.split(' ')

    try:
        g_lastName = fullName[0]
    except IndexError:
        pass

    try:
        g_firstName = fullName[1]
    except IndexError:
        pass

    try:
        g_middleName = fullName[2]
    except IndexError:
        pass

    return g_lastName, g_firstName, g_middleName


def lists():
    list_head = 'company;department;email;' \
                'fileAs;firstName;' \
                'homeCity;homeCountry;' \
                'homeState;jobTitle;lastName;' \
                'middleName;workPhone;workPhone2;workURL\n'

    list_all = open(lists_path + 'ALL.CSV', 'w', encoding=default_encoding)
    list_all.write(list_head)

    city = []

    for emp in base:
        if emp[d_key_city] not in city:

            city.append(emp[d_key_city])

            list_c = open(lists_path + emp[d_key_city] + '.CSV', 'w', encoding=default_encoding)
            list_c.write(list_head)

        else:
            list_c = open(lists_path + emp[d_key_city] + '.CSV', 'a', encoding=default_encoding)

        lastName, firstName, middleName = get_emp_name(emp[d_key_name])

        line = emp[d_key_company] + sep_out + emp[d_key_department_short] + sep_out + emp[d_key_mail] + sep_out + \
               key_zimbra + sep_out + firstName + sep_out + emp[d_key_city] + sep_out + homeCountry + sep_out + \
               homeState + sep_out + emp[d_key_jTitle_short] + sep_out + lastName + sep_out + middleName + sep_out + \
               emp[d_key_phone] + sep_out + emp[d_key_phone_short] + sep_out + phonebook + '\n'

        list_c.write(line)
        list_c.close()

        list_all.write(line)
    list_all.close()

    return None


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
###########################################################
#
#
#
###########################################################
# Выгрузка базы для WEB формы  ############################
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def data():
    data_header = 'window.dataSet = [\n'

    data_all = open(data_path + '0.data.js', 'w', encoding=default_encoding)
    data_all.write(data_header)

    city_list = []

    for emp in base:

        s_phone = emp[d_key_phone].replace('(', '').replace(')', '').replace('-', '')

        if emp[d_key_city] not in city_list:

            city_list.append(emp[d_key_city])

            data_c = open(data_path + emp[d_key_city] + '.js', 'w', encoding=default_encoding)
            data_c.write(data_header)
        else:
            data_c = open(data_path + emp[d_key_city] + '.js', 'a', encoding=default_encoding)

        line_all = f'\t["{emp[d_key_id]}", "{emp[d_key_city]}", ' \
            f'"{emp[d_key_department]}", "{emp[d_key_department_short]}", "<a title=\'{emp[d_key_department]}\'>{emp[d_key_department_short]}</a>", ' \
            f'"{emp[d_key_jTitle]}", "{emp[d_key_jTitle_short]}", "<a title=\'{emp[d_key_jTitle]}\'>{emp[d_key_jTitle_short]}</a>", ' \
            f'"{emp[d_key_name]}", "{s_phone}", "{emp[d_key_phone]}", ' \
            f'"<a align=\'center\'>{emp[d_key_phone_short]}</a>", "{emp[d_key_mail]}"],\n'

        line_c = f'\t["{emp[d_key_id]}", ' \
            f'"{emp[d_key_department]}", "{emp[d_key_department_short]}", "<a title=\'{emp[d_key_department]}\'>{emp[d_key_department_short]}</a>", ' \
            f'"{emp[d_key_jTitle]}", "{emp[d_key_jTitle_short]}", "<a title=\'{emp[d_key_jTitle]}\'>{emp[d_key_jTitle_short]}</a>", ' \
            f'"{emp[d_key_name]}", "{s_phone}", "{emp[d_key_phone]}", ' \
            f'"<a href=\'avaya://video?{emp[d_key_phone_short]}\' align=\'center\'>{emp[d_key_phone_short]}</a>", "{emp[d_key_mail]}"],\n'

        data_c.write(line_c)
        data_all.write(line_all)

    for city in city_list:

        data_c = open(data_path + city + '.js', 'a', encoding=default_encoding)
        data_c.write('];')
        data_c.close()

    data_all.write('];')
    data_all.close()

    return None


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
###########################################################


def for_avaya():

    avaya = open(avaya_dir + 'phones', 'w', encoding=default_encoding)

    for line in base:
        if line[d_key_city] == 'Дирекция':
            avaya.write(line[d_key_name] + sep_out + line[d_key_phone_short] + '\n')

    avaya.close()


short_phones = short_phone_local_base()

base = read_input(data_input)

lists()

data()

for_avaya()
