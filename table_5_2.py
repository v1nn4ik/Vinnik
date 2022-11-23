import csv
import re

from prettytable import PrettyTable

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}
dic_currency_to_ru = {
    'AZN': 'Манаты',
    'BYR': 'Белорусские рубли',
    'EUR': 'Евро',
    'GEL': 'Грузинский лари',
    'KGS': 'Киргизский сом',
    'KZT': 'Тенге',
    'RUR': 'Рубли',
    'UAH': 'Гривны',
    'USD': 'Доллары',
    'UZS': 'Узбекский сум'
}
dic_experience = {
    'noExperience': 'Нет опыта',
    'between1And3': 'От 1 года до 3 лет',
    'between3And6': 'От 3 до 6 лет',
    'moreThan6': 'Более 6 лет',
}
dic_rus_names = {
    'Описание': 'description',
    'Навыки': 'skills_length',
    'Оклад': 'salary_average',
    'Дата публикации вакансии': 'published',
    'Опыт работы': 'experience_weight',
    'Премиум-вакансия': 'premium',
    'Идентификатор валюты оклада': 'salary_currency',
    'Название': 'name',
    'Название региона': 'area_name',
    'Компания': 'employer_name',
}


class Salary:
    def __init__(self, vacancy):
        self.salary_from = int(float(vacancy['salary_from']))
        self.salary_to = int(float(vacancy['salary_to']))
        self.salary_gross = 'Без вычета налогов' if vacancy['salary_gross'].lower() == 'true' else 'С вычетом налогов'
        self.salary_currency = vacancy['salary_currency']
        self.salary_average = currency_to_rub[self.salary_currency] * (self.salary_from + self.salary_to) / 2

    def __str__(self):
        return '{0:,} - {1:,} ({2}) ({3})'.format(self.salary_from, self.salary_to,
                                                  dic_currency_to_ru[self.salary_currency],
                                                  self.salary_gross).replace(',', ' ')


class Vacancy:
    order = ['index', 'name', 'description', 'key_skills', 'experience_id', 'premium', 'employer_name', 'salary',
             'area_name', 'published_at']
    dic_experience_weight_dictionary = {
        'Нет опыта': 1,
        'От 1 года до 3 лет': 2,
        'От 3 до 6 лет': 3,
        'Более 6 лет': 4
    }

    def __init__(self, vacancy):
        self.index = 0
        self.name = self.clear_html(vacancy['name'])
        self.description = self.shortener(self.clear_html(vacancy['description']))
        self.skills = vacancy['key_skills'].split('\n')
        self.key_skills = self.shortener(vacancy['key_skills'])
        self.skills_length = len(self.skills)
        self.experience_id = dic_experience[vacancy['experience_id']]
        self.premium = 'Да' if vacancy['premium'].lower() == 'true' else 'Нет'
        self.employer_name = vacancy['employer_name']
        self.salary_class = Salary(vacancy)
        self.salary = str(self.salary_class)
        self.area_name = vacancy['area_name']
        self.published = vacancy['published_at']
        self.published_at = '{0[2]}.{0[1]}.{0[0]}'.format(vacancy['published_at'][:10].split('-'))

    @staticmethod
    def clear_html(string):
        result = re.sub(r'<.*?>', '', string)
        result = re.sub(r'\s+', ' ', result)
        return result.strip()

    @staticmethod
    def shortener(string):
        return string if len(string) <= 100 else string[:100] + '...'

    @property
    def salary_to(self):
        return self.salary_class.salary_to

    @property
    def salary_average(self):
        return self.salary_class.salary_average

    @property
    def salary_currency(self):
        return self.salary_class.salary_currency

    @property
    def experience_weight(self):
        return self.dic_experience_weight_dictionary[self.experience_id]

    @property
    def salary_from(self):
        return self.salary_class.salary_from

    def get_list(self):
        return [getattr(self, key) for key in self.order]


