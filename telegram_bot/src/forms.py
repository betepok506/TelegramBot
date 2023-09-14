from utils import \
    CyclicInputRequestFields, \
    EmployeeInformationFields, UserStates

# Формы для последовательного запроса у пользователя
# Основная форма запроса Имени, Фамилии, должности, проекта
FIELDS_MAIN_EMPLOYEE_FORM = CyclicInputRequestFields()
FIELDS_MAIN_EMPLOYEE_FORM.add_field({'text': 'имя', 'field_name': EmployeeInformationFields.FIRST_NAME,
                                     'type_field': 'text', 'max_len': 60})
FIELDS_MAIN_EMPLOYEE_FORM.add_field({'text': 'фамилию', 'field_name': EmployeeInformationFields.LAST_NAME,
                                     'type_field': 'text', 'max_len': 60})
FIELDS_MAIN_EMPLOYEE_FORM.add_field({'text': 'Должность', 'field_name': EmployeeInformationFields.POSITION,
                                     'type_field': 'text', 'max_len': 60})
FIELDS_MAIN_EMPLOYEE_FORM.add_field({'text': 'Проект', 'field_name': EmployeeInformationFields.PROJECT,
                                     'type_field': 'text', 'max_len': 60})

# Форма запроса дополнительной информации
FIELDS_ADDITIONAL_EMPLOYEE_FORM = CyclicInputRequestFields()
FIELDS_ADDITIONAL_EMPLOYEE_FORM.add_field({'text': 'отчество', 'field_name': EmployeeInformationFields.PATRONYMIC,
                                           'type_field': 'text', 'max_len': 60})
FIELDS_ADDITIONAL_EMPLOYEE_FORM.add_field({'text': 'фото', 'field_name': EmployeeInformationFields.IMAGE_BUFFER,
                                           'type_field': 'img', 'max_len': 1e18})

# Форма для запроса имени
FIELDS_FIRST_NAME_REQUEST_FORM = CyclicInputRequestFields()
FIELDS_FIRST_NAME_REQUEST_FORM.add_field({'text': 'имя', 'field_name': EmployeeInformationFields.FIRST_NAME,
                                          'type_field': 'text', 'max_len': 60})

# Форма для запроса фамилии
FIELDS_LAST_NAME_REQUEST_FORM = CyclicInputRequestFields()
FIELDS_LAST_NAME_REQUEST_FORM.add_field({'text': 'фамилия', 'field_name': EmployeeInformationFields.LAST_NAME,
                                         'type_field': 'text', 'max_len': 60})

# Форма для запроса отчества
FIELDS_PATRONYMIC_REQUEST_FORM = CyclicInputRequestFields()
FIELDS_PATRONYMIC_REQUEST_FORM.add_field({'text': 'отчество', 'field_name': EmployeeInformationFields.PATRONYMIC,
                                          'type_field': 'text', 'max_len': 60})

# Форма для запроса проекта
FIELDS_PROJECT_REQUEST_FORM = CyclicInputRequestFields()
FIELDS_PROJECT_REQUEST_FORM.add_field({'text': 'проект', 'field_name': EmployeeInformationFields.PROJECT,
                                       'type_field': 'text', 'max_len': 60})

# Форма для запроса должности
FIELDS_POSITION_REQUEST_FORM = CyclicInputRequestFields()
FIELDS_POSITION_REQUEST_FORM.add_field({'text': 'должность', 'field_name': EmployeeInformationFields.POSITION,
                                        'type_field': 'text', 'max_len': 60})

# Форма для запроса фото
FIELDS_IMG_REQUEST_FORM = CyclicInputRequestFields()
FIELDS_IMG_REQUEST_FORM.add_field({'text': 'фото', 'field_name': EmployeeInformationFields.IMAGE_BUFFER,
                                   'type_field': 'img', 'max_len': 1e18})


def get_fields_current_state(user_state):
    """По текущему состоянию пользователя возвращаем поля, которы необходимо у него запросить"""
    if user_state == UserStates.ENTERING_MAIN_FORM_ADDING_EMPLOYEE:
        return FIELDS_MAIN_EMPLOYEE_FORM
    elif user_state == UserStates.ENTERING_ADDITIONAL_FORM_ADDING_EMPLOYEE:
        return FIELDS_ADDITIONAL_EMPLOYEE_FORM
    elif user_state == UserStates.ENTERING_EMPLOYEE_FIRST_NAME:
        return FIELDS_FIRST_NAME_REQUEST_FORM
    elif user_state == UserStates.ENTERING_EMPLOYEE_LAST_NAME:
        return FIELDS_LAST_NAME_REQUEST_FORM
    elif user_state == UserStates.ENTERING_EMPLOYEE_PATRONYMIC:
        return FIELDS_PATRONYMIC_REQUEST_FORM
    elif user_state == UserStates.ENTERING_EMPLOYEE_POST:
        return FIELDS_POSITION_REQUEST_FORM
    elif user_state == UserStates.ENTERING_EMPLOYEE_PROJECT:
        return FIELDS_PROJECT_REQUEST_FORM
    elif user_state == UserStates.ENTERING_EMPLOYEE_IMG:
        return FIELDS_IMG_REQUEST_FORM
