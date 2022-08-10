from causal_testing.specification.causal_dag import CausalDAG
from causal_testing.specification.scenario import Scenario
from causal_testing.specification.variable import Input, Output
from causal_testing.specification.causal_specification import CausalSpecification
from causal_testing.data_collection.data_collector import ObservationalDataCollector
from causal_testing.testing.causal_test_case import CausalTestCase
from causal_testing.testing.causal_test_outcome import ExactValue, Positive
from causal_testing.testing.causal_test_engine import CausalTestEngine
from causal_testing.testing.estimators import Estimator, LogisticRegressionEstimator

import pandas as pd
import numpy as np
import random

# 1. Read in the Causal DAG
causal_dag = CausalDAG("./dag.dot")

# 2. Create variables
plane_transport = Input("plane_transport", bool)
country = Input("country", str)
s1 = Input("S1", bool)
s2 = Input("S2", bool)
s3 = Input("S3", bool)

alarm = Output("alarm", bool)

# 3. Create scenario by applying constraints over a subset of the input variables
scenario = Scenario(
    variables={
        plane_transport,
        country,
        s1,
        s2,
        s3,
        alarm,
    }
)

def generate_mock_row():
    np.random.seed(random.randint(0, 50000))
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

    content_pick = int(np.random.randint(0, 3))
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
        
    df = pd.DataFrame([df_row], columns=['country', 'plane_transport', 'content', 'weight', 'S1', 'S2', 'S3', 'alarm'])

    return df

def trigger_s1_or_s2(chance: float) -> bool:    
    return int(np.random.uniform() > chance)

content_types = {'tiles': 0.65,
                 'electrical': 0.25,
                 'wood': 0.45}

countries = {'China': 0.25,
             'France': 0.60,
             'Russia': 0.90}

# Both country and content contribute to S3
def trigger_s3(country: str, content: str, weight: float) -> bool:

    trigger_s3_chance = (countries[country] + content_types[content] + weight/100) / 3

    print(trigger_s3_chance)

    random = np.random.rand()

    return int(random > trigger_s3_chance)


def trigger_alarm(s1: int, s2: int, s3: int) -> bool:
    s1_prob = 0.4
    s2_prob = 0.5
    s3_prob = 0.7

    random = np.random.rand()

    trigger_alarm_chance = ((s1_prob * s1) + (s2_prob * s2) + (s3_prob * s3)) / (s1_prob + s2_prob + s3_prob)
    
    if s1 == 0 and s2 == 0 and s3 == 0:
        trigger_alarm_chance = 1
    
    return int(random > trigger_alarm_chance)


'''
For each edge, get treatment and outcome. Fuzz treatment and examine effect of treatment on alarm
Calculate if change in alarm, if there is calculate distance from original value

'''

# Get all edges
edges = []
for edge in causal_dag.graph:
    edges.append(edge)
        
print(edges)

# alarm
outcome = edges[len(causal_dag.graph)-1]

edges.remove(outcome)
edges.remove('distance')
# Separate out layers of DAG into separate lists

layer_1 = [dag_edge for dag_edge in edges if 'S'.upper() not in dag_edge]
sensor_layer = list(set(edges) - set(layer_1))
outcome = [outcome]
print(layer_1)
print(sensor_layer)
print(outcome)

# Now we generate a mock row of the csv

mock_row = generate_mock_row()
# Fuzz the different nodes in outer layer
for fuzz in layer_1:
    # Get fuzz value
    fuzz_value = mock_row[fuzz]
    print(mock_row)
    
    # Pick a different content
    if fuzz == 'content':
        content_keys = content_types.keys()
        remaining = list(content_keys - fuzz_value)
        new_type = remaining[np.random.randint(len(remaining))]
        
        mock_row[fuzz] = new_type
        
    # Using this new data frame, see if the alarm changes
    
    new_s1_s2_val = trigger_s1_or_s2(0.5)
    print(mock_row)
    new_s3_val = trigger_s3(mock_row.loc[0]['country'], mock_row.loc[0]['content'], mock_row.loc[0]['weight'])
    
    print(new_s1_s2_val)
    print(new_s3_val)
    
   

    quit()
    
quit()

# 4. Construct a causal specification from the scenario and causal DAG
causal_specification = CausalSpecification(scenario, causal_dag)

def test_intensity_num_shapes(
    observational_data_path,
    causal_test_case,
):
    # 6. Create a data collector
    data_collector = ObservationalDataCollector(scenario, observational_data_path)

    # 7. Create an instance of the causal test engine
    causal_test_engine = CausalTestEngine(
        causal_test_case, causal_specification, data_collector
    )

    # 8. Obtain the minimal adjustment set for the causal test case from the causal DAG
    causal_test_engine.load_data(index_col=0)

    # 9. Set up an estimator
    data = pd.read_csv(observational_data_path)

    treatment = list(causal_test_case.control_input_configuration)[0].name
    outcome = list(causal_test_case.outcome_variables)[0].name

    
    estimator = LogisticRegressionEstimator(
        treatment=[treatment],
        control_values=list(causal_test_case.control_input_configuration.values())[
            0
        ],
        treatment_values=list(
            causal_test_case.treatment_input_configuration.values()
        )[0],
        adjustment_set=set(),
        outcome=[outcome],
        df=data,
    )

    # 10. Execute the test
    causal_test_result = causal_test_engine.execute_test(
        estimator, causal_test_case.estimate_type
    )

    return causal_test_result


observational_data_path = "data/random_complex.csv"