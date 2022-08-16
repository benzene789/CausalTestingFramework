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

from data.improved_csv_gen import new_shipment

import pandas as pd
import numpy as np
import random

np.random.seed(random.randint(0, 50000))

content_types = {'tiles': 0.65,
                 'electrical': 0.25,
                 'wood': 0.45,
                 'banana': 0.90}

countries = {'China': 0.25,
             'France': 0.60,
             'Russia': 0.90}

# 1. Read in the Causal DAG
causal_dag = CausalDAG("./dag.dot")

# 2. Create variables
plane_transport = Input("plane_transport", bool)
country = Input("country", str)
content = Input('content', str)
weight = Input('weight', float)
s1 = Input("S1", bool)
s2 = Input("S2", bool)
s3 = Input("S3", bool)

alarm = Output("alarm", bool)

# 3. Create scenario by applying constraints over a subset of the input variables
scenario = Scenario(
    variables={
        plane_transport,
        country,
        content,
        weight,
        s1,
        s2,
        s3,
        alarm,
    }
)

# 4. Construct a causal specification from the scenario and causal DAG
causal_specification = CausalSpecification(scenario, causal_dag)

observational_data_path = 'data/new_test.csv'

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

    # 9. Set up an estimator
    data = pd.read_csv(observational_data_path)

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
    # causal_test_result = causal_test_engine.execute_test(
    #     estimator, causal_test_case.estimate_type
    # )
    control_prediction, treatment_prediction = estimator.estimate_control_treatment()
    # causal_test_result = CausalTestResult(
    #     treatment=estimator.treatment,
    #     outcome=estimator.outcome,
    #     treatment_value=estimator.treatment_values,
    #     control_value=estimator.control_values,
    #     adjustment_set=estimator.adjustment_set,
    #     ate=prediction,
    #     effect_modifier_configuration=causal_test_case.effect_modifier_configuration,
    #     adjustment_set_configuration=causal_test_case.adjustment_set_configuration,
    #     confidence_intervals=confidence_interval)

    return (control_prediction, treatment_prediction)


def get_ate(name, control, treatment, shipment):
    # 5. Create a causal test case
    causal_test_case = CausalTestCase(
        control_input_configuration={scenario.variables[name]: control},
        treatment_input_configuration={scenario.variables[name]: treatment},
        expected_causal_effect=ExactValue(4, tolerance=0.5),
        outcome_variables={alarm},
        estimate_type="ate",
    )
    control_prediction, treatment_prediction = test_shipment(
        observational_data_path,
        causal_test_case,
        shipment
    )

    return (control_prediction, treatment_prediction)

def categorical_predictions(type, seen):
    if type == 'content':
        dict_keys = list(content_types.keys())
    else:
        dict_keys = list(countries.keys())

    dict_keys.remove(seen)
    remaining = list(dict_keys)

    fuzzed = remaining[np.random.randint(len(remaining))]

    preds = get_ate(type, seen, fuzzed, shipment_df)

    predictions.append((seen, preds[0]))
    predictions.append((fuzzed, preds[1]))

    remaining.remove(fuzzed)

    for fuzz in remaining:
        predictions.append((fuzz, get_ate(type, seen, fuzz, shipment_df)[1]))

    print('Predictions for ' + seen, predictions)

    print('=' * 150)
    print('Seen value: ', seen)

    for val in predictions:
        print_str = str(val[0]) + ' sets off the alarm ' + str(val[1])
        print(print_str)
    print(shipment_df)


def binary_predictions(type, seen):
    # Came on plane or ship

    if seen == 1:
        fuzzed = 0        
    else:
        fuzzed = 1

    preds = get_ate(type, seen, fuzzed, shipment_df)
    predictions.append((seen, preds[0]))
    predictions.append((fuzzed, preds[1]))

    for val in predictions:
        print_str = str(type) + ' as ' + str(bool(val[0])) + ' sets off the alarm ' + str(val[1])
        print(print_str)
    print(shipment_df)

def float_predictions(type, seen, n):
    # Trial n different numbers
    weight_predictions = []
    for val in range(n):
        fuzzed_weight = np.random.rand() * 100
        preds = get_ate(type, seen, fuzzed_weight, shipment_df)

        if len(weight_predictions) == 0:
            weight_predictions.append((seen, preds[0]))
            
        predictions.append((fuzzed_weight, preds[1]))

    for val in predictions:
        print_str = str(val[0]) + ' set off the alarm ' + str(val[1])
        print(print_str)
    print(shipment_df)


'''
For each edge, get treatment and outcome. Fuzz treatment and examine effect of treatment on alarm
Calculate if change in alarm, if there is calculate distance from original value

'''

# Get all edges
edges = []
for edge in causal_dag.graph:
    edges.append(edge)

# alarm
outcome = edges[len(causal_dag.graph)-1]

edges.remove(outcome)
edges.remove('distance')
# Separate out layers of DAG into separate lists

layer_1 = [dag_edge for dag_edge in edges if 'S'.upper() not in dag_edge]
sensor_layer = list(set(edges) - set(layer_1))
outcome = [outcome]

# Now we generate a mock row of the csv

shipment = new_shipment()
shipment_df =  pd.DataFrame([shipment], columns=['country', 'plane_transport', 'content', 'weight', 'S1', 'S2', 'S3', 'alarm'])
print(shipment_df)
# Fuzz the different nodes in outer layer
for fuzz_type in layer_1:
    print(fuzz_type)
    # Get fuzz value
    seen = shipment_df[fuzz_type].to_numpy()[0]

    predictions = []

    # Categorical predictions
    # if shipment_df[fuzz_type].dtypes == 'object':
    #     categorical_predictions(fuzz_type, seen)

    # Non-categorical, binary only
    # if seen == 1 or seen == 0:
    #     binary_predictions(fuzz_type, seen)

    # Non-categorical, float
    if shipment_df[fuzz_type].dtypes == 'float':
        float_predictions(fuzz_type, seen, 10)

        
