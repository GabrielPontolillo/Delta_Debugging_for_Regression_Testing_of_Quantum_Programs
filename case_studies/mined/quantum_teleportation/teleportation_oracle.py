import warnings
from abc import abstractmethod

import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.quantum_info import random_statevector

from case_studies.property_based_test_oracle_interface import PropertyBasedTestOracleInterface
from case_studies.mined.quantum_teleportation.equal_output_property import EqualOutputProperty

from dd_regression.assertions.assert_equal import assert_equal, assert_equal_state, holm_bonferroni_correction, measure_qubits
from dd_regression.helper_functions import circuit_to_list, list_to_circuit, get_quantum_register, add_random_chaff
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.diff_algorithm_r import Addition, Removal, diff, apply_diffs, Experiment

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class TeleportationOracle(PropertyBasedTestOracleInterface):
    @staticmethod
    def test_oracle(passing_circuit, failing_circuit, deltas, property_classes, inputs_to_generate=25,
                    measurements=1000):
        print("going to apply diffs to make circuit")
        print(property_classes)
        # create quantum circuit by applying diffs to the passing circuit
        changed_circuit_list = apply_diffs(passing_circuit, failing_circuit, deltas)
        changed_circuit = list_to_circuit(changed_circuit_list)

        composed_results = []

        # call the property_based_test method on each property class using the new circuit
        for property_class in property_classes:
            # calling each property based test
            property_test_results = property_class.property_based_test(changed_circuit)

            composed_results.append(property_test_results)



        # failing_indexes - a list of lists of failing p-value indexes, matches with property classes
        failing_indexes = []

