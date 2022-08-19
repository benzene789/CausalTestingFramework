import numpy as np
import pandas as pd

from geopy.distance import geodesic

content_types = ['tiles', 'electrical', 'wood']
countries = ['China', 'France', 'Russia']

df_rows = []

# France
FRANCE = [(48.8566, 2.3522), (43.7102, 7.2620), (45.7640, 4.8357)]

# UK
UK = [(51.5072, 0.1276), (53.4808, 2.2426), (50.7260, 3.5275), (51.4545, 2.5879)]

# China
CHINA = [(39.9042, -116.4074), (31.2304, -121.4737), (30.5928, -114.3052)]

# Russia
RUSSIA = [(55.7558, -37.6173), (59.9311, -30.3609), (54.9833, -82.8964)]

for row in range(10000):
    df_row = []

    # Country (each country has a different chance of setting off sensors)
    country_pick = int(np.random.randint(0, 3))

    china = False
    france = False
    russia = False

    # China
    city_pick_uk = UK[int(np.random.randint(0, 4))]
    if(country_pick == 0):
        china = True
        city_pick = CHINA[int(np.random.randint(0, 3))]

    # France
    elif(country_pick == 1):
        france = True
        city_pick = FRANCE[int(np.random.randint(0, 3))]

    # Russia
    else:
        russia = True
        city_pick = RUSSIA[int(np.random.randint(0, 3))]

    df_row.append(countries[country_pick])

    df_row.append(geodesic(city_pick_uk, city_pick).miles)

    # plane
    plane = np.random.randint(0,2)

    df_row.append(plane)


    # ship
    # If on plane, then cannot come through via ship and vice versa
    # if plane == 1:
    #     df_row.append(0)
    # else:
    #     df_row.append(1)

    # content
    content_pick = int(np.random.randint(0, 3))
    df_row.append(content_types[content_pick])

    # amount
    df_row.append(np.random.uniform(1, 50))

    # S1, S2, S3
    # If on plane, can only go through S1, ships can only go through S2
    # Planes have a 30% chance of setting off S1, ships have 70% chance of setting off S2

    if plane == 1:
        s1 = int(np.random.uniform() > 0.5)
        s2 = 0
    else:
        s1 = 0
        s2 = int(np.random.uniform() > 0.5)

    # COUNTRIES TO SET OFF SENSORS

    # China has a 25% chance of setting off S3
    if china:
        s3 = int(np.random.uniform() > 0.75)
    # France has 60% chance of setting off S3
    elif france:
        s3 = int(np.random.uniform() > 0.4)
    # Russia has 90% chance of setting off S3
    else:
        s3 = int(np.random.uniform() > 0.1)

    df_row.append(s1)
    df_row.append(s2)
    df_row.append(s3)

    # alarm
    if(s1 == 0 and s2 == 0 and s3 == 0):
        df_row.append(0)
    else:
        df_row.append(np.random.randint(0,2))
        # # S1 has a 40% chance of setting off alarm
        # if s1:
        #     df_row.append(int(np.random.normal() > 0.6))
        # # S2 has a 50% chance of setting off alarm
        # elif s2:
        #     df_row.append(int(np.random.normal() > 0.5))
        # # S3 has a 70% chance of setting off alarm
        # else:
        #     df_row.append(int(np.random.normal() > 0.3))

    df_rows.append(df_row)

df = pd.DataFrame(df_rows, columns=['country', 'distance', 'plane_transport', 'content', 'amount', 'S1', 'S2', 'S3', 'alarm'])
print(df)

print('DONE!')
df.to_csv('random_complex.csv')

