import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer
import random
from qiskit.extensions import UnitaryGate
from qiskit.quantum_info import random_statevector, Statevector, Operator

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.statistical_analysis import assert_equal, assert_equal_state, measure_qubits, \
    assert_equal_distributions
from dd_regression.helper_functions import get_circuit_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class PhaseShiftProperty(PropertyBasedTestInterface):
    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        # print("inside equal output property based test call")
        log = False
        experiments = []

        for i in range(inputs_to_generate):
            # initialize to random state and append the applied delta modified circuit
            qlength, clength = get_circuit_register(circuit)
            init_int = random.randint(0, 7)
            # print(init_int)
            init_vect = np.zeros(8)
            init_vect[init_int] = 1
            shifted_vector = [init_vect[1], init_vect[2], init_vect[3], init_vect[4], init_vect[5], init_vect[6],
                              init_vect[7], init_vect[0]]

            init_state_circuit = QuantumCircuit(qlength)
            init_state_circuit.initialize(init_vect, [2, 1, 0])
            inputted_circuit_to_test = init_state_circuit.compose(circuit)
            phase_shifted_circuit_to_test = PhaseShiftProperty.phase_shift(inputted_circuit_to_test)

            up_shifted_circuit = QuantumCircuit(qlength)
            up_shifted_circuit.initialize(shifted_vector, [2, 1, 0])
            up_shifted_circuit_to_test = up_shifted_circuit.compose(circuit)

            if log:
                print(phase_shifted_circuit_to_test.draw(vertical_compression='high', fold=300))
                print(up_shifted_circuit_to_test.draw(vertical_compression='high', fold=300))

            phase_shifted_measurements = measure_qubits(phase_shifted_circuit_to_test, [0, 1, 2], measurements=measurements)
            up_shifted_measurements = measure_qubits(up_shifted_circuit_to_test, [0, 1, 2], measurements=measurements)

            if log:
                print(phase_shifted_measurements)
                print(up_shifted_measurements)

            # compare the output of the merged circuit to test, with an empty circuit initialised to expected state
            p_list = assert_equal_distributions(phase_shifted_measurements, up_shifted_measurements)
            if log:
                print(p_list)

            # add a tuple of 3 elements index, initialised vector, p values, measurements
            experiments.append([i, init_vect, (p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5], p_list[6], p_list[7], p_list[8]),
                                (phase_shifted_measurements, up_shifted_measurements)])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               extra_info=None, measurements=1000):
        log = False
        if log:
            print("verification heuristic")

        qlength, clength = get_circuit_register(original_failing_circuit)
        init_state = QuantumCircuit(qlength)

        init_state.initialize(input_state_list, [2, 1, 0])
        inputted_circuit_to_test = init_state.compose(list_to_circuit(original_failing_circuit))
        inputted_circuit_to_test = PhaseShiftProperty.phase_shift(inputted_circuit_to_test)

        if log:
            print(inputted_circuit_to_test)

        measurements_1 = measure_qubits(inputted_circuit_to_test, [0, 1, 2], measurements=measurements)

        if log:
            print(measurements_1)
            print(output_distribution)

        p_list = assert_equal_distributions(measurements_1, output_distribution)

        return [property_idx, exp_idx, (p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5], p_list[6], p_list[7], p_list[8])]

    @staticmethod
    def phase_shift(qc):
        qc.p(-np.pi/4, 0)
        qc.p(-np.pi/2, 1)
        qc.p(-np.pi/1, 2)
        return qc
