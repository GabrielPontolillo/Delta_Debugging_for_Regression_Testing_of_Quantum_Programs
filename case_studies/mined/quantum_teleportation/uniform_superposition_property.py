import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer
from qiskit.quantum_info import random_statevector

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.assert_equal import assert_equal_distributions, \
    measure_qubits
from dd_regression.helper_functions import get_quantum_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class UniformSuperpositionProperty(PropertyBasedTestInterface):
    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        experiments = []

        for i in range(inputs_to_generate):
            # initialize to random state and append the applied delta modified circuit
            qlength, clength = get_quantum_register(circuit)
            init_state = QuantumCircuit(qlength)
            init_vector = random_statevector(2)
            init_state.initialize(init_vector, 0)
            inputted_circuit_to_test = init_state.compose(circuit)

            # create a new circuit with just state initialization to compare with
            qc = QuantumCircuit(2, 2)
            bell_state = (1 / 2) * np.array([1, 1, 1, 1])
            qc.initialize(bell_state, [0, 1])

            # probably do all measurements, and get only the z for this test
            measurements_1 = measure_qubits(inputted_circuit_to_test, [0, 1], basis=['z'])
            measurements_2 = measure_qubits(qc, [0, 1], basis=['z'])

            # print(measurements_1)
            # print(measurements_2)
            # compare the output of the merged circuit to test, with an empty circuit initialised to expected state
            p_list = assert_equal_distributions(measurements_1, measurements_2, basis=['z'])

            # print(p_list)

            # add a tuple of 3 elements index, initialised vector, p values, measurements
            experiments.append([i, init_vector, (p_list[0], p_list[1]), (measurements_1, measurements_2)])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               extra_info=None, measurements=1000):
        qlength, clength = get_quantum_register(original_failing_circuit)
        init_state = QuantumCircuit(qlength)

        # print(input_state_list)

        init_state.initialize(input_state_list, 0)
        inputted_circuit_to_test = init_state + list_to_circuit(original_failing_circuit)

        measurements_1 = measure_qubits(inputted_circuit_to_test, [0, 1], basis=['z'])

        # print(measurements_1)
        # print(output_distribution)

        # not quite perfect here, should be checking all basis for the qubits, but only checking z
        p_value_0, p_value_1 = assert_equal_distributions(measurements_1, output_distribution, basis=['z'])

        return [property_idx, exp_idx, (p_value_0, p_value_1)]
