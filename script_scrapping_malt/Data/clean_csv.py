import pandas as pd
import matplotlib.pyplot as plt

file_csv = "./script_scrapping_malt/Data/clean_data.csv"
df= pd.read_csv(file_csv)

def anonymize_names(name):
    return 'person' + str(name)

# column name to string
df['name'] = 'person' + pd.Series(pd.factorize(df['Freelance'])[0] + 1).astype(str)

# column price to int
df['price'] = df['price'].str.replace('€', '')
df = df.astype({'price': 'int32'})

print(df.head())

# plt.figure(figsize=(20, 14))
# plt.table(cellText=data.values, colLabels=data.columns, loc='center')
# plt.axis('off')
# plt.show()