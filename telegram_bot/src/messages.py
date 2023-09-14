from interface import employee_index_entry_buttons
from utils import EmployeeInformationFields
import base64


def output_employee_information(bot, chat_id, employee_info):
    """Вывод информации о сотруднике ввиде текстового сообщения"""
    for cur_employee in employee_info:
        item = cur_employee.get('image', None)
        if item is not None and item != '':
            bot.send_photo(chat_id, base64.b64decode(cur_employee['image']))

        bot.send_message(chat_id, ' ----==== Карточка сотрудника ====----\n'
                         f'\t Идентификатор работника:    {cur_employee["id"]}\n'
                         f'\t Имя: {cur_employee["first_name"]}\n'
                         f'\t Фамилия: {cur_employee["last_name"]}\n'
                         f'\t Отчество: {cur_employee["patronymic"]}\n'
                         f'\t Должность: {cur_employee["post_name"]}\n'
                         f'\t Проект: {cur_employee["project_name"]}')


def output_addition_employee_information(bot, chat_id, cur_employee):
    item = cur_employee.get(EmployeeInformationFields.IMAGE_BUFFER, None)
    if item is not None and item != '':
        bot.send_photo(chat_id, base64.b64decode(cur_employee[EmployeeInformationFields.IMAGE_BUFFER]))

    bot.send_message(chat_id, ' ----==== Карточка сотрудника ====----\n'
                     f'\t Имя:\t{cur_employee[EmployeeInformationFields.FIRST_NAME]}\n'
                     f'\t Фамилия:\t{cur_employee[EmployeeInformationFields.LAST_NAME]}\n'
                     f'\t Отчество:\t{cur_employee.get(EmployeeInformationFields.PATRONYMIC, "Не указано")}\n'
                     f'\t Должность:\t{cur_employee[EmployeeInformationFields.POSITION]}\n'
                     f'\t Проект:\t{cur_employee[EmployeeInformationFields.PROJECT]}')
