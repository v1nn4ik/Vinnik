import pandas as pd
import sqlite3

con = sqlite3.connect('C:\\Users\\vinni\\PycharmProjects\\Vinnik\\3_5\\curr.sqlite')
c = con.cursor()

df = pd.read_csv('C:\\Users\\vinni\\PycharmProjects\\Vinnik\\3_5\\curr.csv')
df = df.to_sql('currencies', con, if_exists='replace', index=False)
con.commit()
