import pandas as pd
import sqlite3

con = sqlite3.connect('/3_5/3_5_1/currencies.sqlite')
c = con.cursor()

df = pd.read_csv('/3_5/3_5_1/curr.csv')
df = df.to_sql('currencies', con, if_exists='replace', index=False)
con.commit()
