
from signal import alarm
from causal_testing.specification.causal_dag import CausalDAG
from causal_testing.specification.scenario import Scenario
from causal_testing.specification.variable import Input, Output
from causal_testing.specification.causal_specification import CausalSpecification
from causal_testing.data_collection.data_collector import ObservationalDataCollector
from causal_testing.testing.causal_test_case import CausalTestCase
from causal_testing.testing.causal_test_outcome import ExactValue, Positive
from causal_testing.testing.causal_test_engine import CausalTestEngine
from causal_testing.testing.estimators import Estimator, LogisticRegressionEstimator
from causal_testing.testing.causal_test_outcome import CausalTestResult

import pandas as pd
import numpy as np
import random
import sys

np.random.seed(random.randint(0, 50000))

types = {
        np.dtype("float64"): float,
        np.dtype("int64"): int,
        np.dtype("object"): str,
        pd.Int64Dtype(): int,
    }

DAG_FILE = sys.argv[1]

observational_data_path = sys.argv[2]

data = pd.read_csv(observational_data_path)
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

alarm_col = str(list(data.columns)[len(data.columns)-1])

# 1. Read in the Causal DAG
causal_dag = CausalDAG(DAG_FILE)

# 2. Create variables
vars = set()
for col in data.columns:
    data_type = types[data.dtypes[col]]
    dag_var = Input(col, data_type)
    vars.add(dag_var)

# 3. Create scenario by applying constraints over a subset of the input variables
scenario = Scenario(variables=vars)

# 4. Construct a causal specification from the scenario and causal DAG
causal_specification = CausalSpecification(scenario, causal_dag)

def test_shipment(
    observational_data_path,
    causal_test_case,
    shipment
):
    # 6. Create a data collector
    data_collector = ObservationalDataCollector(scenario, observational_data_path)

    # 7. Create an instance of the causal test engine
    causal_test_engine = CausalTestEngine(
        causal_test_case, causal_specification, data_collector
    )

    # 8. Obtain the minimal adjustment set for the causal test case from the causal DAG
    causal_test_engine.load_data(index_col=0)

    # # 9. Set up an estimator
    # data = pd.read_csv(observational_data_path)

    treatment = list(causal_test_case.control_input_configuration)[0].name
    outcome = list(causal_test_case.outcome_variables)[0].name

    minimal_adjustment_sets = causal_dag.enumerate_minimal_adjustment_sets([v.name for v in causal_test_case.control_input_configuration], [v.name for v in causal_test_case.outcome_variables])
    minimal_adjustment_set = min(minimal_adjustment_sets, key=len)

    minimal_adjustment_set = \
            minimal_adjustment_set - {v.name for v in causal_test_case.control_input_configuration}
    minimal_adjustment_set = minimal_adjustment_set - {v.name for v in causal_test_case.outcome_variables}

    estimator = LogisticRegressionEstimator(
        treatment=[treatment],
        control_values=list(causal_test_case.control_input_configuration.values())[
            0
        ],
        treatment_values=list(
            causal_test_case.treatment_input_configuration.values()
        )[0],
        adjustment_set=minimal_adjustment_set,
        adjustment_set_configuration={scenario.variables[k]:shipment[k][0] for k in minimal_adjustment_set},
        outcome=[outcome],
        df=data,
    )

    # 10. Execute the test
    control_prediction, treatment_prediction = estimator.estimate_control_treatment()

    return (control_prediction, treatment_prediction)


def get_ate(name, control, treatment, shipment):
    # 5. Create a causal test case
    causal_test_case = CausalTestCase(
        control_input_configuration={scenario.variables[name]: control},
        treatment_input_configuration={scenario.variables[name]: treatment},
        expected_causal_effect=ExactValue(4, tolerance=0.5),
        outcome_variables={scenario.variables[alarm_col]},
        estimate_type="ate",
    )
    control_prediction, treatment_prediction = test_shipment(
        observational_data_path,
        causal_test_case,
        shipment
    )

    return (control_prediction, treatment_prediction)

