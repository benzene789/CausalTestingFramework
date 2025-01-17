import logging

import lhsmdu
import pandas as pd
import z3
from scipy import stats

from causal_testing.specification.scenario import Scenario
from causal_testing.specification.variable import Variable
from causal_testing.testing.causal_test_case import CausalTestCase
from causal_testing.testing.causal_test_outcome import CausalTestOutcome

logger = logging.getLogger(__name__)


class AbstractCausalTestCase:
    """
    An abstract test case serves as a generator for concrete test cases. Instead of having concrete conctrol
    and treatment values, we instead just specify the intervention and the treatment variables. This then
    enables potentially infinite concrete test cases to be generated between different values of the treatment.
    """

    def __init__(
        self,
        scenario: Scenario,
        intervention_constraints: set[z3.ExprRef],
        treatment_variables: set[Variable],
        expected_causal_effect: dict[Variable:CausalTestOutcome],
        effect_modifiers: set[Variable] = None,
        estimate_type: str = "ate",
    ):
        assert treatment_variables.issubset(scenario.variables.values()), (
            "Treatment variables must be a subset of variables."
            + f" Instead got:\ntreatment_variables={treatment_variables}\nvariables={scenario.variables}"
        )

        assert len(expected_causal_effect) == 1, "We currently only support tests with one causal outcome"

        self.scenario = scenario
        self.intervention_constraints = intervention_constraints
        self.treatment_variables = treatment_variables
        self.expected_causal_effect = expected_causal_effect
        self.estimate_type = estimate_type

        if effect_modifiers is not None:
            self.effect_modifiers = effect_modifiers
        else:
            self.effect_modifiers = {}

    def __str__(self):
        outcome_string = " and ".join(
            [f"the effect on {var} should be {str(effect)}" for var, effect in self.expected_causal_effect.items()]
        )
        return f"When we apply intervention {self.intervention_constraints}, {outcome_string}"

    def datapath(self):
        def sanitise(string):
            return "".join([x for x in string if x.isalnum()])

        return (
            sanitise("-".join([str(c) for c in self.intervention_constraints]))
            + "_"
            + "-".join([f"{v.name}_{e}" for v, e in self.expected_causal_effect.items()])
            + ".csv"
        )

    def _generate_concrete_tests(
        self, sample_size: int, rct: bool = False, seed: int = 0
    ) -> tuple[list[CausalTestCase], pd.DataFrame]:
        """Generates a list of `num` concrete test cases.

        :param sample_size: The number of strata to use for Latin hypercube sampling. Where no target_ks_score is
        provided, this corresponds to the number of test cases to generate. Where target_ks_score is provided, the
        number of test cases will be a multiple of this.
        :param rct: Whether we're running an RCT, i.e. whether to add the treatment run to the concrete runs.
        :param seed: Random seed for reproducability.
        :return: A list of causal test cases and a dataframe representing the required model run configurations.
        :rtype: ([CausalTestCase], pd.DataFrame)
        """

        concrete_tests = []
        runs = []
        run_columns = sorted([v.name for v in self.scenario.variables.values() if v.distribution])

        # Generate the Latin Hypercube samples and put into a dataframe
        # lhsmdu.setRandomSeed(seed+i)
        samples = pd.DataFrame(
            lhsmdu.sample(len(run_columns), sample_size, randomSeed=seed).T,
            columns=run_columns,
        )
        # Project the samples to the variables' distributions
        for name in run_columns:
            var = self.scenario.variables[name]
            samples[var.name] = lhsmdu.inverseTransformSample(var.distribution, samples[var.name])

        for index, row in samples.iterrows():
            optimizer = z3.Optimize()
            for c in self.scenario.constraints:
                optimizer.assert_and_track(c, str(c))
            for c in self.intervention_constraints:
                optimizer.assert_and_track(c, str(c))

            optimizer.add_soft([self.scenario.variables[v].z3 == row[v] for v in run_columns])
            if optimizer.check() == z3.unsat:
                logger.warning(
                    "Satisfiability of test case was unsat.\n"
                    + f"Constraints\n{optimizer}\nUnsat core {optimizer.unsat_core()}"
                )
            model = optimizer.model()

            concrete_test = CausalTestCase(
                control_input_configuration={v: v.cast(model[v.z3]) for v in self.treatment_variables},
                treatment_input_configuration={
                    v: v.cast(model[self.scenario.treatment_variables[v.name].z3]) for v in self.treatment_variables
                },
                expected_causal_effect=list(self.expected_causal_effect.values())[0],
                outcome_variables=list(self.expected_causal_effect.keys()),
                estimate_type=self.estimate_type,
                effect_modifier_configuration={v: v.cast(model[v.z3]) for v in self.effect_modifiers},
            )

            for v in self.scenario.inputs():
                if row[v.name] != v.cast(model[v.z3]):
                    constraints = "\n  ".join([str(c) for c in self.scenario.constraints if v.name in str(c)])
                    logger.warning(
                        f"Unable to set variable {v.name} to {row[v.name]} because of constraints\n"
                        + f"{constraints}\nUsing value {v.cast(model[v.z3])} instead in test\n{concrete_test}"
                    )

            concrete_tests.append(concrete_test)
            # Control run
            control_run = {
                v.name: v.cast(model[v.z3]) for v in self.scenario.variables.values() if v.name in run_columns
            }
            control_run["bin"] = index
            runs.append(control_run)
            # Treatment run
            if rct:
                treatment_run = control_run.copy()
                treatment_run.update({k.name: v for k, v in concrete_test.treatment_input_configuration.items()})
                treatment_run["bin"] = index
                runs.append(treatment_run)

        return concrete_tests, pd.DataFrame(runs, columns=run_columns + ["bin"])

    def generate_concrete_tests(
        self, sample_size: int, target_ks_score: float = None, rct: bool = False, seed: int = 0, hard_max: int = 1000
    ) -> tuple[list[CausalTestCase], pd.DataFrame]:
        """Generates a list of `num` concrete test cases.

        :param sample_size: The number of strata to use for Latin hypercube sampling. Where no target_ks_score is
        provided, this corresponds to the number of test cases to generate. Where target_ks_score is provided, the
        number of test cases will be a multiple of this.
        :param target_ks_score: The target KS score. A value in range [0, 1] with lower values representing a higher
        confidence and requireing more tests to achieve. A value of 0.05 is recommended.
        TODO: Make this more flexible so we're not restricting ourselves just to the KS test.
        :param rct: Whether we're running an RCT, i.e. whether to add the treatment run to the concrete runs.
        :param seed: Random seed for reproducability.
        :param hard_max: Number of iterations to run for before timing out if target_ks_score cannot be reached.
        :return: A list of causal test cases and a dataframe representing the required model run configurations.
        :rtype: ([CausalTestCase], pd.DataFrame)
        """

        if target_ks_score is not None:
            assert 0 <= target_ks_score <= 1, "target_ks_score must be between 0 and 1."
        else:
            hard_max = 1

        concrete_tests = []
        runs = pd.DataFrame()
        ks_stats = []

        for i in range(hard_max):
            concrete_tests_, runs_ = self._generate_concrete_tests(sample_size, rct, seed + i)
            concrete_tests += concrete_tests_
            runs = pd.concat([runs, runs_])
            assert concrete_tests_ not in concrete_tests, "Duplicate entries unlikely unless something went wrong"

            control_configs = pd.DataFrame([test.control_input_configuration for test in concrete_tests])
            ks_stats = {
                var: stats.kstest(control_configs[var], var.distribution.cdf).statistic
                for var in control_configs.columns
            }
            # Putting treatment and control values in messes it up because the two are not independent...
            # This is potentially problematic as constraints might mean we don't get good coverage if we use control values alone
            # We might then need to carefully craft our _control value_ generating distributions so that we can get good coverage
            # without the generated treatment values violating any constraints.

            # treatment_configs = pd.DataFrame([test.treatment_input_configuration for test in concrete_tests])
            # both_configs = pd.concat([control_configs, treatment_configs])
            # ks_stats = {var: stats.kstest(both_configs[var], var.distribution.cdf).statistic for var in both_configs.columns}
            effect_modifier_configs = pd.DataFrame([test.effect_modifier_configuration for test in concrete_tests])
            ks_stats.update(
                {
                    var: stats.kstest(effect_modifier_configs[var], var.distribution.cdf).statistic
                    for var in effect_modifier_configs.columns
                }
            )
            if target_ks_score and all((stat <= target_ks_score for stat in ks_stats.values())):
                break

        if target_ks_score is not None and not all((stat <= target_ks_score for stat in ks_stats.values())):
            logger.error(
                "Hard max of %s reached but could not achieve target ks_score of %s. Got %s.",
                hard_max,
                target_ks_score,
                ks_stats,
            )
        return concrete_tests, runs
