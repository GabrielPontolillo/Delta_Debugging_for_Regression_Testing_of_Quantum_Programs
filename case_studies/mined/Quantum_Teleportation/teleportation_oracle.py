import warnings
from time import perf_counter as pc

from qiskit import Aer

from case_studies.property_based_test_oracle_interface import PropertyBasedTestOracleInterface
from dd_regression.assertions.assert_equal import holm_bonferroni_correction
from dd_regression.diff_algorithm import apply_diffs
from dd_regression.helper_functions import list_to_circuit
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class TeleportationOracle(PropertyBasedTestOracleInterface):
    @staticmethod
    def test_oracle(passing_circuit, failing_circuit, deltas, property_classes, measurements, significance_level,
                    inputs_to_generate=25):
        # create quantum circuit by applying diffs to the passing circuit
        changed_circuit_list = apply_diffs(passing_circuit, deltas)
        changed_circuit = list_to_circuit(changed_circuit_list)

        composed_results = []
        p_value_index_pairs = []

        t0 = pc()
        # call the property_based_test method on each property class using the new circuit
        for i, property_class in enumerate(property_classes):
            # calling each property based test
            property_test_results = property_class.property_based_test(changed_circuit,
                                                                       inputs_to_generate=inputs_to_generate,
                                                                       measurements=measurements)
            composed_results.append(property_test_results)

            # place results in a list that links index of experiment, and property that the property it comes from
            for idx_experiment, experiment in enumerate(property_test_results):
                for p_value in experiment[2]:
                    p_value_index_pairs.append((i, experiment[0], p_value))

        # print("verification_p_value_index_pairs")
        # print(p_value_index_pairs)

        # using the list of pvalues, and indexes, apply holm bonferroni correction
        failed_indexes = holm_bonferroni_correction(p_value_index_pairs, significance_level)

        # print("failed_indexes")
        # print(failed_indexes)

        # print(composed_results)

        # print(f"original check {pc() - t0}")
        t0 = pc()

        verification_p_value_index_pairs = []

        for prop_idx, exp_idx in failed_indexes:
            # print(prop_idx)
            # print(exp_idx)
            # print(composed_results[prop_idx][exp_idx][3][0])
            composed_results[prop_idx][exp_idx][0]

            # this is original property only returns index, intial value, p values and measurements
            if len(composed_results[prop_idx][exp_idx]) == 4:
                # requires the failing circuit, the previous measurements, and state to initialise
                verification_result = property_classes[prop_idx].verification_heuristic(prop_idx, exp_idx,
                                                                                        failing_circuit,
                                                                                        composed_results[
                                                                                            prop_idx][
                                                                                            exp_idx][3][0],
                                                                                        composed_results[
                                                                                            prop_idx][
                                                                                            exp_idx][1],
                                                                                        measurements=measurements)
            # this is if the original property test returns an extra value, then pass that to verification
            else:
                verification_result = property_classes[prop_idx].verification_heuristic(prop_idx, exp_idx,
                                                                                        failing_circuit,
                                                                                        composed_results[
                                                                                            prop_idx][
                                                                                            exp_idx][3][0],
                                                                                        composed_results[
                                                                                            prop_idx][
                                                                                            exp_idx][1],
                                                                                        extra_info=composed_results[prop_idx][
                                                                                            exp_idx][4:],
                                                                                        measurements=measurements)
            # print("verification result")
            # print(verification_result)
            for p_value in verification_result[2]:
                verification_p_value_index_pairs.append((verification_result[0], verification_result[1], p_value))

        # print("verification_p_value_index_pairs")
        # print(verification_p_value_index_pairs)

        # using the list of pvalues, and indexes, apply holm bonferroni correction
        verification_failed_indexes = holm_bonferroni_correction(verification_p_value_index_pairs, significance_level)

        # print(f"verif time new {pc() - t0}")
        # print("verification failed indexes")
        # print(verification_failed_indexes)

        # print("failed indexes")
        # print(failed_indexes)

        # if any state not equal, inconclusive result
        if len(verification_failed_indexes) > 0:
            return Inconclusive()
        elif len(failed_indexes) > 0:
            return Failed()
        else:
            return Passed()
