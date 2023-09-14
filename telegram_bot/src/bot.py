import os
import telebot
from interface import (
    extended_confirmation_command_menu,
    index_entry_or_employee_search_menu,
    creating_main_menu_buttons,
    index_re_entry_menu,
    interaction_menu_employee_card,
    creating_yes_and_no_buttons,
    command_confirmation_menu,
    employee_information_editing_menu,
    employee_index_entry_buttons,
    search_continuation_menu)
from messages import (
    output_employee_information,
    output_addition_employee_information
)
import base64
import functools
from utils import (
    get_full_name,
    EmployeeInformationFields,
    convert_employee_id_to_information,
    send_request,
    UserStates)
import logging
import forms
from forms import get_fields_current_state
import requests
import json
from api import RequestAddresses

SERVER_URI = os.getenv('SERVER_URI') #, 'http://127.0.0.1:8001')
TBOT_TOKEN = os.getenv('TELEGRAM_TOKEN')#,
bot = telebot.TeleBot(TBOT_TOKEN)
local_path = None

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
logger.info(f'Bot token: {TBOT_TOKEN}')
logger.info(f'Server uri: {SERVER_URI}')


def init_user(user_id):
    send_request(requests.post, {"user_id": user_id}, SERVER_URI + RequestAddresses.ADD_USER_INFORMATION)


def update_user_information(info):
    send_request(requests.post, info, SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)


