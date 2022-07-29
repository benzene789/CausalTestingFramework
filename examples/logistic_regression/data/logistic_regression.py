from traceback import print_tb
import statsmodels.formula.api as smf

import pandas as pd

df = pd.read_csv('random_complex.csv')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

print(df)

# What effect does the country have on whether alarm was set off?
model = smf.logit(formula='S3 ~ country', data=df)
results = model.fit()

# What lengths do we want to ask it about?
countries = pd.DataFrame([
    { 'country': 'France' },
    { 'country': 'China' },
    { 'country': 'Russia' },

])

transport = pd.DataFrame([
    { 'plane': '1' },
    { 'plane': '1' },
    { 'plane': '0' },
    { 'plane': '1' },
    { 'plane': '1' },
    { 'plane': '0' },
    { 'plane': '0' },
    { 'plane': '0' },
])

# Save the predictions into a new column
countries['predicted'] = results.predict(countries)

print(countries)

results.summary()

# model_2 = smf.logit(formula='S2 ~ plane', data=df)
# results_2 = model_2.fit()

# transport['predicted'] = results_2.predict(transport)

# print(transport)