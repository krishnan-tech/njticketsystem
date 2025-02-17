import pandas as pd
import json

df = pd.read_csv("countss.csv", sep="\t")

filtered_df = df[df['b'].str.startswith('2024-09')]

print(filtered_df)

# Step 2: Group by column 'a' and get the count of each unique value in 'a'
result = filtered_df.groupby('a').size().reset_index(name='count')

result = result.sort_values(by='count', ascending=False)

# 'result' will contain the unique values in column 'a' and their respective counts
print(result)

with open("whitelist.json", 'r') as wl_file:
    whitelist = json.load(wl_file)

print([_ for _ in whitelist if _ not in result['a'].to_list()])