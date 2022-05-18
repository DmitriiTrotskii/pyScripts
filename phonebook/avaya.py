# -*- coding: utf-8 -*-

import os

default_encoding = 'utf-8'

max = 12 # максимальное колличество символов в Фамилии + 1, за исключением 4х символов на И.О.

# путь к csv файлу
# принимаемый формат данных
# company;department;email;fileAs;firstName;homeCity;homeCountry;homeState;jobTitle;lastName;middleName;workPhone;workPhone2;workURL
phones = '/var/www/PhoneBook/lists/test.csv'

cfg_name = 'ABKNAME'
cfg_phone = 'ABKNUMBER'
cfg_type = 'ABKTYPE'
type = '0'

cfg_sep_1 = 'PHNLABEL'
cfg_sep_2 = 'CLNAME'

# путь к коннфигам телефонов avaya
configs_path = '/var/www/PhoneBackup/PhoneBackup/'

# исключать из обрабоктки
exclude_phones = ['0000', '0001']

def get_contacs(phones_base):

    phones_base = open(phones_base, 'r', encoding=default_encoding).readlines()

    del phones_base[0]  # Удаление заголовка
    # company;department;email;fileAs;firstName;homeCity;homeCountry;homeState;jobTitle;lastName;middleName;workPhone;workPhone2;workURL

    node = sort_contacs(phones_base)

    contacs = ''

    i = 0

    for user in node:
        i = i + 1
        index = take_index(i)

        user = user.split(';')

        # ABKNAME001=Фамилия И.О.
        # ABKNUMBER001=6762
        # ABKTYPE001=0

        contacs += cfg_name + index + '=' + user[0] + '\n' \
                   + cfg_phone + index + '=' + user[1] + '\n' \
                   + cfg_type + index + '=' + type + '\n'

    return contacs

def sort_contacs(s_c_phone_base):

    s_c_node = []

    for line in s_c_phone_base:
        line = line.split(';')

        line = line[9][:max] + ' ' + line[4][0] + '.' + line[10][0] + '.' + ';' + line[12]

        s_c_node.append(line)

    s_c_node.sort()

    return s_c_node

def take_index(num):

    num = str(num)

    if len(num) == 1:
        num = '00' + num

    if len(num) == 2:
        num = '0' + num

    else:
        pass

    return num

def add_contacts_to_cfg(config):

    for config in configs_list:

        config_data = open(configs_path + config, 'r', encoding='utf-16').readlines()

        tmp_cfg = []

        for line in config_data:
            if line.find(cfg_name) != -1 or line.find(cfg_phone) != -1 or line.find(cfg_type) != -1:
                pass
            else:
                tmp_cfg.append(line)

        i = 0
        cfg = ''

        for i in range(len(tmp_cfg)):

            if i == 1:
                cfg = cfg + contacs

            cfg = cfg + tmp_cfg[i]

            i = i + 1

        config_data = open(configs_path + config, 'w', encoding='utf-16')
        config_data.write(cfg)
        config_data.close()

contacs = get_contacs(phones)

configs_list = os.listdir(configs_path)

for file in configs_list:

    phone = file.split('_')[0]

    if phone not in exclude_phones:

        print(phone)

        config_data = open(configs_path + file, 'r', encoding='utf-16').readlines()

        tmp_cfg = []

        for line in config_data:
            if line.find(cfg_name) != -1 or line.find(cfg_phone) != -1 or line.find(cfg_type) != -1:
                pass
            else:
                tmp_cfg.append(line)

        i = 0
        cfg = ''

        for i in range(len(tmp_cfg)):

            if i == 1:
                cfg = cfg + contacs

            cfg = cfg + tmp_cfg[i]

            i = i + 1

        config_data = open(configs_path + file, 'w', encoding='utf-16')
        config_data.write(cfg)
        config_data.close()
