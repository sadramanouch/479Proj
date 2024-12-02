import sys
import pandas as pd

in_file = sys.argv[1]
out_file = sys.argv[2]

df = pd.read_csv(in_file)
# apparently pages aren't the same size of something
df = df.head(1500)
print(df.shape)
df = df[df['state'] == 'closed']
df = df.sample(frac=1, random_state=42).reset_index(drop=True)


df = df[['html_url']]
df = df.rename(columns={'html_url':'url'})
df['reject'] = ''
df['notes'] = ''
df['fault_category'] = ''

df.to_csv(out_file, index=False)