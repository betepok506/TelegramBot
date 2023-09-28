import json
from api import RequestAddresses
import requests


class EmployeeInformationFields:
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    PATRONYMIC = 'patronymic'
    POSITION = 'position'
    PROJECT = 'project'
    IMAGE_BUFFER = 'image_buffer'
    TIME_ADDITION = 'time_addition'


class CyclicInputRequestFields():
    def __init__(self):
        self.fields = []
        self.callback_end_input = None

    def add_field(self, item):
        if not isinstance(item, dict):
            raise "The passed argument must be a dictionary!"

        self.fields.append(item)

    def __iter__(self):
        return iter(self.fields)

    def __getitem__(self, ind):
        return self.fields[ind]

    def __len__(self):
        return len(self.fields)


class UserStates:
    """Состояния пользователя"""
    ENTERING_MAIN_FORM_ADDING_EMPLOYEE = 1
    ENTERING_ADDITIONAL_FORM_ADDING_EMPLOYEE = 2
    ENTERING_EMPLOYEE_FIRST_NAME = 3
    ENTERING_EMPLOYEE_LAST_NAME = 4
    ENTERING_EMPLOYEE_PATRONYMIC = 5
    ENTERING_EMPLOYEE_POST = 6
    ENTERING_EMPLOYEE_PROJECT = 7
    ENTERING_EMPLOYEE_IMG = 8


def send_request(func_requests, payload, url, message=None, error_callback=None, successful_callback=None):
    payload = json.dumps(payload)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = func_requests(url,
                             data=payload,
                             headers=headers)
    try:
        data = response.json()
        return data
    except:
        pass


def convert_employee_id_to_information(message, server_url):
    '''Функция для преобразования буфера, в котором хранится индекс выбранного сотрудника в информацию о нем'''
    user_info = send_request(requests.post, {'user_id': message.chat.id},
                             server_url + RequestAddresses.SEARCH_USER_INFORMATION)

    id_employee = int(user_info['last_message'])

    response = send_request(requests.post, {'id': id_employee}, server_url + RequestAddresses.SEARCH_EMPLOYEE_BY_ID)
    struct_user_input = {'id': id_employee,
                         EmployeeInformationFields.FIRST_NAME: response['first_name'],
                         EmployeeInformationFields.LAST_NAME: response['last_name'],
                         EmployeeInformationFields.PATRONYMIC: response['patronymic'],
                         EmployeeInformationFields.POSITION: response['post_name'],
                         EmployeeInformationFields.PROJECT: response['project_name']}

    send_request(requests.post, {'user_id': message.chat.id,
                                 'last_message': json.dumps(struct_user_input, ensure_ascii=False)},
                 server_url + RequestAddresses.UPDATE_USER_INFORMATION)


def get_full_name(text_message):
    '''Функция для получения имени и фамилии из строки'''
    split_text = text_message.split()
    first_name = split_text[0]

    if len(split_text) >= 2:
        last_name = ' '.join(split_text[1:])
        if len(split_text) >= 3:
            patronymic = ' '.join(split_text[2:])
        else:
            patronymic = ''
    else:
        last_name = ''
        patronymic = ''

    return first_name, last_name, patronymic
