from curses import panel
import numpy as np
import pandas as pd

from geopy.distance import geodesic

# Planes and ships have a set chance of setting off S1 (ship) or S2 (ship)
def trigger_s1_or_s2(chance: float) -> bool:    
    return int(np.random.uniform() > chance)

content_types = {'tiles': 0.65,
                 'electrical': 0.25,
                 'wood': 0.45,
                 'banana': 0.90}

countries = {'China': 0.25,
             'France': 0.60,
             'Russia': 0.90}

# Both country and content contribute to S3
def trigger_s3(country: str, content: str, weight: float) -> bool:

    trigger_s3_chance = (countries[country] + content_types[content] + weight/100) / 3

    random = np.random.rand()

    return int(random < trigger_s3_chance)


def trigger_alarm(s1: int, s2: int, s3: int) -> bool:
    s1_prob = 0.4
    s2_prob = 0.5
    s3_prob = 0.7

    random = np.random.rand()

    trigger_alarm_chance = ((s1_prob * s1) + (s2_prob * s2) + (s3_prob * s3)) / (s1_prob + s2_prob + s3_prob)
    
    return int(random < trigger_alarm_chance)


df_rows = []
for row in range(10000):
    df_row = []

    s1_triggered = 0
    s2_triggered = 0
    s3_triggered = 0
    alarm_triggered = 0

    # plane or ship
    plane = np.random.randint(0,2)

    # Planes have 50% chance, ship has 50%
    if plane:
        s1_triggered = trigger_s1_or_s2(0.5)
    else:
        s2_triggered = trigger_s1_or_s2(0.5)

    country_pick = int(np.random.randint(0, 3))
    country_key = list(countries.keys())[country_pick]

    content_pick = int(np.random.randint(0, 4))
    content_key = list(content_types.keys())[content_pick]
    weight = np.random.rand() * 100

    s3_triggered = trigger_s3(country_key, content_key, weight)

    alarm_triggered = trigger_alarm(s1_triggered, s2_triggered, s3_triggered)

    if alarm_triggered > 0.4:
        alarm_triggered = 1
    else:
        alarm_triggered = 0

    # Sort out rows of df

    df_row.append(country_key)
    df_row.append(plane)
    df_row.append(content_key)
    df_row.append(weight)
    df_row.append(s1_triggered)
    df_row.append(s2_triggered)
    df_row.append(s3_triggered)
    df_row.append(alarm_triggered)

    df_rows.append(df_row)

df = pd.DataFrame(df_rows, columns=['country', 'plane_transport', 'content', 'weight', 'S1', 'S2', 'S3', 'alarm'])

df.to_csv('new_test.csv')

print('DONE!')
