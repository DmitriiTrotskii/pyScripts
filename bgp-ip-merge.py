#################################################################################################
'''
Необходимо прочитать файл с полной BGP таблицей
Сделать выборку всех ИП адресов маршрутизируемых указанной АС
Произвести возможное сложение всех сетей до максимально возможной маски
Подготовить данные для экспорта в БД
'''
#################################################################################################


from datetime import datetime


def ip_to_bin(ip: str) -> str:
    """
    Получает IP адрес в виде строки
    172.16.0.0
    Возвращает адрес в двоичном виде
    10101100000100000000000000000000
    """

    bin_ip = ''

    for itb_oct in ip.split('.'):
        itb_oct = str(bin(int(itb_oct))[2:])
        bin_ip += '0' * (8 - len(itb_oct)) + itb_oct

    return bin_ip


def sum_net(ip_1: str, ip_2: str) -> str:
    """
    Получачет две смежные сети
    Для каждой сети вызывает функции перевода в двоичный вид
    Возвращает суммированную подсеть и маску
    172.16.0.0  ->  1010110000010000000000000 0000000
    172.16.0.64 ->  1010110000010000000000000 1000000
    Результат сложения:
    172.16.0.0  ->  1010110000010000000000000 0000000
    25          ->  1111111111111111111111111 0000000
    """

    ip_1, ip_2 = ip_to_bin(ip_1), ip_to_bin(ip_2)

    sn_net_bin, sn_mask = '', ''

    s = 0

    for s in range(len(ip_1)):
        if ip_1[s] == ip_2[s]:
            sn_net_bin += ip_1[s]
        else:
            break

    sn_mask = str(s)
    sn_net_bin += (32 - len(sn_net_bin)) * '0'

    sn_net = '{0}.{1}.{2}.{3}'.format(str(int(sn_net_bin[:8], 2)), str(int(sn_net_bin[8:16], 2)),
                                      str(int(sn_net_bin[16:24], 2)), str(int(sn_net_bin[24:], 2)))

    return sn_net + '/' + sn_mask


def dict_by_mask(dbm_ls: list) -> dict:
    """
    Получает список сетей
    [x.x.x.x/y, z.z.z.z/y, ...]
    Возвращает словарь
    Ключ = подсеть
    Значение = список сетей
    {y: [x.x.x.x, z.z.z.z], ...}
    """

    """
    Генерируем избыточный словарь со всеми возможными масками в обратном порядке
    Это помжет избежать необходимости сортировки и проверок на наличие маски
    Кроме того избавит от необходимости несколько раз проходить словарь для сложения подсетей
    Сложение будет происходить от меньших к большим за один проход словоря
    """
    dbm_base = {x: [] for x in range(32, 0, -1)}

    for el in dbm_ls:
        ip, dbm_mask = el.split('/')
        dbm_base[int(dbm_mask)].append(ip)

    return dbm_base


def is_neighbor(nrct_1: str, nrct_2: str, sw: list) -> bool:
    """
    Получает два адреса в виде строки и их маску в виде числа
    172.16.0.0, 172.16.1.0, 24

    Так же получает два значения, октет и степень:
    Октет   -   порядок подсети
    Сетень  -   степень для получения шага подсети
    
    Прим.: [4, 6]
        4   -   подсеть нужно искать в 4 октете
        6   -   2**6 = 64, значит соседняя подсеть отличается от нашей на 64 в 4 октете
        вывод: подсети различаются на 64 в 4 октете
        Подсети смежны, подлежат сложению
        172.16.0.>0</26 и 172.16.0.>64</26  -   0 vs 64     -   различаются на 64
        Подсети смежны, подлежат сложению
        172.16.0.>0</26 и 172.16.0.>192</26 -   0 vs 192    -   не различаются на 64
        Подсети не смежны, не подлежат сложению
    Возвращает True - если подсети смежны
    Возвращает False - если подсети не смежны
    """
    nrct_1, nrct_2 = nrct_1.split('.'), nrct_2.split('.')

    net_oct, sq = sw[0], sw[1]

    #   Сравниваем первые октеты, они должны быть равны
    for oct in range(net_oct - 1):
        if nrct_1[oct] != nrct_2[oct]:
            return False

    #   Проверяем октет подсети, он не должен различатся больше чем на 2 ** sq
    if int(nrct_1[net_oct - 1]) + 2 ** sq == int(nrct_2[net_oct - 1]):
        return True

    return False


