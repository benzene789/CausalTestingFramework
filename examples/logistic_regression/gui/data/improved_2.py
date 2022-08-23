import random
import numpy as np
import pandas as pd

location = {'Spain': 0.15,
             'Brazil': 0.5,
             'Cuba': 0.8,
             'Mexico':0.3}

def trigger_s1(loc: int, delivery_chance: int):
    loc_coef = 0.1

    trigger_s1_chance = (loc_coef * loc) + delivery_chance

    random = np.random.rand()

    return int(random < trigger_s1_chance)


# Location, delivery type and length contribute to S2
def trigger_s2(loc: int, delivery_type: int, length: float) -> bool:
    loc_coef = 0.1

    trigger_s2_chance = ((loc_coef * loc) + delivery_type + length/100)/3

    random = np.random.rand()

    return int(random < trigger_s2_chance)

# S3 for transport
def trigger_s3(chance: float) -> bool:    
    return int(np.random.uniform() < chance)

def trigger_alarm(s1: int, s2: int, s3: int, shipment: bool, average_alarm: float) -> bool:
    s1_prob = 0.45
    s2_prob = 0.55
    s3_prob = 0.7

    random = np.random.rand()

    trigger_alarm_chance = ((s1_prob * s1) + (s2_prob * s2) + (s3_prob * s3)) / (s1_prob + s2_prob + s3_prob)

    if(shipment):
        return int(trigger_alarm_chance > average_alarm)
    else:
        return int(random < trigger_alarm_chance)
        

def new_shipment(shipment: bool, average_alarm: float) -> None:
    np.random.seed(random.randint(0, 50000))

    df_row = []

    s1_triggered = 0
    s2_triggered = 0
    s3_triggered = 0
    alarm_triggered = 0

    # plane or ship
    delivery_type = np.random.randint(0,2)

    # Delivery location of origin
    delivery_location = list((location.keys()))[int(np.random.randint(0, 4))]
    delivery_chance = location[delivery_location]


    # Planes have 30% chance, ship has 70%
    if delivery_type:
        delivery_type_percent = 0.3
        s1_triggered = trigger_s1(delivery_type_percent, delivery_chance)
    else:
        delivery_type_percent = 0.7
        s1_triggered = trigger_s1(delivery_type_percent, delivery_chance)

    length = np.random.rand() * 50

    s2_triggered = trigger_s2(delivery_chance, delivery_type_percent, length)

    s3_triggered = trigger_s3(delivery_chance)

    alarm_triggered = trigger_alarm(s1_triggered, s2_triggered, s3_triggered, shipment, average_alarm)


    # Sort out rows of df
    df_row.append(delivery_location)
    df_row.append(delivery_type)
    df_row.append(length)
    df_row.append(s1_triggered)
    df_row.append(s2_triggered)
    df_row.append(s3_triggered)
    df_row.append(alarm_triggered)

    return df_row


def create_csv():
    columns = ['delivery_location', 'delivery_type', 'length', 'S1', 'S2', 'S3', 'trigger']

    df_row = new_shipment(False, 0)
    df_rows = []
    for row in range(10000):    

        df_row = new_shipment(False, 0)
        
        df_rows.append(df_row)


    df = pd.DataFrame(df_rows, columns=columns)

    df.to_csv('test_2.csv')

    print('DONE!')

#create_csv()