class DataSet:
    def __init__(self, file_name, filter_param, sort_param, sort_reverse, sort_range):
        self.file_name = file_name
        self.filter_param = filter_param
        self.sort_param = sort_param
        self.sort_reverse = sort_reverse
        self.sort_range = sort_range
        self.vacancies_objects = []

    cond_to_sort = {
        'Навыки': lambda vacancy, value: all([skill in vacancy.skills for skill in value.split(', ')]),
        'Идентификатор валюты оклада': lambda vacancy, value: dic_currency_to_ru[vacancy.salary_currency] == value,
        'Название': lambda vacancy, value: vacancy.name == value,
        'Название региона': lambda vacancy, value: vacancy.area_name == value,
        'Оклад': lambda vacancy, value: vacancy.salary_from <= float(value) <= vacancy.salary_to,
        'Дата публикации вакансии': lambda vacancy, value: vacancy.published_at == value,
        'Опыт работы': lambda vacancy, value: vacancy.experience_id == value,
        'Премиум-вакансия': lambda vacancy, value: vacancy.premium == value,
        'Компания': lambda vacancy, value: vacancy.employer_name == value
    }

    def csv_reader(self):
        header = []
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for index, row in enumerate(reader):
                if index == 0:
                    header = row
                    csv_header_length = len(row)
                elif '' not in row and len(row) == csv_header_length:
                    self.vacancies_objects.append(Vacancy(dict(zip(header, row))))
        if len(self.vacancies_objects) == 0:
            if len(header) == 0:
                print('Пустой файл')
            else:
                print('Нет данных')
            exit()

    def get_rows(self):
        return [vacancy.get_list() for vacancy in self.vacancies_objects]

    def get_range(self):
        vacancies_temp = []
        length = len(self.sort_range)
        for index, vacancy in enumerate(self.vacancies_objects):
            if (length > 1 and self.sort_range[0] <= index < self.sort_range[1]) or (
                    length == 1 and self.sort_range[0] <= index) or length == 0:
                vacancy.index = index + 1
                vacancies_temp.append(vacancy)
        self.vacancies_objects = vacancies_temp

    def sort_rows(self):
        if self.sort_param != '':
            self.vacancies_objects.sort(key=lambda a: getattr(a, dic_rus_names[self.sort_param]),
                                        reverse=self.sort_reverse)
        elif self.sort_param == '' and self.sort_reverse:
            self.vacancies_objects.reverse()

    def filter_rows(self):
        if len(self.filter_param) == 0:
            return
        self.vacancies_objects = list(
            filter(lambda vacancy: self.cond_to_sort[self.filter_param[0]](vacancy, self.filter_param[1]),
                   self.vacancies_objects))


class InputConnect:
    def __init__(self):
        self.errors = []
        self.file_name = input('Введите название файла: ')
        self.filter_param = self.parse_filter_param(input('Введите параметр фильтрации: '))
        self.sort_param = self.parse_sort_param(input('Введите параметр сортировки: '))
        self.sort_reverse = self.parse_sort_reverse(input('Обратный порядок сортировки (Да / Нет): '))
        self.sort_range = self.parse_sort_range(input('Введите диапазон вывода: '))
        self.table_fields = self.parse_table_fields(input('Введите требуемые столбцы: '))
        if len(self.errors) != 0:
            print(self.errors[0])
            exit()
        data_set = DataSet(self.file_name, self.filter_param, self.sort_param, self.sort_reverse, self.sort_range)
        data_set.csv_reader()
        data_set.filter_rows()
        data_set.sort_rows()
        data_set.get_range()
        rows = data_set.get_rows()
        if len(rows) == 0:
            print('Ничего не найдено')
        else:
            table = PrettyTable(align='l', field_names=InputConnect.table_header, max_width=20, hrules=1)
            table.add_rows(rows)
            print(table.get_string(fields=self.table_fields))

    table_header = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад',
                    'Название региона', 'Дата публикации вакансии']

    def parse_filter_param(self, filter_param):
        if filter_param == '':
            return []
        if ': ' not in filter_param:
            self.errors.append('Формат ввода некорректен')
            return []
        filter_param = filter_param.split(': ')
        if filter_param[0] not in list(DataSet.cond_to_sort.keys()):
            self.errors.append('Параметр поиска некорректен')
            return []
        return filter_param

    def parse_sort_reverse(self, sort_reverse):
        if sort_reverse not in ('', 'Да', 'Нет'):
            self.errors.append('Порядок сортировки задан некорректно')
        return True if sort_reverse == 'Да' else False

    def parse_sort_param(self, sort_param):
        if sort_param not in InputConnect.table_header + ['']:
            self.errors.append('Параметр сортировки некорректен')
        return sort_param

    @staticmethod
    def parse_table_fields(table_fields):
        return InputConnect.table_header if table_fields == '' else ['№'] + [a for a in table_fields.split(', ') if
                                                                             a in InputConnect.table_header]

    @staticmethod
    def parse_sort_range(sort_range):
        return [] if sort_range == '' else [int(limit) - 1 for limit in sort_range.split()]


def get_table():
    InputConnect()