def categorical_predictions(type, seen, shipment_df):

    c_prediction_list = []

    # For getting unique column/category values in column of 'type' variable
    data = pd.read_csv(observational_data_path)

    unique_vals = list(data[type].unique())
    
    print(unique_vals)
   
    unique_vals.remove(seen)

    fuzzed = unique_vals[np.random.randint(len(unique_vals))]

    # Get the predicted values for the seen shipment location and a random fuzz
    preds = get_ate(type, seen, fuzzed, shipment_df)
    c_prediction_list.append((seen, preds[0]))
    c_prediction_list.append((fuzzed, preds[1]))

    # Remove and fuzz the rest
    unique_vals.remove(fuzzed)

    for fuzz in unique_vals:
        c_prediction_list.append((fuzz, get_ate(type, seen, fuzz, shipment_df)[1]))

    print('Predictions for ' + seen, c_prediction_list)

    print('=' * 150)
    print('Seen value: ', seen)

    for val in c_prediction_list:
        print_str = str(val[0]) + ' sets off the alarm ' + str(val[1])

        print(print_str)
    print(shipment_df)

    return c_prediction_list


def binary_predictions(type, seen, shipment_df):
    # Came on plane or ship

    binary_preds = []

    if seen == 1:
        fuzzed = 0        
    else:
        fuzzed = 1

    preds = get_ate(type, seen, fuzzed, shipment_df)
    binary_preds.append((seen, preds[0]))
    binary_preds.append((fuzzed, preds[1]))

    for val in binary_preds:
        print_str = str(type) + ' as ' + str(bool(val[0])) + ' sets off the alarm ' + str(val[1])

    print(print_str)
    print(shipment_df)

    print(binary_preds)

    return binary_preds

def float_predictions(type, seen, n, shipment_df):
    # Trial n different numbers
    weight_predictions = []
    for val in range(n):
        fuzzed_weight = np.random.uniform(0, 100.0)
        preds = get_ate(type, seen, fuzzed_weight, shipment_df)

        if len(weight_predictions) == 0:
            weight_predictions.append((seen, preds[0]))
            
        weight_predictions.append((fuzzed_weight, preds[1]))

    for val in weight_predictions:
        print_str = str(val[0]) + ' set off the alarm ' + str(val[1])
        print(print_str)
    print(shipment_df)

    return weight_predictions

def calc_threshold_vals(preds: list, min_alarm_chance: float):
    above = [a for a in preds if a[1] > min_alarm_chance]
    below = [b for b in preds if b[1] < min_alarm_chance]

    if len(below) != 0:
        max_threshold_below = max(below,key=lambda c:c[1])
    else:
        max_threshold_below = (None, min_alarm_chance)
    
    if len(above) != 0:
        min_threshold_above = min(above,key=lambda d:d[1])
    else:
        min_threshold_above = (None, min_alarm_chance)

    return (max_threshold_below, min_threshold_above)

def distance_metric_float(float_predictions: list, min_alarm_chance: float, seen):
    # Split into two lists, above and below threshold

    max_threshold_below, min_threshold_above = calc_threshold_vals(float_predictions, min_alarm_chance)

    float_predictions = dict(float_predictions)

    float_distance = 0

    print('=' * 150)
    print('DISTANCE METRIC FOR WEIGHT')

    if max_threshold_below[0] is None:
        max_threshold_below_list = list(max_threshold_below)
        max_threshold_below_list[0] = min_alarm_chance
        max_threshold_below = tuple(max_threshold_below_list)
    
    if min_threshold_above[0] is None:
        min_threshold_above_list = list(min_threshold_above)
        min_threshold_above_list[0] = min_alarm_chance
        min_threshold_above = tuple(min_threshold_above_list)

    print(max_threshold_below)
    print(min_threshold_above)

    if seen > max_threshold_below[0]:
        print('Need to change value to ' + str(max_threshold_below[0]) + ' from ' + str(seen))

        print('This effects the alarm from ' + str(float_predictions[seen]) + ' to ' + str(max_threshold_below[1]))

        print('This is an increase of ' + str(seen - max_threshold_below[0]))

        float_distance = float_predictions[seen] - max_threshold_below[1]
    
    elif seen < min_threshold_above[0]:

        print('Need to change value to ' + str(min_threshold_above[0]) + ' from ' + str(seen))

        print('This effects the alarm from ' + str(float_predictions[seen]) + ' to ' + str(min_threshold_above[1]))

        print('This is an increase of ' + str(min_threshold_above[0] - seen))

        float_distance = min_threshold_above[1] - float_predictions[seen]

    return float_distance


