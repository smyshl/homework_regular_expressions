import csv
import re


def get_contact_list_from_csv_file():

    with open('phonebook_raw.csv', 'r', encoding='utf-8') as csv_file:
        rows = csv.reader(csv_file, delimiter=',')
        contact_list = list(rows)

    return contact_list


def save_new_contact_list_to_csv_file(contact_list_to_save):

    with open('phonebook.csv', 'w', newline='' , encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerows(contact_list_to_save)


def get_correct_names(names_list_to_analyse):
    """
    Получает список, содержащий фамилию, имя и отчество в разных возможных комбинациях
    Возвращает список списков фамилии, имени и отчества
    Множество в расчетах используется для того, чтобы объединить одинаковые значения имени фамилии или отчества, которые
    могут быть записаны в разных полях адресной книги
    :param names_list_to_analyse:
    :return:
    """

    correct_names_list = ['', '', '']

    names_list_to_analyse = [names_list_to_analyse[j].lower().split(' ') for j in range(3)]

    for j in range(3):
        len_bad_fio_list = len(names_list_to_analyse[j])
        delta_len = 3 - len_bad_fio_list

        if j != 0 and delta_len != 0:
            names_list_to_analyse[j].insert(0, '')
            delta_len = 3 - len(names_list_to_analyse[j])
            if delta_len != 0:
                if j == 1:
                    names_list_to_analyse[j].extend('' for _ in range(delta_len))
                else:
                    names_list_to_analyse[j].insert(0, '')

        if j == 0:
            names_list_to_analyse[j].extend(['' for _ in range(delta_len)])

    for j in range(3):
        correct_names_list[j] = {names_list_to_analyse[i][j].capitalize() for i in range(3) if names_list_to_analyse[i][j]}

    correct_names_list = [list(correct_names_list[i]) if correct_names_list[i] else [] for i in range(3)]

    return correct_names_list


def get_correct_phone_num(phone_num_to_analyse):

    pattern = r'(\+7|8)*\s*\(*(\d{3})\)*\s*[-]*(\d{3})\s*[-]*(\d{2})\s*[-]*(\d{2})\s?\(?(\w*[.]*)\s*(\d*)\)*'
    repl = r'+7(\2)\3-\4-\5 \6\7'

    return re.sub(pattern, repl, phone_num_to_analyse).rstrip()


def make_choice(choice_list):

    index_list = [i for i in range(len(choice_list))]
    chosen_list = [None]

    print('\nИз имеющихся значений необходимо выбрать одно, которое останется в базе')

    for i in index_list:
        print(f'{i} - {choice_list[i]}')

    chosen_index = input('Введите номер выбранного значения: ')

    if not chosen_index.isdigit():
        print('\nВвод не распознан. В базе будет сохранено первое значение из списка')
        chosen_index = 0
    elif not int(chosen_index) in index_list:
        print('\nВвод не распознан. В базе будет сохранено первое значение из списка')
        chosen_index = 0
    else:
        chosen_index = int(chosen_index)

    chosen_list[0] = choice_list[chosen_index]

    return chosen_list


def make_correct_record(record_to_correct):

    correct_names = get_correct_names(record_to_correct[0:3])
    corrected_record = record_to_correct.copy()

    for i in range(len(correct_names)):

        if len(correct_names[i]) > 1:
            print(f'\nВ записи {record_to_correct}\nимеется неоднозначность имен: {", ".join(correct_names[i])}')
            correct_names[i] = make_choice(correct_names[i])

        if correct_names[i]:
            corrected_record[i] = correct_names[i][0]
        else:
            corrected_record[i] = ''

    corrected_record[5] = get_correct_phone_num(corrected_record[5])

    return corrected_record


def fill_empty_fields(new_record, old_record):

    filled_fields_flag = 0

    for i in range(2, len(old_record)):
        if not old_record[i] and new_record[i]:
            old_record[i] = new_record[i]
            filled_fields_flag = 1
        elif old_record[i] and new_record[i] and old_record[i] != new_record[i]:
            print(f'\nВ имеющейся в базе записи {old_record}\n'
                  f'и новой записи {new_record}\n'
                  f'имеется неоднозначность значений: {old_record[i]} и {new_record[i]}')
            old_record[i] = make_choice([old_record[i], new_record[i]])[0]
            filled_fields_flag = 1

    return filled_fields_flag


def remove_duplicates(record_for_check, clean_records_list):

    removed_duplicate_flag = 0

    for clean_record in clean_records_list:
        if record_for_check[0:2] == clean_record[0:2]:
            if fill_empty_fields(record_for_check, clean_record):
                removed_duplicate_flag = 1

    return removed_duplicate_flag


if __name__ == '__main__':

    contact_list_raw_data = get_contact_list_from_csv_file()
    new_contact_list = [contact_list_raw_data[0]]

    print(f'\nИз файла для обработки получено {len(contact_list_raw_data) - 1} записей')

    for row in contact_list_raw_data:
        if row[0] != 'lastname':
            correct_row = make_correct_record(row)
            if not remove_duplicates(correct_row, new_contact_list[1:]):
                new_contact_list.append(correct_row)

    save_new_contact_list_to_csv_file(new_contact_list)

    print(f'\nВ файл записано {len(new_contact_list) - 1} обработанных уникальных записей')








