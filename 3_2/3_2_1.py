import pandas as pd

file_name = "C:\\Users\\vinni\\Documents\\PycharmProjects\\Vinnik\\csv\\vacancies_by_year.csv"
df = pd.read_csv(file_name)

df["years"] = df["published_at"].apply(lambda date: int(date[:4]))
years = df["years"].unique()
for year in years:
    data = df[df["years"] == year]
    data.iloc[:, :6].to_csv(rf"new_csv_files\part_{year}.csv", index=False)
