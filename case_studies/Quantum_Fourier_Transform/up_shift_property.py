import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer
import random
from qiskit.extensions import UnitaryGate
from qiskit.quantum_info import random_statevector, Statevector, Operator

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.assert_equal import assert_equal, assert_equal_state, measure_qubits, \
    assert_equal_distributions, assert_equal_distributions_chi
from dd_regression.helper_functions import get_circuit_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class UpShiftProperty(PropertyBasedTestInterface):
    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        # print("inside equal output property based test call")
        log = False
        experiments = []

        for i in range(inputs_to_generate):
            unitary_matrix = [
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, ((1 / np.sqrt(2)) + (1j / np.sqrt(2))), 1j, ((-1 / np.sqrt(2)) + (1j / np.sqrt(2))), -1,
                 ((-1 / np.sqrt(2)) + (-1j / np.sqrt(2))), -1j, ((1 / np.sqrt(2)) + (-1j / np.sqrt(2)))],
                [1, 1j, -1, -1j, 1, 1j, -1, -1j],
                [1, ((-1 / np.sqrt(2)) + (1j / np.sqrt(2))), -1j, ((1 / np.sqrt(2)) + (1j / np.sqrt(2))), -1,
                 ((1 / np.sqrt(2)) + (-1j / np.sqrt(2))), 1j, ((-1 / np.sqrt(2)) + (-1j / np.sqrt(2)))],
                [1, -1, 1, -1, 1, -1, 1, -1],
                [1, ((-1 / np.sqrt(2)) + (-1j / np.sqrt(2))), 1j, ((1 / np.sqrt(2)) + (-1j / np.sqrt(2))), -1,
                 ((1 / np.sqrt(2)) + (1j / np.sqrt(2))), -1j, ((-1 / np.sqrt(2)) + (1j / np.sqrt(2)))],
                [1, -1j, -1, 1j, 1, -1j, -1, 1j],
                [1, ((1 / np.sqrt(2)) + (-1j / np.sqrt(2))), -1j, ((-1 / np.sqrt(2)) + (-1j / np.sqrt(2))), -1,
                 ((-1 / np.sqrt(2)) + (1j / np.sqrt(2))), 1j, ((1 / np.sqrt(2)) + (1j / np.sqrt(2)))],
            ]

            unitary_matrix = 1 / np.sqrt(8) * np.array(unitary_matrix)

            # initialize to random state and append the applied delta modified circuit
            qlength, clength = get_circuit_register(circuit)

            init_int = random.randint(0, 7)
            init_vect = unitary_matrix[init_int]

            if log:
                print(init_int)
                print(init_vect)

            init_state_circuit = QuantumCircuit(qlength)
            init_state_circuit.initialize(init_vect, [0, 1, 2])
            inputted_circuit_to_test = init_state_circuit.compose(circuit.inverse())

            phase_shift_circuit = QuantumCircuit(qlength)
            phase_shift_circuit.initialize(init_vect, [0, 1, 2])
            shifted_circuit_to_test = UpShiftProperty.phase_shift(phase_shift_circuit)
            shifted_circuit_to_test = shifted_circuit_to_test.compose(circuit.inverse())

            if log:
                print(inputted_circuit_to_test.draw(vertical_compression='high', fold=300))
                print(shifted_circuit_to_test.draw(vertical_compression='high', fold=300))

            base_measurements = measure_qubits(inputted_circuit_to_test, [0, 1, 2], measurements=measurements)
            shifted_measurements = measure_qubits(shifted_circuit_to_test, [0, 1, 2], measurements=measurements)

            if log:
                print(init_int)
                print(base_measurements)

            UpShiftProperty.up_shift(base_measurements, init_int)

            if log:
                print(base_measurements)
                print(shifted_measurements)

            # compare the output of the merged circuit to test, with an empty circuit initialised to expected state
            p_val = assert_equal_distributions(base_measurements, shifted_measurements)

            if log:
                print(p_val)

            print(p_val)

            # add a tuple of 3 elements index, initialised vector, p values, measurements
            experiments.append([i, init_vect, [i for i in p_val],
                                (base_measurements, shifted_measurements), init_int])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               extra_info=None, measurements=1000):
        # print("verification heuristic")

        qlength, clength = get_circuit_register(original_failing_circuit)
        init_state = QuantumCircuit(qlength)

        init_state.initialize(input_state_list, [0, 1, 2])
        inputted_circuit_to_test = init_state.compose(list_to_circuit(original_failing_circuit).inverse())

        init_int = extra_info[0]
        # print(init_int)

        # print(inputted_circuit_to_test)

        base_measurements = measure_qubits(inputted_circuit_to_test, [0, 1, 2], measurements=measurements)
        UpShiftProperty.up_shift(base_measurements, init_int)

        # print(measurements_1)
        # print(output_distribution)

        p_val = assert_equal_distributions(base_measurements, output_distribution)

        print(p_val)

        return [property_idx, exp_idx,
                [i for i in p_val]]

    @staticmethod
    def phase_shift(qc):
        qc.p(-np.pi / 4, 0)
        qc.p(-np.pi / 2, 1)
        qc.p(-np.pi / 1, 2)
        return qc

    @staticmethod
    # This could also be done through adding a circuit that subtracts the binary number by one (flipping 111 to 000)
    def up_shift(measurements, init_int):
        if init_int % 2 == 1:
            ## NNF
            UpShiftProperty._swap_z(measurements[2])
        if init_int % 4 == 0:
            ## FFF
            UpShiftProperty._swap_z(measurements[0])
            UpShiftProperty._swap_z(measurements[1])
            UpShiftProperty._swap_z(measurements[2])
        if init_int % 4 == 2:
            ## NFF
            UpShiftProperty._swap_z(measurements[1])
            UpShiftProperty._swap_z(measurements[2])


    @staticmethod
    def _swap_z(dict):
        temp = dict['z0']
        dict['z0'] = dict['z1']
        dict['z1'] = temp
