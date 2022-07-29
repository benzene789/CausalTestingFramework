import numpy as np
import pandas as pd

from geopy.distance import geodesic

content_types = ['tiles', 'electrical', 'wood']
countries = ['China', 'France', 'Russia']

df_rows = []

for row in range(10000):
    # chance of s1 = 0.5, s2 = 0.5

    df_row = []

    s1_coeff = 0.6
    s2_coeff = 0.25

    s1 = np.random.uniform()
    s2 = np.random.uniform()
    s3 = np.random.uniform()
    
    alarm = 0

    df_row.append(s1)
    df_row.append(s2)

    alarm_calc = (np.exp((s1_coeff * s1) + (s2_coeff * s2)))

    alarm += alarm_calc / (1 + (alarm_calc))

    print(alarm)

    random_num = np.random.uniform()

    df_row.append(int(alarm > random_num))

    #df_row.append(alarm)
    
    # if(s1 ==0 and s2 ==0 ):
    #     df_row.append(0)
    # else:
    #     if(s1):
    #         df_row.append(int(np.random.uniform() > 0.4))
    #     else:
    #         df_row.append(int(np.random.uniform() > 0.75))

    df_rows.append(df_row)


df = pd.DataFrame(df_rows, columns=['S1', 'S2', 'alarm'])

print(df)

print('DONE!')
df.to_csv('random_simple.csv')

