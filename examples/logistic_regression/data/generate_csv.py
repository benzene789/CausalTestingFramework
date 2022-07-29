import numpy as np
import pandas as pd

content_types = ['tiles', 'electrical', 'wood']
countries = ['China', 'France', 'Russia']

df_rows = []

for row in range(90):
    df_row = []

    # plane
    plane = np.random.randint(2)
    df_row.append(plane)


    # ship
    # If on plane, then cannot come through via ship and vice versa
    if(plane == 1):
        df_row.append(0)
    else:
        df_row.append(1)
    

    # content
    content_pick = int(np.random.randint(0, 3))
    df_row.append(content_types[content_pick])

    # amount
    df_row.append(np.random.uniform(1, 50))

    # country
    country_pick = int(np.random.randint(0, 3))
    df_row.append(countries[country_pick])

    # S1, S2, S3
    # If on plane, can only go through S1, ships can only go through S2
    if plane == 1:
        s1 = np.random.randint(2)
        s2 = 0
    else:
        s1 = 0
        s2 = np.random.randint(2)

    s3 = np.random.randint(2)

    df_row.append(s1)
    df_row.append(s2)
    df_row.append(s3)

    # alarm
    if(s1 == 0 and s2 == 0 and s3 == 0):
        df_row.append(0)
    else:
        chance_of_alarm = np.random.rand()
        df_row.append(int(chance_of_alarm > 0.75))

    df_rows.append(df_row)


print(df_rows)

df = pd.DataFrame(df_rows, columns=['plane', 'ship', 'content', 'amount', 'country', 'S1', 'S2', 'S3', 'alarm'])
print(df)

print('DONE!')
df.to_csv('random.csv')