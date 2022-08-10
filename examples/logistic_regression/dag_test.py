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

print(causal_dag.graph)

'''
For each edge, get treatment and outcome. Fuzz treatment and examine effect of treatment on alarm
Calculate if change in alarm, if there is calculate distance from original value


'''

for edge in causal_dag.graph:
    print(edge)
    
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