# -*- coding: utf-8 -*-

import os
import datetime
import shutil

separators = ['.CS#', '.AB#']

tftp_path = '/tftp/'
output = '/CiscoConfigs/'

bad_configs_path = output + 'bad/'
current_path = output + 'current/'
arcchive_path = output + 'archive/'
backup_path = arcchive_path + 'backup/'

key_date = 'Дата'
key_time = 'Время'
key_mtime = 'Метка'

def get_configs(path):

    tmp = os.listdir(path)

    configs_list = []

    for cfg in tmp:
        for sep in separators:

            if cfg.find(sep) != -1:
                configs_list.append(cfg)

    for cfg in tmp:
        if cfg in configs_list:
            pass
        else:
            src = tftp_path + cfg
            dst = bad_configs_path + cfg

            if not os.path.exists(bad_configs_path):
                os.makedirs(bad_configs_path)

            shutil.move(src, dst)

    return configs_list


def modification_date(filename):
    md = os.path.getmtime(filename)
    md_mtime = md
    md = str(datetime.datetime.fromtimestamp(md))
    md = md.split(' ')
    md_date = md[0]
    md_time, md_time_mark = md[1].split('.')
    #return md_date, md_time, md_time_mark, md_mtime
    return md_date, md_time, md_mtime


def get_configs_time(cfg_list):

    tmp_ct = {}

    for file in cfg_list:
        date, time, mtime = modification_date(tftp_path + file)
        tmp_ct[file] = {
            key_date: date,
            key_time: time,
            key_mtime: mtime
        }

    return tmp_ct


def short_name(name):

    for sep in separators:
        try:
            name.split(sep)[1]
        except IndexError:
            pass
        else:
            return name.split(sep)[0].upper()


def get_current():

    current_configs = {}

    for file in configs_list:
        name = short_name(file)
        if name not in current_configs:
            current_configs[name] = file
        else:
            if configs_list[file][key_mtime] >= configs_list[current_configs[name]][key_mtime]:
                current_configs[name] = file

    return current_configs


def month_format(month):

        mf = {
            '01': '01-Jan',
            '02': '02-Feb',
            '03': '03-Mar',
            '04': '04-Apr',
            '05': '05-May',
            '06': '06-Jun',
            '07': '07-Jul',
            '08': '08-Aug',
            '09': '09-Sep',
            '10': '10-Oct',
            '11': '11-Nov',
            '12': '12-Dec'
        }

        return mf[month]

backup = os.listdir(tftp_path)

if not os.path.exists(backup_path):
    os.makedirs(backup_path)

for file in backup:
    shutil.copyfile(tftp_path + file, backup_path + file)

configs_list = get_configs_time(get_configs(tftp_path))
current_list = get_current()

for dev in current_list:
    dst_name = dev
    src_name = current_list[dev]

    if not os.path.exists(current_path):
        os.makedirs(current_path)

    shutil.copyfile(tftp_path + src_name, current_path + dst_name)


for file in configs_list:

    date = configs_list[file][key_date].split('-')
    time = configs_list[file][key_time].split(':')

    year = date[0]
    month = month_format(date[1])


    dst_path_by_name = arcchive_path + 'by_name' + '/' + short_name(file) + '/'
    if not os.path.exists(dst_path_by_name):
        os.makedirs(dst_path_by_name)

    dst_name = configs_list[file][key_date] + '_' + time[0] + 'h' + time[1] + 'm' + time[2] + 's'

    shutil.copyfile(tftp_path + src_name, dst_path_by_name + dst_name)

    dst_path_by_date = arcchive_path + '/' + 'by_date' + '/' + year + '/' + month + '/'
    if not os.path.exists(dst_path_by_date):
        os.makedirs(dst_path_by_date)

    dst_name = short_name(file) + '_' + time[0] + 'h' + time[1] + 'm' + time[2] + 's'

    shutil.copyfile(tftp_path + src_name, dst_path_by_date + dst_name)

del_all = os.listdir(tftp_path)

for file in del_all:
    os.remove(tftp_path + file)
