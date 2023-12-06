import warnings

import copy
import numpy as np
import qiskit.quantum_info as qi
import random
from qiskit import QuantumCircuit, Aer
from qiskit.extensions import UnitaryGate

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.statistical_analysis import assert_equal_distributions, \
    measure_qubits
from dd_regression.helper_functions import get_circuit_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class AddEigenvectorsSameEigenvalueProperty(PropertyBasedTestInterface):
    """create pool of all possible eigenvectors and eigenvalues from the unitary"""

    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        """"set up simultaneous equation, unitary * eigenvector = eigenvalue * eigenvector 
            choose a non-zero element in eigenvector, compare it to same element in multiplied, rearrange for eigenvalue"""
        estimation_qubits = 2
        unitary_qubits = 3
        eigenvector_eigenvalue_dict = dict()

        unitary_matrix = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0],
            [0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0],
            [0, 0, 0, 0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j],
        ]

        unitary_gate = UnitaryGate(unitary_matrix)

        eigenvalues, eigenvectors = np.linalg.eig(qi.Operator(unitary_gate))

        for i in range(len(eigenvalues)):
            eigenvalue = eigenvalues[i].round()
            eigenvector = eigenvectors[:, i]

            # Check if the eigenvalue is already in the dictionary
            if eigenvalue in eigenvector_eigenvalue_dict:
                eigenvector_eigenvalue_dict[eigenvalue].append(eigenvector)
            else:
                eigenvector_eigenvalue_dict[eigenvalue] = [eigenvector]

        filtered_dict = {key: value for key, value in eigenvector_eigenvalue_dict.items() if
                         len(value) >= 2 and value != 0 and value != 0j}

        experiments = []

        for i in range(inputs_to_generate):
            filtered_dict_c = copy.deepcopy(filtered_dict)
            random_eigenvalue = random.choice(list(filtered_dict_c.keys()))
            random_index = random.randint(0, len(filtered_dict_c[random_eigenvalue]) - 1)
            random_eigenvector = filtered_dict_c[random_eigenvalue][random_index]
            # print(f"1 {filtered_dict_c} i {i}")
            filtered_dict_c[random_eigenvalue].pop(random_index)
            # print(f"2 {filtered_dict_c} i {i}")
            random_eigenvector2 = random.choice(filtered_dict_c[random_eigenvalue])
            # random_eigenvector2 = eigenvectors[0]
            added_eigenvector = np.add(random_eigenvector, random_eigenvector2)
            normalized_eigenvector = added_eigenvector * (1 / np.sqrt(2))

            s1 = qi.Statevector(random_eigenvector)
            s2 = qi.Statevector(normalized_eigenvector)

            # initialize to random state and append the applied delta modified circuit
            qlength, clength = get_circuit_register(circuit)
            init_state = QuantumCircuit(qlength)
            init_state.initialize(s1, [i+estimation_qubits for i in range(unitary_qubits)])
            inputted_circuit_to_test = init_state.compose(circuit)
            # print(inputted_circuit_to_test.draw(vertical_compression='high', fold=300))

            # create a new circuit with just state initialization to compare with
            init_state2 = QuantumCircuit(qlength)
            init_state2.initialize(s2, [i+estimation_qubits for i in range(unitary_qubits)])
            inputted_circuit_to_test2 = init_state2.compose(circuit.copy())
            # print(inputted_circuit_to_test2.draw(vertical_compression='high', fold=300))

            # probably do all measurements, and get only the z for this test
            measurements_1 = measure_qubits(inputted_circuit_to_test, [i for i in range(estimation_qubits)], measurements=measurements)
            measurements_2 = measure_qubits(inputted_circuit_to_test2, [i for i in range(estimation_qubits)], measurements=measurements)

            # print(measurements_1)
            # print(measurements_2)
            # compare the output of the merged circuit to test, with an empty circuit initialised to expected state
            p_list = assert_equal_distributions(measurements_1, measurements_2)

            # print(p_list)

            # add a tuple of 3 elements index, initialised vector, p values, measurements
            # make sure we pass all p_values
            experiments.append([i, random_eigenvector, (
            p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5]),
                                (measurements_1, measurements_2)])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               extra_info=None, measurements=500):
        qlength, clength = get_circuit_register(original_failing_circuit)
        init_state = QuantumCircuit(qlength)
        estimation_qubits = 2
        unitary_qubits = 3

        init_state.initialize(input_state_list, [i+estimation_qubits for i in range(unitary_qubits)])
        inputted_circuit_to_test = init_state.compose(list_to_circuit(original_failing_circuit))

        measurements_1 = measure_qubits(inputted_circuit_to_test, [i for i in range(estimation_qubits)], measurements=measurements)

        # print("verif")
        # print(measurements_1)
        # print(output_distribution)

        # not quite perfect here, should be checking all basis for the qubits, but only checking z
        # make sure we are unpacking all p values from assert equal
        p_list = assert_equal_distributions(measurements_1, output_distribution)

        return [property_idx, exp_idx,
                (p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5])]
