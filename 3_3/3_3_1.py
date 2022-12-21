import pandas as pd
import requests

pd.set_option('expand_frame_repr', False)
df = pd.read_csv('C:\\Users\\vinni\\Documents\\PycharmProjects\\Vinnik\\csv\\vacancies_dif_currencies.csv')

df['published'] = pd.to_datetime(df['published_at'], format='%Y-%m-%dT%H:%M:%S%z', utc=True)
sorted_by_date = df.sort_values(by='published').reset_index()
months = list(sorted_by_date.published.dt.strftime('%m/%Y').unique())

count = df.groupby('salary_currency')['salary_currency'].count()
print(count[count > 5000].to_dict())

df_api_currency = pd.DataFrame(columns=["date", "BYR", "USD", "EUR", "KZT", "UAH"])

for i in range(0, len(months)):
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{months[i]}d=1'
    response = requests.get(url)
    currencies = pd.read_xml(response.text)
    currencies2 = currencies.loc[currencies['CharCode'].isin(['BYN', 'BYR', 'EUR', 'KZT', 'UAH', 'USD'])]

    BYR = float(currencies2.loc[currencies2['CharCode'].isin(['BYR', 'BYN'])]['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'].isin(['BYR', 'BYN'])]['Nominal'].values[0])
    EUR = float(currencies2.loc[currencies2['CharCode'] == 'EUR']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'EUR']['Nominal'].values[0])
    KZT = float(currencies2.loc[currencies2['CharCode'] == 'KZT']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'KZT']['Nominal'].values[0])
    UAH = float(currencies2.loc[currencies2['CharCode'] == 'UAH']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'UAH']['Nominal'].values[0])
    USD = float(currencies2.loc[currencies2['CharCode'] == 'USD']['Value'].values[0].replace(',', '.')) / \
          (currencies2.loc[currencies2['CharCode'] == 'USD']['Nominal'].values[0])

    df_api_currency.loc[i] = [f'{months[i][3:]}-{months[i][:2]}', BYR, EUR, KZT, UAH, USD]

df_api_currency.to_csv('curr.csv')
