# -*- coding: utf-8 -*-

import os
import re
import dns.resolver
import dns.reversename

default_code = 'UTF-8'

cisco_key_iface = 'interface'
cisco_key_sep = '!'
cisco_key_shutdown = 'shutdown'
cisco_key_mode = 'switchport mode'
cisco_key_voice = 'switchport voice vlan'
cisco_key_access = 'switchport access vlan'
cisco_key_descr = 'description'
cisco_key_ip = ' ip address'

d_key_shutdown = 'Shutdown'
d_key_mode = 'PortMode'
d_key_voice = 'Телефония'
d_key_access = 'Access'
d_key_fqdn = 'Устройство'
d_key_aliace = 'Aliace'
d_key_fqnd = 'FQND'
d_key_ip = 'IP'
d_key_port = 'Порт'

current_path = '/CiscoConfigs/current/'
data_path = '/var/www/cisco/data/'
#current_path = 'c:\\temp\\current\\'
#data_path = 'c:\\temp\\data\\'


def lookup(name):
    nslookup = dns.resolver.Resolver()
    nslookup.nameservers = ['10.24.5.2', '10.24.5.3']
    try:
        ip = nslookup.query(name)[0]
        ip = str(ip)
    except dns.exception.DNSException:
        ip = 'DNS error'
    try:
        qname = nslookup.query(dns.reversename.from_address(ip), 'PTR')[0]
        qname = str(qname).split('.')[0].upper()
    except dns.exception.DNSException:
        qname = 'PTR error'

    return ip, qname


def get_description(description):
    description = description.replace('\n', '')
    # Значения по умолчанию
    gd_fqdn, gd_aliace, gd_ip, gd_port = 'aliace', 'FQND', 'IP', 'PORT'

    # Шаблон описания ';;; PORT | DEVICE'

    descr_pars = re.match(r'^;;;\s(\S+)\s\W\s(\S+)\s?\W?\s?(\S+)?$', description)

    if descr_pars:
        descr_pars = descr_pars.groups()
        gd_port, gd_aliace = descr_pars[0], descr_pars[1]
        gd_ip, gd_fqdn = lookup(gd_aliace)

    else:
        gd_aliace, gd_fqdn, gd_ip, gd_port = description, '-', '-', '-'




    return gd_aliace, gd_fqdn, gd_ip, gd_port


def format_web_port_mode(port_mode):

    port_mode = port_mode.lower()

    web_format_mode = {
        'access': "<img src='/images/access.png' alt='ACCESS'>",
        'trunk': "<img src='/images/trunk.png' alt='TRUNK'>",
        'none': "NONE"
    }

    return web_format_mode[port_mode]


def format_web_port_status(port_status):

    port_status = port_status.lower()

    web_format_status = {
        'no': "<img src='/images/online.png' alt='ON'>",
        'yes': "<img src='/images/offline.png' alt='OFF'>",
        'none': "NONE"
    }

    return web_format_status[port_status]


def format_web_voice(voice_status):

    web_format_voice = {
        '120': "<img src='/images/on-phone.png' alt='Yes'>",
        'NO': "<img src='/images/off-phone.png' alt='No'>",
    }

    if voice_status in web_format_voice:
        return web_format_voice[voice_status]

    else: return voice_status


def name_translator(aliace):

# Ручная локализация латиница -> кирилица

    name_dictionary = {
        'trotckii': 'Троцкий'
    }

    try:
        return name_dictionary[aliace.lower()]
    except KeyError:
        return '-'

files_name_list = os.listdir(current_path)


iface_configs = {}

for file in files_name_list:
    file_config = open(current_path + file, 'r', encoding=default_code).readlines()

    iface_configs[file] = {}

    for i in range(len(file_config)):
        file_config[i] = file_config[i].replace('\n', '')


        if file_config[i].find(cisco_key_iface) != -1:

            iface_name = file_config[i].split(cisco_key_iface)[1][1:]

            iface_configs[file][iface_name] = {d_key_shutdown: 'NO', d_key_mode: 'None', d_key_voice: 'NO', d_key_access: '-', d_key_fqdn: '-', d_key_aliace: '-', d_key_ip: '-', d_key_port: '-'}

            while True:
                i += 1

                if file_config[i].find(cisco_key_shutdown) != -1:
                    iface_configs[file][iface_name][d_key_shutdown] = 'YES'

                if file_config[i].find(cisco_key_mode) != -1:
                    iface_configs[file][iface_name][d_key_mode] = file_config[i].split(cisco_key_mode)[1][1:-1]

                if file_config[i].find(cisco_key_voice) != -1:
                    iface_configs[file][iface_name][d_key_voice] = file_config[i].split(cisco_key_voice)[1][1:-1]

                if file_config[i].find(cisco_key_access) != -1:
                    iface_configs[file][iface_name][d_key_access] = file_config[i].split(cisco_key_access)[1][1:-1]

                if file_config[i].find(cisco_key_descr) != -1:

                    aliace, fqnd, ip, port = get_description(file_config[i].split(cisco_key_descr)[1][1:])

                    if file_config[i].find(cisco_key_ip) != -1:
                        iface_configs[file][iface_name][d_key_ip] = file_config[i].split(' ')[3]

                    iface_configs[file][iface_name][d_key_ip] = ip
                    iface_configs[file][iface_name][d_key_aliace] = aliace
                    iface_configs[file][iface_name][d_key_fqdn] = fqnd
                    iface_configs[file][iface_name][d_key_port] = port

                if file_config[i].find(cisco_key_ip) == 0:
                    iface_configs[file][iface_name][d_key_ip] = file_config[i].split(' ')[3]

                if file_config[i].find(cisco_key_sep) != -1:
                    break


js_data = open(data_path + 'data.js', 'w', encoding=default_code)

js_head = 'window.dataSet = [\n'
js_foot = '];'

js_data.write(js_head)

for sw in iface_configs:
    if sw.find('SW') != -1:
        for iface in iface_configs[sw]:

            web_port_mode = format_web_port_mode(iface_configs[sw][iface][d_key_mode])
            web_port_status = format_web_port_status(iface_configs[sw][iface][d_key_shutdown])
            web_voice_status = format_web_voice(iface_configs[sw][iface][d_key_voice])
            web_vlan = iface_configs[sw][iface][d_key_access]
            web_fqdn = iface_configs[sw][iface][d_key_fqdn]
            web_aliace = iface_configs[sw][iface][d_key_aliace]
            web_ip = iface_configs[sw][iface][d_key_ip]
            web_port = iface_configs[sw][iface][d_key_port]
            web_name = name_translator(web_aliace)

            line = f'''\t["{sw}", "{iface}", "{web_port_status}", "{web_port_mode}", "{web_voice_status}", "{web_vlan}", "{web_aliace}", "{web_name}", "{web_fqdn}", "{web_ip}", "{web_port}"],\n'''

            js_data.write(line)

js_data.write(js_foot)

js_data.close()
