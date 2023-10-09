import warnings

import numpy as np
import qiskit.quantum_info as qi
import random
import cmath
from qiskit import QuantumCircuit, Aer, execute
from qiskit.extensions import UnitaryGate
from sklearn.preprocessing import normalize

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.assert_equal import assert_equal_distributions, \
    measure_qubits
from dd_regression.helper_functions import get_circuit_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class EstimateExactPhase(PropertyBasedTestInterface):
    """create pool of all possible eigenvectors and eigenvalues from the unitary"""
    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        """"set up simultaneous equation, unitary * eigenvector = eigenvalue * eigenvector 
            choose a non-zero element in eigenvector, compare it to same element in multiplied, rearrange for eigenvalue"""
        print(circuit.draw(vertical_compression='high', fold=300))
        unitary_matrix = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, np.cos(5 * np.pi / 8) - np.sin(5 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, np.cos(6 * np.pi / 8) - np.sin(6 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, np.cos(np.pi / 4) - np.sin(np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, np.cos(3 * np.pi / 8) - np.sin(3 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * np.pi / 8) - np.sin(2 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(np.pi / 8) - np.sin(np.pi / 8) * 1j, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(np.pi / 8) + np.sin(np.pi / 8) * 1j, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2) - 1j / np.sqrt(2), 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(7 * np.pi / 8) + np.sin(7 * np.pi / 8) * 1j]
        ]

        unitary_gate = UnitaryGate(unitary_matrix)

        eigenvalues, eigenvectors = np.linalg.eig(qi.Operator(unitary_gate))

        experiments = []

        for i in range(inputs_to_generate):
            random_index = random.randint(0, len(eigenvalues)-1)
            random_eigenvalue = eigenvalues[random_index]
            random_eigenvector = eigenvectors[:, random_index]

            print(random_eigenvalue)
            print(random_eigenvector)

            theta = cmath.phase(random_eigenvalue) / (2 * cmath.pi)

            # Ensure that theta is within the range [0, 1)
            theta = (theta + 1) % 1
            print(f"theta {theta}")

            expected_binary = bin(int(theta * 16))[2:].zfill(4)
            print(f"expected binary {expected_binary}")

            s1 = qi.Statevector(random_eigenvector)

            # initialize to random state and append the applied delta modified circuit
            qlength, clength = get_circuit_register(circuit)
            init_state = QuantumCircuit(qlength)
            init_state.initialize(s1, [4, 5, 6, 7])
            inputted_circuit_to_test = init_state.compose(circuit)

            measurements_1 = measure_qubits(inputted_circuit_to_test, [0, 1, 2, 3], basis=['z'], measurements=measurements)

            result = ""
            for res_dict in measurements_1:
                if res_dict.get("z0") == measurements:
                    result += "0"
                elif res_dict.get("z1") == measurements:
                    result += "1"

            print(measurements_1)
            print(f"result {result}")

            if result == expected_binary:
                p_value = 1
            else:
                p_value = 0

            experiments.append([i, random_eigenvector, (p_value,), (measurements_1, [])])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               extra_info=None, measurements=500):
        qlength, clength = get_circuit_register(original_failing_circuit)
        init_state = QuantumCircuit(qlength)

        init_state.initialize(input_state_list, [4, 5, 6, 7])
        inputted_circuit_to_test = init_state.compose(list_to_circuit(original_failing_circuit))

        measurements_1 = measure_qubits(inputted_circuit_to_test, [0, 1, 2, 3], basis=['z'], measurements=measurements)

        print("verif")
        print(measurements_1)
        print(output_distribution)

        # not quite perfect here, should be checking all basis for the qubits, but only checking z
        # make sure we are unpacking all p values from assert equal
        p_value_0, p_value_1, p_value_2, p_value_3 = assert_equal_distributions(measurements_1, output_distribution,
                                                                                basis=['z'])

        print(p_value_0)
        print(p_value_1)
        print(p_value_2)
        print(p_value_3)

        return [property_idx, exp_idx, (p_value_0, p_value_1, p_value_2, p_value_3)]
