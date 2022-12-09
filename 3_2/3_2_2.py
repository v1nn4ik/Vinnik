# -*- coding: utf-8 -*-
import pandas as pd
from multiprocessing import Process, Queue
import cProfile

class UserInput:
    def __init__(self):
        self.file_name = input('Введите название файла: ')
        self.vacancy_name = input('Введите название профессии: ')

class Multithreading:
    def run(self, year, queue):
        df = pd.read_csv(f'new_csv_files\\part_{year}.csv')
        df.loc[:, 'salary'] = df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
        df_vacancy = df[df['name'].str.contains(self)]

        salary_by_years = {year: []}
        vacs_by_years = {year: 0}
        vac_salary_by_years = {year: []}
        vac_counts_by_years = {year: 0}

        salary_by_years[year] = int(df['salary'].mean())
        vacs_by_years[year] = len(df)
        vac_salary_by_years[year] = int(df_vacancy['salary'].mean())
        vac_counts_by_years[year] = len(df_vacancy)

        queue.put([salary_by_years, vacs_by_years, vac_salary_by_years, vac_counts_by_years])


class SplitData:
    def __init__(self, file_name):
        self.dataframe = pd.read_csv(file_name)

        self.dataframe['years'] = self.dataframe['published_at'].apply(lambda date: int(date[:4]))
        self.years = list(self.dataframe['years'].unique())

        for year in self.years:
            data = self.dataframe[self.dataframe['years'] == year]
            data.iloc[:, :6].to_csv(rf'new_csv_files\part_{year}.csv', index=False)


if __name__ == '__main__':
    pr = cProfile.Profile()
    pr.enable()
    pd.set_option('expand_frame_repr', False)

    user_input = UserInput()
    file, vacancy = user_input.file_name, user_input.vacancy_name
    csvs = SplitData(file)
    df, years = csvs.dataframe, csvs.years

    df['published_at'] = df['published_at'].apply(lambda date: int(date[:4]))
    df['salary'] = df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
    df['count'] = df.groupby('area_name')['area_name'].transform('count')
    df_norm = df[df['count'] >= 0.01 * len(df)]
    cities = list(df_norm['area_name'].unique())

    salaries_areas = {}
    vacancies_areas = {}
    for city in cities:
        df_s = df_norm[df_norm['area_name'] == city]
        salaries_areas[city] = int(df_s['salary'].mean())
        vacancies_areas[city] = round(len(df_s) / len(df), 4)

    queue = Queue()
    processes = []
    for year in years:
        proces = Process(target=Multithreading.run, args=(vacancy, year, queue))
        processes.append(proces)
        proces.start()
    dicts_list = []
    salaries_by_year = {}
    vacancies_by_year = {}
    vacancies_salary = {}
    vacancies_count = {}
    for proces in processes:
        dicts_list = queue.get()
        salaries_by_year.update(dicts_list[0])
        vacancies_by_year.update(dicts_list[1])
        vacancies_salary.update(dicts_list[2])
        vacancies_count.update(dicts_list[3])
        proces.join()

    def dict_sort(dictionary):
        return dict(sorted(dictionary.items(), key=lambda item: item[1]))

    def area_dict_sort(dictionary):
        return {key: value for key, value in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)[:10]}

    print('Динамика уровня зарплат по годам:', dict_sort(salaries_by_year))
    print('Динамика количества вакансий по годам:', dict_sort(vacancies_by_year))
    print('Динамика уровня зарплат по годам для выбранной профессии:', dict_sort(vacancies_salary))
    print('Динамика количества вакансий по годам для выбранной профессии:', dict_sort(vacancies_count))
    print('Уровень зарплат по городам (в порядке убывания):', area_dict_sort(salaries_areas))
    print('Доля вакансий по городам (в порядке убывания):', area_dict_sort(vacancies_areas))

    pr.disable()
    pr.print_stats(sort="calls")
