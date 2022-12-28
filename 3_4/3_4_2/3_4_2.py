import math
from concurrent import futures
from statistics import mean
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit

date_df = pd.read_csv('C:\\Users\vinni\\PycharmProjects\\Vinnik\\3_4\\3_4_2\\curr.csv')


class Multithreading:
    def run(self):
        vacancy_name = self[0]
        year = self[1]
        df = pd.read_csv(f'new_csv_files\\part_{year}.csv')
        df.loc[:, 'salary'] = df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
        df_vacancy = df[df['name'].str.contains(vacancy_name)]

        salary_by_years = {year: []}
        vacs_by_years = {year: 0}
        vac_salary_by_years = {year: []}
        vac_counts_by_years = {year: 0}

        salary_by_years[year] = int(df['salary'].mean())
        vacs_by_years[year] = len(df)
        vac_salary_by_years[year] = int(df_vacancy['salary'].mean())
        vac_counts_by_years[year] = len(df_vacancy)

        return [salary_by_years, vacs_by_years, vac_salary_by_years, vac_counts_by_years]


class Salary:
    def get_salary(salary_from, salary_to, salary_currency, date):
        date = date[1] + '/' + date[0]
        salary_value = 0

        if salary_currency in ['BYN', 'BYR', 'EUR', 'KZT', 'UAH', 'USD'] and salary_currency != 'RUR':
            df_date_row = date_df.loc[date_df['date'] == date]
            salary_currency.replace('BYN', 'BYR')
            salary_value = df_date_row[salary_currency].values[0]
        elif salary_currency == 'RUR':
            salary_value = 1

        if not (math.isnan(salary_from)) and math.isnan(salary_to):
            return salary_from * salary_value
        elif math.isnan(salary_from) and not (math.isnan(salary_to)):
            return salary_to * salary_value
        elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
            return mean([salary_from, salary_to]) * salary_value


class UserInput:
    def __init__(self):
        self.file_name = input('Введите название файла: ')
        self.vacancy_name = input('Введите название профессии: ')


class Report:
    def __init__(self, vac_name, dicts_by_year):
        self.generate_image(vac_name, dicts_by_year)
        self.generate_pdf(vac_name, dicts_by_year)

    @staticmethod
    def generate_pdf(vac_name, dicts_by_year):
        env = Environment(loader=FileSystemLoader('..'))
        template = env.get_template("pdf_template.html")

        pdf_template = template.render(
            {'name': vac_name, 'by_year': dicts_by_year})

        options = {'enable-local-file-access': None}
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options=options)

    @staticmethod
    def generate_image(vac_name, dicts_by_year):
        x_nums = np.arange(len(dicts_by_year[0].keys()))
        width = 0.4
        x_list1 = x_nums - width / 2
        x_list2 = x_nums + width / 2
        fig = plt.figure()

        ax = fig.add_subplot(221)
        ax.set_title("Уровень зарплат по годам")
        ax.bar(x_list1, dicts_by_year[0].values(), width, label="средняя з/п")
        ax.bar(x_list2, dicts_by_year[1].values(), width, label=f"з/п {vac_name.lower()}")
        ax.set_xticks(x_nums, dicts_by_year[0].keys(), rotation="vertical")
        ax.tick_params(axis="both", labelsize=8)
        ax.legend(fontsize=8)
        ax.grid(True, axis="y")

        ax = fig.add_subplot(222)
        ax.set_title("Количество вакансий по годам")
        ax.bar(x_list1, dicts_by_year[2].values(), width, label="Количество вакансий")
        ax.bar(x_list2, dicts_by_year[3].values(), width, label=f"Количество вакансий \n{vac_name.lower()}")
        ax.set_xticks(x_nums, dicts_by_year[2].keys(), rotation="vertical")
        ax.tick_params(axis="both", labelsize=8)
        ax.legend(fontsize=8)
        ax.grid(True, axis="y")

        plt.tight_layout()
        plt.savefig("graph.png")


class SplitData:
    def __init__(self, file_name):
        self.dataframe = pd.read_csv(file_name)

        self.dataframe['years'] = self.dataframe['published_at'].apply(lambda date: int(date[:4]))
        self.years = list(self.dataframe['years'].unique())

        for year in self.years:
            data = self.dataframe[self.dataframe['years'] == year]
            data.iloc[:, :6].to_csv(rf'new_csv_files\part_{year}.csv', index=False)


class Sorting:
    def dict_sort(self):
        return dict(sorted(self.items(), key=lambda item: item[1]))

    def area_dict_sort(self):
        return {key: value for key, value in sorted(self.items(), key=lambda item: item[1], reverse=True)[:10]}


if __name__ == "__main__":
    temp = UserInput()
    file, vac = temp.file_name, temp.vacancy_name
    make_csv = SplitData(file)
    df = make_csv.dataframe
    years = make_csv.years

    df["salary"] = df.apply(lambda row: Salary.get_salary(row["salary_from"],
                                                          row["salary_to"],
                                                          row["salary_currency"],
                                                          row["published_at"][:7].split("-")), axis=1)

    salaries_by_year, vacancies_by_year, inp_vacancy_salary, inp_vacancy_count = {}, {}, {}, {}

    executor = futures.ProcessPoolExecutor()
    processes = []
    for year in years:
        args = (vac, year)
        returned_list = executor.submit(Multithreading.run(), args).result()
        salaries_by_year.update(returned_list[0])
        vacancies_by_year.update(returned_list[1])
        inp_vacancy_salary.update(returned_list[2])
        inp_vacancy_count.update(returned_list[3])

    print("Динамика уровня зарплат по годам:", Sorting.dict_sort(salaries_by_year))
    print("Динамика количества вакансий по годам:", Sorting.dict_sort(vacancies_by_year))
    print("Динамика уровня зарплат по годам для выбранной профессии:", Sorting.dict_sort(inp_vacancy_salary))
    print("Динамика количества вакансий по годам для выбранной профессии:", Sorting.dict_sort(inp_vacancy_count))

    dicts_list_by_year = [Sorting.dict_sort(salaries_by_year), Sorting.dict_sort(inp_vacancy_salary),
                          Sorting.dict_sort(vacancies_by_year), Sorting.dict_sort(inp_vacancy_count)]

    report = Report(temp.vacancy_name, dicts_list_by_year)