def send_main_menu(message, message_text='Чем я могу вам помочь?'):
    keyboard = creating_main_menu_buttons('main_menu.search_initial',
                                          'main_menu.add_employee',
                                          'main_menu.delete_employee',
                                          'main_menu.edit_employee')

    bot.send_message(message.chat.id, message_text, reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    init_user(message.chat.id)
    bot.send_message(message.chat.id, 'Добрый день!')
    send_main_menu(message, 'Чем я могу вам помочь?')


def suggestions_entering_employee_index(bot, message):
    markup = employee_index_entry_buttons('search_employees.enter_index',
                                          'exit_the_main_menu')
    bot.send_message(message.chat.id,
                     "Если вы нашли то, что искали вы можете продолжить взаимодействие с карточкой сотрудника. "
                     "Для этого введите индекс карточки выбранного сотрудника", reply_markup=markup)


def employee_index_input_handler(message, markup_in_case_success, message_text_in_case_succes):
    '''Функция-обработчик для проверки корректности введенного id сотрудника'''
    if message.text is not None and message.text.isdigit() and len(message.text) < 15:

        response = send_request(requests.post, {'id': int(message.text)},
                                SERVER_URI + RequestAddresses.SEARCH_EMPLOYEE_BY_ID)
        if response is None:
            # Пишем пользователю о некорректном вводе id и проСим повторить ввод
            markup = employee_index_entry_buttons('search_employees.enter_index',
                                                  'exit_the_main_menu')
            bot.send_message(message.chat.id, "Сотрудник с таким id не найден. Попробуйте ввести другой id ",
                             reply_markup=markup)
        else:
            # Запоминаем ввод пользователя
            update_user_information({'user_id': message.chat.id, 'last_message': message.text,
                                     'image_buffer': response['image']})

            #  Печатаем информацию о найденном сотруднике
            bot.send_message(message.chat.id, 'Выбранный сотрудник: ')
            output_employee_information(bot, message.chat.id, [response])

            # В случае введения правильного индекса печатаем необходимое меню
            bot.send_message(message.chat.id, message_text_in_case_succes, reply_markup=markup_in_case_success)

    else:
        markup = index_re_entry_menu('search_employees.index_re_entry', 'exit_the_main_menu')
        bot.send_message(message.chat.id, "Индекс должен быть целым числом. Хотите повторить ввод?",
                         reply_markup=markup)


def handler_employee_information_input_event(message):
    '''Обработчки ввода текстовой информации о сотруднике'''

    response = send_request(requests.post, {'user_id': message.chat.id},
                            SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)
    try:
        struct_user_input = json.loads(response['last_message'])
    except Exception as e:
        struct_user_input = {}

    ind_request = response['ind']
    # Запрашиваем поля ввода для текущего состояния пользователя
    fields = get_fields_current_state(response['cur_state'])

    if fields[ind_request]['type_field'] == 'text' and \
            message.text is not None and message.text.replace(" ", "").isalpha() and \
            len(message.text) < fields[ind_request]['max_len']:

        struct_user_input[fields[ind_request]['field_name']] = message.text

        # Запоминаем ввод пользователя
        update_user_information(
            {'user_id': message.chat.id, 'last_message': json.dumps(struct_user_input, ensure_ascii=False)})

        # Если пользователь ввел все поля, выходим из итерации запроса
        if response['ind'] + 1 == response['end_ind']:
            fields.callback_end_input()
        else:
            bot.send_message(message.chat.id, f'Введите {fields[ind_request + 1]["text"]} сотрудника:')
            # Обновляем информацию о пользователе
            send_request(requests.post, {'user_id': message.chat.id, 'ind': response['ind'] + 1},
                         SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)
            bot.register_next_step_handler(message, handler_employee_information_input_event)

    elif fields[ind_request]['type_field'] == 'img':
        handler_adding_an_image(message)

    else:
        markup = index_re_entry_menu('main_menu.add_employee.input_information.re_entry', 'exit_the_main_menu')
        bot.send_message(message.chat.id, "Данное поле должно содержать только буквы. Хотите повторить ввод?",
                         reply_markup=markup)


def handler_adding_an_image(message):
    '''Обработчик добавления фото сотрудника'''

    if message.photo is not None:
        response = send_request(requests.post, {'user_id': message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)
        ind_request = response['ind']
        fields = get_fields_current_state(response['cur_state'])

        # Запоминаем ввод пользователя
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        im_b64 = base64.b64encode(downloaded_file).decode("utf8")

        update_user_information({'user_id': message.chat.id, 'image_buffer': im_b64})

        # Обновляем информацию о пользователе
        send_request(requests.post, {'user_id': message.chat.id, 'ind': response['ind'] + 1},
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        # Если пользователь ввел все поля, выходим из итерации запроса
        if response['ind'] + 1 == response['end_ind']:
            fields.callback_end_input()
        else:
            bot.send_message(message.chat.id, f'Загрузите {fields[ind_request + 1]["text"]} сотрудника:')
            # Обновляем информацию о пользователе
            send_request(requests.post, {'user_id': message.chat.id, 'ind': response['ind'] + 1},
                         SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)
            bot.register_next_step_handler(message, handler_employee_information_input_event)

    else:
        markup = index_re_entry_menu('main_menu.add_employee.input_information.re_entry', 'exit_the_main_menu')
        bot.send_message(message.chat.id, "Загрузите фотографию сотрудника",
                         reply_markup=markup)


def completion_mandatory_input_fields(message):
    '''Функция используется для вывода необходимой информации после ввода обязательных полей при добавлении сотрудника'''
    # В случае введения правильного индекса печатаем необходимое меню
    markup = creating_yes_and_no_buttons('main_menu.add_employee.additional_info.yes',
                                         'main_menu.add_employee.additional_info.no')
    bot.send_message(message.chat.id, "Хотите ввести дополнительную информацию о пользователе?",
                     reply_markup=markup)


def completion_additional_input_fields(message):
    '''Функция используется для вывода необходимой информации после ввода дополнительных полей при добавлении сотрудника'''
    response = send_request(requests.post, {'user_id': message.chat.id},
                            SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)
    info = response[EmployeeInformationFields.IMAGE_BUFFER]

    response = json.loads(response["last_message"])
    response[EmployeeInformationFields.IMAGE_BUFFER] = info

    output_addition_employee_information(bot, message.chat.id, response)

    markup = extended_confirmation_command_menu(
        'main_menu.add_employee.additional_info.confirmation',
        'main_menu.add_employee.additional_info.edit_info',
        'exit_the_main_menu')
    bot.send_message(message.chat.id, "Подтвердите корректность введенной информации", reply_markup=markup)


def search_employees_query(chat_id, first_name, last_name, patronymic):
    '''Функция поиска сотрудников по переданным данным ФИО'''
    user_info = send_request(requests.post,
                             {"user_id": chat_id}, SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

    response = send_request(requests.post,
                            {"first_name": first_name,
                             "last_name": last_name,
                             'patronymic': patronymic,
                             "offset": user_info['offset']}, SERVER_URI + RequestAddresses.SEARCH_EMPLOYEE)

    send_request(requests.post,
                 {"user_id": chat_id, "offset": user_info['offset'] + user_info['limit']},
                 SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

    return response['content']


def search_employees(message, message_text, offset=0):
    '''Функция поиска сотрудника, позволяющая зациклить ввывод информации'''
    chat_id = message.chat.id
    first_name, last_name, patronymic = get_full_name(message_text)
    response = search_employees_query(chat_id, first_name, last_name, patronymic)

    if len(response) == 0:
        if offset == 0:
            bot.send_message(chat_id, 'Совпадений не найдено :(')
            send_main_menu(message, 'Чем я могу вам помочь?')

        else:
            bot.send_message(chat_id, "Больше совпадений не найдено :(")
            # Выводим меню для выбора ввода индекса или выхода
            suggestions_entering_employee_index(bot, message)

        return

    #  Печатаем информацию о найденных сотрудниках
    output_employee_information(bot, chat_id, response)

    # Предлагаем продолжить поиск
    markup = search_continuation_menu('search_employees.search_yes',
                                      'search_employees.search_no',
                                      "exit_the_main_menu")
    bot.send_message(chat_id, 'Продолжить поиск сотрудников?', reply_markup=markup)


def init_employee_search(message):
    '''
    Функция для отправки запроса поиска сотрудника
    '''
    send_request(requests.post, {'user_id': message.chat.id,
                                 'last_message': message.text,
                                 "offset": 0
                                 }, SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

    search_employees(message, message.text)


@bot.callback_query_handler(func=lambda call: True)
def handle_inline_button_click(call):
    '''
    Основная функция обработки нажатия на кнопки
    '''
    chat_id = call.message.chat.id

    if call.data == 'main_menu.search_initial' or \
            call.data == 'main_menu.delete_employee.search_initial' or \
            call.data == 'main_menu.edit_employee.search_initial':
        # Кнопка "Поиск сотрудников"
        bot.send_message(chat_id, 'Введите ФИО сотрудника')
        bot.register_next_step_handler(call.message, init_employee_search)

    elif call.data == 'search_employees.edit_employee.first_name' or \
            call.data == 'main_menu.edit_employee.enter_index.edit_employee.first_name':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_EMPLOYEE_FIRST_NAME,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_FIRST_NAME_REQUEST_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_FIRST_NAME_REQUEST_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                                    message=call.message)

        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            convert_employee_id_to_information(call.message, SERVER_URI)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_FIRST_NAME_REQUEST_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'search_employees.edit_employee.last_name' or \
            call.data == 'main_menu.edit_employee.enter_index.edit_employee.last_name':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_EMPLOYEE_LAST_NAME,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_LAST_NAME_REQUEST_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_LAST_NAME_REQUEST_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                                   message=call.message)

        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            convert_employee_id_to_information(call.message, SERVER_URI)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_LAST_NAME_REQUEST_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'search_employees.edit_employee.patronymic' or \
            call.data == 'main_menu.edit_employee.enter_index.edit_employee.patronymic':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_EMPLOYEE_PATRONYMIC,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_PATRONYMIC_REQUEST_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_PATRONYMIC_REQUEST_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                                    message=call.message)

        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            convert_employee_id_to_information(call.message, SERVER_URI)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_PATRONYMIC_REQUEST_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'search_employees.edit_employee.position' or \
            call.data == 'main_menu.edit_employee.enter_index.edit_employee.position':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_EMPLOYEE_POST,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_POSITION_REQUEST_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_POSITION_REQUEST_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                                  message=call.message)

        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            convert_employee_id_to_information(call.message, SERVER_URI)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_POSITION_REQUEST_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'search_employees.edit_employee.project' or \
            call.data == 'main_menu.edit_employee.enter_index.edit_employee.project':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_EMPLOYEE_PROJECT,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_PROJECT_REQUEST_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_PROJECT_REQUEST_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                                 message=call.message)
        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            convert_employee_id_to_information(call.message, SERVER_URI)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_PROJECT_REQUEST_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'search_employees.edit_employee.img' or \
            call.data == 'main_menu.edit_employee.enter_index.edit_employee.img':  # << ----------------- Доделать фотки
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_EMPLOYEE_IMG,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_IMG_REQUEST_FORM),
                                     'image_buffer': None
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)
        forms.FIELDS_IMG_REQUEST_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                             message=call.message)
        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            convert_employee_id_to_information(call.message, SERVER_URI)

        bot.send_message(call.message.chat.id, f'Загрузите {forms.FIELDS_IMG_REQUEST_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'search_employees.search_yes':
        # Продолжаем поиск
        user_info = send_request(requests.post,
                                 {'user_id': call.message.chat.id},
                                 SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)
        # Если пользователь не был инициализирован ранее
        if user_info is None:
            init_user(chat_id)
            user_info = send_request(requests.post, {'user_id': call.message.chat.id},
                                     SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        search_employees(call.message, user_info['last_message'], user_info['offset'])

    elif call.data == 'search_employees.search_no':
        # Выводим меню для выбора ввода индекса или выхода
        suggestions_entering_employee_index(bot, call.message)

    elif call.data == 'exit_the_main_menu':
        # Завершаем поиск, печатаем главное меню
        send_main_menu(call.message, 'Чем я могу вам помочь?')

    elif call.data == "search_employees.index_re_entry" or \
            call.data == 'search_employees.enter_index':

        bot.send_message(call.message.chat.id, 'Введите индекс сотрудника в виде целого числа: ')
        markup = interaction_menu_employee_card('search_employees.edit_employee',
                                                'search_employees.delete_employee',
                                                'exit_the_main_menu')
        message_text = "Выберите то, что хотите сделать с информацией о сотруднике:"
        fun_employee_index_input_handler = functools.partial(employee_index_input_handler,
                                                             markup_in_case_success=markup,
                                                             message_text_in_case_succes=message_text,
                                                             )
        bot.register_next_step_handler(call.message, fun_employee_index_input_handler)

    elif call.data == 'main_menu.delete_employee.enter_index':

        bot.send_message(call.message.chat.id, 'Введите индекс сотрудника в виде целого числа: ')
        markup = command_confirmation_menu('main_menu.delete_employee.enter_index.confirmation',
                                           'exit_the_main_menu')

        message_text = "Подтвердите данную команду:"
        fun_employee_index_input_handler = functools.partial(employee_index_input_handler,
                                                             markup_in_case_success=markup,
                                                             message_text_in_case_succes=message_text)
        bot.register_next_step_handler(call.message, fun_employee_index_input_handler)

    elif call.data == 'main_menu.edit_employee.enter_index':
        bot.send_message(call.message.chat.id, 'Введите индекс сотрудника в виде целого числа: ')
        markup = employee_information_editing_menu('main_menu.edit_employee.enter_index.edit_employee.first_name',
                                                   'main_menu.edit_employee.enter_index.edit_employee.last_name',
                                                   'main_menu.edit_employee.enter_index.edit_employee.patronymic',
                                                   'main_menu.edit_employee.enter_index.edit_employee.position',
                                                   'main_menu.edit_employee.enter_index.edit_employee.project',
                                                   'main_menu.edit_employee.enter_index.edit_employee.img',
                                                   'exit_the_main_menu')

        message_text = "Выберите пункт для редактирования:"
        fun_employee_index_input_handler = functools.partial(employee_index_input_handler,
                                                             markup_in_case_success=markup,
                                                             message_text_in_case_succes=message_text)
        bot.register_next_step_handler(call.message, fun_employee_index_input_handler)

    elif call.data == 'search_employees.edit_employee' or \
            call.data == 'main_menu.add_employee.additional_info.edit_info':

        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        response = json.loads(response["last_message"])
        if isinstance(response, int):
            # Преобразуем индекс сотрудника, хранимый в буфере пользователя, в информацию о выбранном сотруднике
            convert_employee_id_to_information(call.message, SERVER_URI)

        markup = employee_information_editing_menu('search_employees.edit_employee.first_name',
                                                   'search_employees.edit_employee.last_name',
                                                   'search_employees.edit_employee.patronymic',
                                                   'search_employees.edit_employee.position',
                                                   'search_employees.edit_employee.project',
                                                   'search_employees.edit_employee.img',
                                                   'exit_the_main_menu')
        bot.send_message(call.message.chat.id, "Выберите пункт для редактирования:", reply_markup=markup)

    elif call.data == 'search_employees.delete_employee' or \
            call.data == "main_menu.delete_employee.enter_index.confirmation":
        # Удаляем информацию о сотруднике
        # Отправить запрос в БД
        bot.send_message(call.message.chat.id, "Так так так, сейчас мы его удалим...")
        user_info = send_request(requests.post, {'user_id': call.message.chat.id},
                                 SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)

        id_employee = int(user_info['last_message'])
        send_request(requests.post, {'id': id_employee}, SERVER_URI + RequestAddresses.DELETE_EMPLOYEE_BY_ID)
        send_main_menu(call.message)

    elif call.data == 'main_menu.delete_employee':
        # Просим ввести индекс сотрудника или предлагаем осуществить поиск
        markup = index_entry_or_employee_search_menu('main_menu.delete_employee.enter_index',
                                                     'main_menu.delete_employee.search_initial',
                                                     'exit_the_main_menu')
        bot.send_message(call.message.chat.id, "Введите индекс сотрудника или осуществите поиск",
                         reply_markup=markup)

    elif call.data == 'main_menu.edit_employee':
        # Просим ввести индекс сотрудника или предлагаем осуществить поиск
        markup = index_entry_or_employee_search_menu('main_menu.edit_employee.enter_index',
                                                     'main_menu.edit_employee.search_initial',
                                                     'exit_the_main_menu')
        bot.send_message(call.message.chat.id, "Введите индекс сотрудника или осуществите поиск",
                         reply_markup=markup)

    elif call.data == 'main_menu.add_employee':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id, "last_message": '',
                                     'cur_state': UserStates.ENTERING_MAIN_FORM_ADDING_EMPLOYEE,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_MAIN_EMPLOYEE_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_MAIN_EMPLOYEE_FORM.callback_end_input = functools.partial(completion_mandatory_input_fields,
                                                                               message=call.message)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_MAIN_EMPLOYEE_FORM[0]["text"]} сотрудника:')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'main_menu.add_employee.input_information.re_entry':
        bot.send_message(call.message.chat.id, 'Некорректный ввод. Повторите попытку')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    elif call.data == 'main_menu.add_employee.additional_info.no':
        completion_additional_input_fields(call.message)

    elif call.data == 'main_menu.add_employee.additional_info.confirmation':
        # Добавляем информацию в базу
        response = send_request(requests.post, {'user_id': call.message.chat.id},
                                SERVER_URI + RequestAddresses.SEARCH_USER_INFORMATION)
        user_info = response

        response = json.loads(response["last_message"])
        if 'id' in response:
            url = SERVER_URI + RequestAddresses.UPDATE_EMPLOYEE
            message_text = 'Информацию успешно изменена'
        else:
            url = SERVER_URI + RequestAddresses.ADD_EMPLOYEE
            message_text = "Сотрудник успешно добавлен!"

        send_request(requests.post, {'id': response.get('id', 0),
                                     'first_name': response[EmployeeInformationFields.FIRST_NAME],
                                     'last_name': response[EmployeeInformationFields.LAST_NAME],
                                     'patronymic': response.get(EmployeeInformationFields.PATRONYMIC, ''),
                                     'post_name': response[EmployeeInformationFields.POSITION],
                                     'project_name': response[EmployeeInformationFields.PROJECT],
                                     'image': user_info.get(EmployeeInformationFields.IMAGE_BUFFER, None)
                                     }, url)

        bot.send_message(call.message.chat.id, message_text)

        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id, "last_message": '', 'image_buffer': ''},
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        send_main_menu(call.message)

    elif call.data == 'main_menu.add_employee.additional_info.yes':
        # Очищаем информацию в базе о последнем сообщении
        send_request(requests.post, {"user_id": call.message.chat.id,
                                     'cur_state': UserStates.ENTERING_ADDITIONAL_FORM_ADDING_EMPLOYEE,
                                     'ind': 0, 'end_ind': len(forms.FIELDS_ADDITIONAL_EMPLOYEE_FORM)
                                     },
                     SERVER_URI + RequestAddresses.UPDATE_USER_INFORMATION)

        forms.FIELDS_ADDITIONAL_EMPLOYEE_FORM.callback_end_input = functools.partial(completion_additional_input_fields,
                                                                                     message=call.message)

        bot.send_message(call.message.chat.id, f'Введите {forms.FIELDS_ADDITIONAL_EMPLOYEE_FORM[0]["text"]} сотрудника')
        bot.register_next_step_handler(call.message, handler_employee_information_input_event)

    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=None)


if __name__ == '__main__':
    import time

    logger.info('Telegram bot starting...')
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            logger.warning(e)
            time.sleep(1)

    logger.info("Break infinity polling")