def debug(d_net_1: str, d_net_2: str, d_net_mask: str, d_new_net, d_new_mask: str, d_case_id: int) -> None:
    d_n = 64

    d_case = {
        0: 'Смежны, подлежат сложению',
        1: 'Смежны, но сложение образует пустоты'
    }

    print(d_n * '*')

    if d_case[d_case_id]:
        print(d_case[d_case_id])
        print(d_n * '-')

    print('{0}/{2} + {1}/{2} = {3}/{4}'.format(d_net_1, d_net_2, d_net_mask, d_new_net, d_new_mask))
    print(d_n * '-')
    print('Сеть 1:  ', ip_to_bin(d_net_1))
    print('Сеть 2:  ', ip_to_bin(d_net_2))
    print('Сеть 3:  ', ip_to_bin(d_new_net))
    print('Маска:   ', '1' * int(d_new_mask) + '0' * (32 - int(d_new_mask)))
    print(d_n * '*', '\n')

    return None


def mod_octets(fo_ip: str) -> str:
    """
    Принимает IP адрес в виде строки
    Дополняет октеты '0' до 3х символов, для сортировки
    либо
    Удаляет впередистоящие нули

    Прим.:
        172.16.0.0 -> 172.016.000.000
        192.168.010.064 -> 192.168.10.64
    """

    full_ip = ''

    for octet in fo_ip.split('.'):
        if len(octet) != 3:
            octet = '0' * (3 - len(octet)) + octet
        elif len(octet) == 3:
            if octet.startswith('00'):
                octet = octet[2:]
            elif octet.startswith('0'):
                octet = octet[1:]

        full_ip += octet + '.'

    return full_ip[:-1]


as_adresses = []
AS = ''

#   Генерируем значения октета и степени для всех масок
 #   switch = {Маска: [октет, степень], 1: [1, 7], ... 24: [3, 0], ..., 30: [4, 2], ...}
switch = {x + 1: [(x // 8 + 1), (8 - (x % 8 + 1))] for x in range(0, 32)}

while True:
    mode = input('Input mode (test or bgp): ')
    if mode == 'test' or mode == 'bgp':
        break

if mode == 'bgp':

    # file_path = input('Full path to bgp snapshot: ')
    # AS = input('AS number: ')
    file_path = 'C:\\oix-full-snapshot-latest.dat'
    AS = '197695'

    as_adresses = []
    file = open(file_path, 'r')
    for line in file:
        if AS in line:
            if line.rsplit()[1] not in as_adresses:
                as_adresses.append(line.rsplit()[1])

    file.close()

elif mode == 'test':
    as_adresses = ['172.16.0.0/26', '172.16.0.64/26', '172.16.0.128/26', '172.16.0.192/26', '192.168.0.128/26',
                   '192.168.0.64/26']
    AS = None

else:
    print('Somthing wrong...')
    exit()

adresses_id = 0

for adresses_id in range(len(as_adresses)):
    ip, mask = as_adresses[adresses_id].split('/')
    as_adresses[adresses_id] = mod_octets(ip) + '/' + mask

as_adresses.sort()

for adresses_id in range(len(as_adresses)):
    ip, mask = as_adresses[adresses_id].split('/')
    as_adresses[adresses_id] = mod_octets(ip) + '/' + mask

base = dict_by_mask(as_adresses)

for mask in range(32, 1, -1):
    if len(base[mask]) > 1:
        i, j = 0, len(base[mask])
        while i < j:
            try:

                #   В случае если остался один адрес
                #   Пары ему не найдется, и нужно прервать цикл

                base[mask][i + 1]
            except IndexError:
                break

            if is_neighbor(base[mask][i], base[mask][i + 1], switch[mask]):
                new_net, new_mask = sum_net(base[mask][i], base[mask][i + 1]).split('/')

                if int(new_mask) + 1 != mask:
                    #   Проверка на образование пустот
                    #   172.16.0.64/26 + 172.16.0.128/26 = 172.16.0.0/24, но
                    #   172.16.0.0/26 и 172.16.0.192/26 - не участвовали в объединении
                    #   не принимаем сложение, и переходим к следующей паре

                    #################################################################################################
                    #   Debug output
                    #
                    #   debug(base[mask][i], base[mask][i + 1], str(mask), new_net, new_mask, 1)
                    #
                    #################################################################################################

                    i += 1
                    continue

                #####################################################################################################
                #   Debug output
                #
                #   debug(base[mask][i], base[mask][i + 1], str(mask), new_net, new_mask, 0)
                #
                #####################################################################################################

                base[int(new_mask)].append(new_net)

                base[mask].remove(base[mask][i])
                base[mask].remove(base[mask][i])

                j -= 2

                continue

            i += 1

####################################################################################################################


insert_data = []

for key in base:
    if base[key]:
        for ip in base[key]:
            now = datetime.now()
            date = now.strftime("%d-%m-%Y")

            out = f"('{date}', '{AS}', '{ip}', '{key}')"

            ########################################################################################################
            #   For line output
            #
            #   print("{}".format(out))
            #
            ########################################################################################################

            insert_data.append(out)
