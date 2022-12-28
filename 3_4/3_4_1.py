import math
from statistics import mean
import pandas as pd

pd.set_option('expand_frame_repr', False)
date_df = pd.read_csv('C:\\Users\\vinni\\PycharmProjects\\Vinnik\\3_4\\curr.csv')
df = pd.read_csv('C:\\Users\\vinni\\PycharmProjects\\Vinnik\\csv\\vacancies_dif_currencies.csv')


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


df['salary'] = df.apply(lambda row: get_salary(row['salary_from'],
                                               row['salary_to'],
                                               row['salary_currency'],
                                               row['published_at'][:7].split('-')), axis=1)

df[:100].to_csv('vac_dif_curr.csv', index=False)
