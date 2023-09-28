from telebot import types


class NamesReplyMenuButtons:
    MENU_BUTTON = 'Меню'
    HELP_BUTTON = 'Помощь'


class NamesSettingsButtons:
    ADD_EMPLOYEE_BUTTON = ''
    DELETE_EMPLOYEE_BUTTON = ''
    BUTTON_FOR_EDITING_EMPLOYEE_INFORMATION = ''
    EMPLOYEE_SEARCH_BUTTON = ''


def reply_button_after_the_start_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_help = types.KeyboardButton(NamesReplyMenuButtons.HELP_BUTTON)
    button_menu = types.KeyboardButton(NamesReplyMenuButtons.MENU_BUTTON)
    markup.row(button_menu, button_help)
    return markup


def creating_yes_and_no_buttons(callback_yes_button: str, callback_no_button: str):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_yes = types.InlineKeyboardButton('Да', callback_data=callback_yes_button)
    button_no = types.InlineKeyboardButton('Нет', callback_data=callback_no_button)

    keyboard.add(button_yes, button_no)
    return keyboard


def index_re_entry_menu(callback_re_entry, callback_exit):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_re_entry = types.InlineKeyboardButton('Повторить ввод', callback_data=callback_re_entry)
    button_exit = types.InlineKeyboardButton('Выйти в главное меню', callback_data=callback_exit)

    keyboard.add(button_re_entry, button_exit)
    return keyboard


def employee_index_entry_buttons(callback_input_button, callback_exit_button):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_input = types.InlineKeyboardButton('Ввести индекс', callback_data=callback_input_button)
    button_exit = types.InlineKeyboardButton('Выйти в главное меню', callback_data=callback_exit_button)

    keyboard.add(button_input, button_exit)
    return keyboard


def search_continuation_menu(callback_yes_button, callback_no_button, callback_exit_button):
    '''Меню для продолжения поиска'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_yes = types.InlineKeyboardButton('Да, продолжить поиск', callback_data=callback_yes_button)
    button_no = types.InlineKeyboardButton('Нет, я нашел что искал', callback_data=callback_no_button)
    button_exit = types.InlineKeyboardButton('Заверишть поиск', callback_data=callback_exit_button)

    keyboard.add(button_yes, button_no, button_exit)
    return keyboard


def creating_main_menu_buttons(callback_search_initial,
                               callback_add_employee,
                               callback_delete_employee,
                               callback_edit_employee):
    '''
    Функция для создания кнопок главного меню

    :param callback_search_initial:
    :param callback_add_employee:
    :param callback_delete_employee:
    :param callback_edit_employee:
    :return:
    '''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_search_employee = types.InlineKeyboardButton('Найти сотрудника',
                                                        callback_data=callback_search_initial)
    button_add_employee = types.InlineKeyboardButton('Добавить сотрудника',
                                                     callback_data=callback_add_employee)
    button_delete_employee = types.InlineKeyboardButton('Удалить сотрудника',
                                                        callback_data=callback_delete_employee)
    button_edit_employee = types.InlineKeyboardButton('Редактировать информацию о сотруднике',
                                                      callback_data=callback_edit_employee)

    keyboard.add(button_add_employee, button_delete_employee, button_search_employee, button_edit_employee)
    return keyboard


def interaction_menu_employee_card(callback_card_editing, callback_card_deleting, callback_exit_button):
    '''Создание меню для взаимодействия с информацией о сотруднике'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_yes = types.InlineKeyboardButton('Отредактировать информацию о сотруднике',
                                            callback_data=callback_card_editing)
    button_no = types.InlineKeyboardButton('Удалить информацию о сотруднике', callback_data=callback_card_deleting)
    button_exit = types.InlineKeyboardButton('Вернуться к главному меню', callback_data=callback_exit_button)

    keyboard.add(button_yes, button_no, button_exit)
    return keyboard


def employee_information_editing_menu(callback_edit_first_name,
                                      callback_edit_last_name,
                                      callback_edit_patronymic,
                                      callback_edit_position,
                                      callback_edit_project,
                                      callback_edit_img,
                                      callback_exit_button):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_edit_first_name = types.InlineKeyboardButton('Изменить имя', callback_data=callback_edit_first_name)
    button_edit_last_name = types.InlineKeyboardButton('Изменить фамилию', callback_data=callback_edit_last_name)
    button_edit_patronymic = types.InlineKeyboardButton('Изменить отчество', callback_data=callback_edit_patronymic)
    button_edit_position = types.InlineKeyboardButton('Изменить должность', callback_data=callback_edit_position)
    button_edit_project = types.InlineKeyboardButton('Изменить проект', callback_data=callback_edit_project)
    button_edit_img = types.InlineKeyboardButton('Изменить фотограцию', callback_data=callback_edit_img)
    button_exit = types.InlineKeyboardButton('Выйти в главное меню', callback_data=callback_exit_button)

    keyboard.add(button_edit_first_name, button_edit_last_name, button_edit_patronymic,
                 button_edit_position, button_edit_project, button_edit_img, button_exit)
    return keyboard


def index_entry_or_employee_search_menu(callback_enter_index, callback_search_initial, callback_exit_button):
    '''Создание меню для ввода индекса или поиска сотрудника'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_enter_index = types.InlineKeyboardButton('Ввести индекс сотрудника',
                                                    callback_data=callback_enter_index)
    button_search_employee = types.InlineKeyboardButton('Найти сотрудника', callback_data=callback_search_initial)
    button_exit = types.InlineKeyboardButton('Вернуться к главному меню', callback_data=callback_exit_button)

    keyboard.add(button_enter_index, button_search_employee, button_exit)
    return keyboard


def command_confirmation_menu(callback_confirmation, callback_exit_menu):
    '''Меню подтверждения команды'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_confirmation = types.InlineKeyboardButton('Подтверждаю',
                                                     callback_data=callback_confirmation)
    button_exit = types.InlineKeyboardButton('Отменить и выйти в главное меню', callback_data=callback_exit_menu)

    keyboard.add(button_confirmation, button_exit)
    return keyboard


def extended_confirmation_command_menu(callback_confirmation, callback_re_entry, callback_exit_menu):
    '''Расширенное Меню подтверждения команды'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_confirmation = types.InlineKeyboardButton('Подтверждаю',
                                                     callback_data=callback_confirmation)
    button_edit_input = types.InlineKeyboardButton('Отредактировать ввод',
                                                   callback_data=callback_re_entry)
    button_exit = types.InlineKeyboardButton('Отменить и выйти в главное меню', callback_data=callback_exit_menu)

    keyboard.add(button_confirmation, button_edit_input, button_exit)
    return keyboard


def search_menu(callback_full_name, callback_project, callback_position, callback_time_period, callback_exit_menu):
    '''Расширенное Меню поиска сотрудников'''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_full_name = types.InlineKeyboardButton('ФИО', callback_data=callback_full_name)
    button_project = types.InlineKeyboardButton('Проект', callback_data=callback_project)
    button_position = types.InlineKeyboardButton('Должность', callback_data=callback_position)
    button_time_period = types.InlineKeyboardButton('Период прихода сотрудника', callback_data=callback_time_period)

    button_exit = types.InlineKeyboardButton('Отменить и выйти в главное меню', callback_data=callback_exit_menu)

    keyboard.add(button_full_name, button_project, button_time_period, button_position, button_exit)
    return keyboard