def distance_metric_categorical(c_prediction_list: list, min_alarm_chance: float, seen):
    # Get all categorical predictions
    # Keep threshold in mind (min_alarm_chance). 
    # Find out what which categories for that shipment will cause the alarm to go trigger and not trigger
    # Find the min and max of the boundary between alarm triggering
    # This is the distance metric

    category_distance = 0

    max_threshold_below, min_threshold_above = calc_threshold_vals(c_prediction_list, min_alarm_chance)

    cat_predictions = {k: v for k, v in sorted(dict(c_prediction_list).items(), key=lambda item: item[1])}

    print(cat_predictions)

    if cat_predictions[seen] > max_threshold_below[1]:
        print('Need to change category to ' + str(max_threshold_below[0]) + ' from ' + str(seen))

        print('This effects the alarm from ' + str(cat_predictions[seen]) + ' to ' + str(max_threshold_below[1]))

        category_distance = cat_predictions[seen] - max_threshold_below[1]

    elif cat_predictions[seen] < min_threshold_above[1]:

        print('Need to change category to ' + str(min_threshold_above[0]) + ' from ' + str(seen))

        print('This effects the alarm from ' + str(cat_predictions[seen]) + ' to ' + str(min_threshold_above[1]))

        category_distance = min_threshold_above[1] - cat_predictions[seen]

    return category_distance

def distance_metric_binary(b_prediction_list: list, min_alarm_chance: float, seen):

    binary_dist = 0

    b_prediction_dict = dict(b_prediction_list)

    if seen == 1:
        key = 0
    else:
        key = 1

    if b_prediction_dict[seen] > b_prediction_dict[key]:
        binary_dist = b_prediction_dict[seen] - b_prediction_dict[key]
    else:
        binary_dist = b_prediction_dict[key] - b_prediction_dict[seen]
    
    return binary_dist

'''
For each edge, get treatment and outcome. Fuzz treatment and examine effect of treatment on alarm
Calculate if change in alarm, if there is calculate distance from original value
'''

def collect_shipment():

    # Get all edges
    # alarm column may have a different name

    edges = [dag_edge for dag_edge in causal_dag.graph if alarm_col not in dag_edge]

    # New shipment coming in

    # Average alarm chance in the trained DataFrame
    average_alarm_chance = data[alarm_col].sum()/len(data)

    print(edges)
    return average_alarm_chance, edges

def order_edge_predictions(shipment_df):

    FLOAT_FUZZ_AMOUNT = 15

    average_alarm_chance, edges = collect_shipment()

    print('Alarm has a high chance of triggering when above', average_alarm_chance)
    # Fuzz the different nodes in outer layer
    distances = []
     
    for fuzz_type in edges:
        print(shipment_df[fuzz_type].dtypes)
        # Get fuzz value
        seen = shipment_df[fuzz_type].to_numpy()[0]

        # Categorical predictions
        if shipment_df[fuzz_type].dtypes == 'object':
            c_prediction_list = categorical_predictions(fuzz_type, seen, shipment_df)
            distances.append((fuzz_type, distance_metric_categorical(c_prediction_list, average_alarm_chance, seen)))

        # Non-categorical, binary only
        elif seen == 1 or seen == 0:
            b_prediction_list = binary_predictions(fuzz_type, seen, shipment_df)
            print(b_prediction_list)
            distances.append((fuzz_type, distance_metric_binary(b_prediction_list, average_alarm_chance, seen)))

        # Non-categorical, float
        elif shipment_df[fuzz_type].dtypes == 'float':
            weight_predictions = float_predictions(fuzz_type, seen, FLOAT_FUZZ_AMOUNT, shipment_df)
            distances.append((fuzz_type, distance_metric_float(weight_predictions, average_alarm_chance, seen)))

    print(distances)
    ordered = {k: v for k, v in sorted(dict(distances).items(), key=lambda item: item[1])}

    print('ORDERED EDGES')

    print('=' * 150)

    print(ordered)

    return ordered
