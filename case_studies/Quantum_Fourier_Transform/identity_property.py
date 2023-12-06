import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer
import random
from qiskit.extensions import UnitaryGate
from qiskit.quantum_info import random_statevector, Statevector, Operator, random_unitary

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.statistical_analysis import assert_equal, assert_equal_state, measure_qubits, \
    assert_equal_distributions, assert_equal_distributions_chi
from dd_regression.helper_functions import get_circuit_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class IdentityProperty(PropertyBasedTestInterface):
    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        # print("inside equal output property based test call")
        log = False
        experiments = []

        for i in range(inputs_to_generate):
            qlength, clength = get_circuit_register(circuit)

            operator = random_unitary(8)

            id_circuit = QuantumCircuit(qlength)
            id_circuit = id_circuit.compose(circuit)
            for num in range(len(qlength)):
                id_circuit.h(num)
            id_circuit.unitary(operator, [0, 1, 2])

            only_unitary = QuantumCircuit(qlength)
            only_unitary.unitary(operator, [0, 1, 2])

            if log:
                print(id_circuit.draw(vertical_compression='high', fold=300))
                print(only_unitary.draw(vertical_compression='high', fold=300))

            base_measurements = measure_qubits(id_circuit, [0, 1, 2], measurements=measurements)
            only_unitary_measurements = measure_qubits(only_unitary, [0, 1, 2], measurements=measurements)

            if log:
                print(base_measurements)
                print(only_unitary_measurements)

            # compare the output of the merged circuit to test, with an empty circuit initialised to expected state
            # p_list = assert_equal_distributions(base_measurements, only_unitary_measurements)
            p_val = assert_equal_distributions(base_measurements, only_unitary_measurements)

            if log:
                print(p_val)

            # add a tuple of 3 elements index, initialised vector, p values, measurements
            # experiments.append([i, [1, 0, 0, 0, 0, 0, 0, 0], (
            #     p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5], p_list[6], p_list[7], p_list[8]),
            #                     (base_measurements, only_unitary_measurements), operator])

            experiments.append([i, [1, 0, 0, 0, 0, 0, 0, 0], [i for i in p_val], (base_measurements, only_unitary_measurements), operator])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               extra_info=None, measurements=1000):
        # print("verification heuristic")

        qlength, clength = get_circuit_register(original_failing_circuit)

        id_circuit = QuantumCircuit(qlength)
        id_circuit = id_circuit.compose(list_to_circuit(original_failing_circuit))
        for num in range(len(qlength)):
            id_circuit.h(num)
        id_circuit.unitary(extra_info[0], [0, 1, 2])

        # print(inputted_circuit_to_test)

        base_measurements = measure_qubits(id_circuit, [0, 1, 2], measurements=measurements)

        # print(base_measurements)
        # print(output_distribution)

        p_val = assert_equal_distributions(base_measurements, output_distribution)

        return [property_idx, exp_idx, [i for i in p_val]]
